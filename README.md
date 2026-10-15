# Enjoy Your Day Studio — GitHub CSV edition

Celebrate. Relax. Enjoy Your Day.

Edit names-template.csv on GitHub → workflow generates video and thumbnail → uploads to your YouTube channel → commits status and URL to the CSV. No Google Sheet or Google Sheets API is used.

## 1. Replace files in GitHub

Upload this project's CONTENTS to your repository root, including `.github/workflows/birthday-upload.yml`. Keep your existing queue data: do not overwrite completed rows with the supplied sample CSV. Remove the old `src/sheet.py` file if it remains in your repository; it is no longer used. Use only this workflow against the queue.

## 2. Edit names-template.csv

The exact columns are:

Name,Status,YouTube URL,Uploaded Date,Job ID,Updated At,Error,Type,Duration Seconds,Style

The first seven columns are required; Type, Duration Seconds and Style are optional for legacy birthday-only CSVs. Leave automated columns C–G empty for new requests.

```csv
Name,Status,YouTube URL,Uploaded Date,Job ID,Updated At,Error,Type,Duration Seconds,Style
Amit,Pending,,,,,,birthday,,
Gentle Rain,Pending,,,,,,rain,60,
Peaceful Moments,Pending,,,,,,music,60,
cat,Pending,,,,,,animal,30,cartoon
dog,Pending,,,,,,animal,30,pastel
```

Open the file on GitHub → pencil icon (Edit) → append a row → Commit changes to the default branch. Do not remove completed rows. Do not edit the queue while a run is processing it. If you do, conditional writes protect your edits, but the workflow will stop and may require recovery.

Birthday: short vertical video with English female narration. Rain/music: landscape illustrated animation, no narration; 10–600 seconds (default 60). Rain is digitally synthesized noise, not a natural field recording. Music is a simple original procedural instrumental, not a full AI song generator. Public repositories expose queue names and video links; use a private repository if desired.

## 3. Enable the remaining Google APIs

Create/select your project at https://console.cloud.google.com/ and enable:

- YouTube Data API v3 for uploading.
- Cloud Text-to-Speech API for female birthday narration (billing may be required).

Google Sheets API is NOT required. You can ignore the previous Sheet setup and sharing steps.

Create a Google service account with permission to use Text-to-Speech in the project and download its JSON key. This key is only for narration. Rain/music runs do not load it. Never commit credentials. GitHub Actions and speech synthesis may incur usage charges.

## 4. Authorize YouTube once

Configure Google Auth Platform / OAuth consent. Choose External if needed; add your own Google account as a test user. Create an OAuth client of type Desktop app; download its JSON.

A one-time authorization needs a browser on your own computer; the hourly jobs run entirely on GitHub afterward. On Windows 11, install Python 3.12, then run these commands from the project folder:

```powershell
py -m pip install -r requirements.txt
py scripts/authorize_youtube.py client_secret.json
```

Replace `client_secret.json` with the downloaded filename. Sign in and select the actual Enjoy Your Day Studio channel (including the correct Brand Account if applicable). The script prints the channel name and saves credentials in `youtube-token.json`. It never prints the refresh token.

For unattended operation, move the OAuth app from Testing to Production when appropriate and reauthorize. External apps in Testing generally have seven-day refresh tokens for these scopes. Production status is separate from OAuth verification and YouTube's API compliance audit. Tokens can still expire or be revoked; if authentication fails, authorize again and replace the secret.


## 5. Add GitHub Secrets and Variables

Settings → Secrets and variables → Actions → Secrets:

| Secret | Value |
|---|---|
| GOOGLE_SERVICE_ACCOUNT_JSON | Complete service-account JSON, birthday voice only |
| YOUTUBE_CLIENT_ID | From the authorization JSON |
| YOUTUBE_CLIENT_SECRET | From the authorization JSON |
| YOUTUBE_REFRESH_TOKEN | From the authorization JSON |
| YOUTUBE_CHANNEL_ID | From the authorization JSON |

GOOGLE_SHEET_ID is not needed; delete it if you wish. Do not add a personal GitHub access token. GitHub automatically provides the workflow's temporary GITHUB_TOKEN.

Variables:

| Variable | Value |
|---|---|
| UPLOADS_ENABLED | false initially, then true |
| YOUTUBE_PRIVACY | private initially; public when ready |
| MADE_FOR_KIDS | true or false according to your actual intended audience |

Under Settings → Actions → General → Workflow permissions, allow Read and write permissions if your repository allows it. The workflow declares contents: write to update the CSV. Organization policies or branch protection may block direct commits; this workflow requires bot commits to the default branch. If blocked, use a repository where this permission is allowed. The program refuses to upload until it can persist the Processing and Uploading states.

