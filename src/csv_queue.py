"""Persist each queue transition immediately using GitHub's conditional Contents API."""
import base64
import csv
import io
import json
import os
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from .config import required

HEADERS = ['Name','Status','YouTube URL','Uploaded Date','Job ID','Updated At','Error']
OPTIONAL = ['Type','Duration Seconds','Style']

class QueueConflict(RuntimeError):
    pass

class CsvQueue:
    def __init__(self):
        self.path = Path(os.getenv('QUEUE_FILE','names-template.csv'))
        self.token = os.getenv('GITHUB_TOKEN','')
        self.sha = None
        if self.token:
            repo=required('GITHUB_REPOSITORY')
            self.branch=required('GITHUB_QUEUE_BRANCH')
            self.url=f'https://api.github.com/repos/{quote(repo,safe="/")}/contents/{quote(self.path.as_posix(),safe="/")}'
            data=self.request('GET')
            self.sha=data['sha']
            text=base64.b64decode(data['content']).decode('utf-8-sig')
        else:
            if os.getenv('GITHUB_ACTIONS') == 'true':
                raise ValueError('Missing GITHUB_TOKEN: refusing ephemeral queue writes in Actions')
            text=self.path.read_text(encoding='utf-8-sig')
        self.original=text
        self.data=list(csv.reader(io.StringIO(text)))
        if not self.data or self.data[0][:7] != HEADERS or self.data[0][7:] != OPTIONAL[:len(self.data[0])-7] or len(self.data[0]) not in (7,8,9,10):
            raise ValueError('CSV headers must match names-template.csv')
        width=len(self.data[0])
        if any(len(row)>width for row in self.data[1:]):
            raise ValueError('CSV row has too many columns')
        self.data=[self.data[0]]+[(row+['']*width)[:width] for row in self.data[1:]]

    def request(self, method, payload=None):
        url=self.url + ('?ref='+quote(self.branch,safe='') if method=='GET' else '')
        headers={'Authorization':f'Bearer {self.token}','Accept':'application/vnd.github+json',
                 'X-GitHub-Api-Version':'2022-11-28','User-Agent':'EnjoyYourDayStudio'}
        body=None if payload is None else json.dumps(payload).encode()
        if body: headers['Content-Type']='application/json'
        try:
            with urlopen(Request(url,data=body,headers=headers,method=method),timeout=60) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code in (409,422):
                raise QueueConflict('CSV changed or branch disallows writes; inspect repository before retrying') from None
            raise RuntimeError(f'GitHub queue request failed (HTTP {exc.code})') from None

    def rows(self):
        return [(i,list(row)) for i,row in enumerate(self.data[1:],2) if row[0].strip()]

    def write(self, number, row):
        data=[list(r) for r in self.data]
        data[number-1][:7]=row[:7]
        output=io.StringIO(newline='')
        csv.writer(output,lineterminator='\n').writerows(data)
        text=output.getvalue()
        if self.token:
            result=self.request('PUT',{'message':f'Update video queue row {number}: {row[1]}',
                'content':base64.b64encode(text.encode()).decode(),'sha':self.sha,'branch':self.branch})
            self.sha=result['content']['sha']
        else:
            if self.path.read_text(encoding='utf-8-sig') != self.original:
                raise QueueConflict('Local CSV changed during processing')
            temporary=self.path.with_suffix('.csv.tmp')
            temporary.write_text(text,encoding='utf-8');temporary.replace(self.path)
        self.original=text
        self.data=data