## 6. Preview and activate

Actions → Enjoy Your Day Studio videos → Run workflow → leave preview checked. Download MP4/JPG preview artifacts from the finished run. Preview reads the CSV but does not modify it or upload to YouTube. Birthday preview still uses Text-to-Speech.

Then set UPLOADS_ENABLED=true and manually run with preview unchecked. Confirm private video URLs appear in the repository's CSV. The file visible in the workflow checkout may be older: refresh the CSV on GitHub to see API commits.

The workflow also runs on user commits to names-template.csv and hourly at minute 17, on the default branch only. Its own status commits use GITHUB_TOKEN, so they do not trigger a workflow loop. Scheduled jobs can be delayed and public repository schedules may be disabled after 60 days of inactivity. Maximum three new videos and three thumbnail retries per run. You can edit MAX_PER_RUN in the workflow (1–10).

YouTube may restrict public uploads or Shorts thumbnails based on API project/channel eligibility. Test with your actual account. Setting public does not override YouTube restrictions. This code does not update your channel profile, banner, description or playlists; apply the supplied branding images in YouTube Studio yourself.

## Recovery

Every Processing, Uploading, Uploaded and thumbnail transition is committed immediately to GitHub through the Contents API with a file SHA guard. No end-of-job push is needed. A crash cannot rely on the runner's local disk as durable state.

- Pending or blank: eligible.
- Processing: generation started; after a killed run, inspect before resetting to Pending.
- Uploading / Needs Review: outcome uncertain. Check YouTube Studio and match the description's Reference job ID to column E. If found, save the URL and mark Uploaded. Do not reset blindly.
- Uploaded: skipped; keeps the YouTube URL.
- Error: fix generation, billing, credentials or input, then set Pending.
- Uploaded with Error starting Thumbnail pending:: retry only the thumbnail. Never reset this video to Pending. Clear Error to stop retrying if the channel cannot set custom thumbnails.

If a GitHub write fails or conflicts, the workflow stops. If YouTube accepted the video but saving the URL failed, Uploading remains and blocks duplicate uploads. Inspect Studio and restore the CSV as above. There is no atomic transaction across GitHub and YouTube, so ambiguous outcomes need review.

## Validation and limitations

Run `python -m unittest discover -s tests` and `python -m compileall -q src scripts` from the project folder. Live API upload requires your credentials and repository permissions. No channel has been connected or uploads performed during code creation. Dependencies use compatible version ranges. Keep the CSV below GitHub Contents API's inline-content limit (under 1 MB recommended); archive old completed rows separately if it grows, retaining their upload records.

Official references:
- https://docs.github.com/en/rest/repos/contents
- https://docs.github.com/en/actions/concepts/security/github_token
- https://developers.google.com/youtube/v3/docs/videos/insert
- https://developers.google.com/youtube/v3/docs/thumbnails/set

## Animal videos — use now

All four formats run through the same queue: birthday, rain, music, animal.

Add a tenth column J named exactly `Style`. Existing CSVs with seven, eight or nine columns remain supported. When adding Style, use all three optional headers in order: H Type, I Duration Seconds, J Style. Preserve all existing upload records.

| Name (A) | Type (H) | Duration Seconds (I) | Style (J) |
|---|---|---|---|
| cat | animal | 30 | cartoon |
| dog | animal | 30 | pastel |
| bird | animal | 30 | neon |
| fish | animal | 30 | silhouette |

Set Status (B) to Pending and leave C–G empty for new requests. Name is the animal species, not a pet's personal name.

Supported species: cat, dog, rabbit, bird, fish, butterfly, elephant, lion. Case is ignored. Unsupported animals fail before upload rather than showing a different animal.

Styles: cartoon (brand colors), pastel (soft light colors), silhouette (dark animal shapes), neon (bright colors on a dark background). Style currently applies only to animal videos; birthday/rain/music retain their existing branded designs. Blank animal Style defaults to cartoon.

Animal videos are landscape 1280×720 illustrated animation at 12 fps, with movement, blinking or wing/tail motion depending on species, original generated instrumental background audio, no narration and no realistic animal sounds. Duration supports 10–600 seconds (default 60). There are no downloaded photos, stock videos, real wildlife clips or AI-generated realistic video in this version. No extra API key is required.

The thumbnail shows the chosen species and style; upload titles and descriptions clearly label the videos as animation. Set MADE_FOR_KIDS accurately for your intended audience; animal cartoons can require a different audience decision than relaxation content. This starter uses one repository-wide setting, so process batches with the appropriate audience setting rather than mixing content that requires different settings.

Run preview first and inspect the animal MP4/JPG files before enabling upload. Files are generated and uploaded automatically only after your YouTube authorization and GitHub permissions are configured.
