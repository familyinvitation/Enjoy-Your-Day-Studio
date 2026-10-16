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
Gentle Rain,Pending,,,,,,rain,1800,
Peaceful Moments,Pending,,,,,,music,1800,
cat,Pending,,,,,,animal,30,cartoon
dog,Pending,,,,,,animal,30,pastel
```

Open the file on GitHub → pencil icon (Edit) → append a row → Commit changes to the default branch. Do not remove completed rows. Do not edit the queue while a run is processing it. If you do, conditional writes protect your edits, but the workflow will stop and may require recovery.

Birthday: longer vertical video with English female narration of a short personalized birthday greeting repeated over soft instrumental music (90-second minimum by default). Rain/music: landscape illustrated animation, no narration; 1800–7200 seconds (default 1800). Rain is digitally synthesized noise, not a natural field recording. Music is a simple original procedural instrumental, not a full AI song generator. Public repositories expose queue names and video links; use a private repository if desired.

## 3. Voice generation now uses Piper

No Google Cloud Text-to-Speech API, billing account, service account JSON or speech API key is needed. The workflow installs piper-tts 1.8.0 from its published Python package (OHF-Voice/piper1-gpl) and downloads en_US-ljspeech-medium model/config and its model card on the first birthday request. Model files are cached by GitHub Actions; later synthesis runs offline on CPU. Internet is required for installation and initial downloads. No laptop commands are needed. Rain, music and animal formats continue as before.

The chosen model card describes a single-speaker US English female voice trained on the public-domain LJ Speech dataset. The model repository is marked MIT; the maintained engine is GPL-3.0. See THIRD_PARTY_NOTICES.md for upstream sources and terms. This project integrates the installed engine rather than copying the entire upstream repository. Do not remove upstream notices when redistributing upstream code or models. The generated voice is a pretrained narrator, not a clone of your own voice. Test name pronunciation in preview mode.

## 4. Browser-only YouTube authorization

If your four YouTube secrets are already saved, keep them; the Piper change does not require reauthorizing YouTube.

For a new setup: enable YouTube Data API v3. In Google Auth Platform create a Web application OAuth client with authorized redirect URI https://developers.google.com/oauthplayground (not JavaScript origins). Add your Google account as a test user if the app is in Testing.

Open https://developers.google.com/oauthplayground/ → settings → Server-side flow, Offline access, Consent Screen prompt, Use your own OAuth credentials. Enter your Web client ID and secret. In Step 1 authorize both scopes:

https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly

Sign in and select Enjoy Your Day Studio. In Step 2 exchange the authorization code immediately, then save the refresh token directly to GitHub Secrets. Never share tokens, client secrets or screenshots containing them. No local Python authorization is required; scripts/authorize_youtube.py remains an optional local alternative using a Desktop client.

External OAuth apps in Testing generally issue seven-day refresh tokens for these scopes. For long-term unattended use, move to Production where appropriate and obtain a new token. OAuth production/verification and YouTube compliance auditing are separate. Revoked tokens need reauthorization.

## 5. Add GitHub Secrets and Variables

Settings → Secrets and variables → Actions → Secrets:

| Secret | Value |
|---|---|
| YOUTUBE_CLIENT_ID | From the authorization JSON |
| YOUTUBE_CLIENT_SECRET | From the authorization JSON |
| YOUTUBE_REFRESH_TOKEN | From the authorization JSON |
| YOUTUBE_CHANNEL_ID | From the authorization JSON |

GOOGLE_SHEET_ID and GOOGLE_SERVICE_ACCOUNT_JSON are not needed; remove them if previously added. Do not add a personal GitHub access token. GitHub automatically provides the workflow's temporary GITHUB_TOKEN.

Variables:

| Variable | Value |
|---|---|
| UPLOADS_ENABLED | false initially, then true |
| YOUTUBE_PRIVACY | private initially; public when ready |
| MADE_FOR_KIDS | true or false according to your actual intended audience |

Under Settings → Actions → General → Workflow permissions, allow Read and write permissions if your repository allows it. The workflow declares contents: write to update the CSV. Organization policies or branch protection may block direct commits; this workflow requires bot commits to the default branch. If blocked, use a repository where this permission is allowed. The program refuses to upload until it can persist the Processing and Uploading states.

## 6. Preview and activate

Actions → Enjoy Your Day Studio videos → Run workflow → leave preview checked. Download MP4/JPG preview artifacts from the finished run. Preview reads the CSV but does not modify it or upload to YouTube. Birthday preview uses Piper on the GitHub runner with no speech API calls.

Then set UPLOADS_ENABLED=true and manually run with preview unchecked. Confirm private video URLs appear in the repository's CSV. The file visible in the workflow checkout may be older: refresh the CSV on GitHub to see API commits.

The workflow also runs on user commits to names-template.csv and hourly at minute 17, on the default branch only. Its own status commits use GITHUB_TOKEN, so they do not trigger a workflow loop. Scheduled jobs can be delayed and public repository schedules may be disabled after 60 days of inactivity. Maximum one new video and one thumbnail retry per run. You can edit MAX_PER_RUN in the workflow (1–10).

YouTube may restrict public uploads or Shorts thumbnails based on API project/channel eligibility. Test with your actual account. Setting public does not override YouTube restrictions. This code does not update your channel profile, banner, description or playlists; apply the supplied branding images in YouTube Studio yourself.

## Recovery

Every Processing, Uploading, Uploaded and thumbnail transition is committed immediately to GitHub through the Contents API with a file SHA guard. No end-of-job push is needed. A crash cannot rely on the runner's local disk as durable state.

- Pending or blank: eligible.
- Processing: generation started; after a killed run, inspect before resetting to Pending.
- Uploading / Needs Review: outcome uncertain. Check YouTube Studio and match the description's Reference job ID to column E. If found, save the URL and mark Uploaded. Do not reset blindly.
- Uploaded: skipped; keeps the YouTube URL.
- Error: fix generation, voice download, credentials or input, then set Pending.
- Uploaded with Error starting Thumbnail pending:: retry only the thumbnail. Never reset this video to Pending. Clear Error to stop retrying if the channel cannot set custom thumbnails.

If a GitHub write fails or conflicts, the workflow stops. If YouTube accepted the video but saving the URL failed, Uploading remains and blocks duplicate uploads. Inspect Studio and restore the CSV as above. There is no atomic transaction across GitHub and YouTube, so ambiguous outcomes need review.

## Validation and limitations

Run `python -m unittest discover -s tests` and `python -m compileall -q src scripts` from the project folder. Live API upload requires your credentials and repository permissions. No channel has been connected or uploads performed during code creation. Dependencies use compatible version ranges. Keep the CSV below GitHub Contents API's inline-content limit (under 1 MB recommended); archive old completed rows separately if it grows, retaining their upload records.

Official references:
- https://docs.github.com/en/rest/repos/contents
- https://docs.github.com/en/actions/concepts/security/github_token
- https://developers.google.com/youtube/v3/docs/videos/insert
- https://developers.google.com/youtube/v3/docs/thumbnails/set

## Real animal footage — automatic Coverr selection

The geometric animal renderer has been removed. Animal requests now search Coverr for the selected species playing, select at least two distinct landscape clips whose metadata indicates activity, trim and assemble them with instrumental background music, and create a thumbnail from the actual selected footage. A new GitHub secret COVERR_API_KEY is required. Obtain it through https://coverr.co/developers and paste it directly into GitHub repository Secrets. Do not share it or commit it.

Set Type=animal, Name=cat/dog/rabbit/bird/fish/butterfly/elephant/lion, Style=real, Duration Seconds=30 (10–600 supported). Existing cartoon/pastel/neon/silhouette animal rows also use real footage after this update. They do not fall back to illustrations. If no matching clips or API key are available, the request fails before YouTube upload. Activity matching uses source metadata, not computer vision: swimming/flying/running may be selected, and playing cannot be guaranteed. Preview to check relevance.

Clips are normalized to 1280×720 at 24 fps and assembled with generated music. Source audio is removed; videos are not claimed to contain authentic animal sounds. Requests longer than the assembled footage repeat the compilation. Source contributor names and Coverr links are included in the YouTube description and preview .sources.json artifact. Review Coverr terms and API rules; API limits apply. Using stock clips does not guarantee YouTube monetization eligibility.

Thumbnail retries use the original selected frame cached in .cache/animal-thumbnails. If it is no longer available, the thumbnail retry fails rather than using a frame from unrelated footage. Apply a thumbnail manually for that already-uploaded video if needed; never reset Uploaded to Pending just to fix a thumbnail.

Keep existing Uploaded rows and links unchanged; this update does not delete or replace videos already on YouTube. To make a replacement video, add a NEW Pending row and manage the old upload manually in YouTube Studio. Start in preview mode. Choose MADE_FOR_KIDS based on the actual target audience; it remains a global setting.

References:
- https://coverr.co/developersdocumentation/
- https://coverr.co/terms
- https://coverr.co/license

## Upgrade from the previous Google voice edition

Replace src/voice.py, src/main.py, src/config.py, requirements.txt and .github/workflows/birthday-upload.yml (or upload this entire updated project while preserving your CSV data). Keep the four existing YouTube secrets. No Google billing activation is required. Run preview with a single Pending birthday row first, inspect the MP4 narration, then enable uploads. GitHub processing and YouTube quotas still apply; free speech generation does not mean unlimited free hosting or uploads.

## Longer birthday videos with your lyrics

Birthday rows now use Duration Seconds (column I). Blank means a minimum of 90 seconds; choose 60–600. Example: `Amit,Pending,,,,,,birthday,120,` makes a personalized video at least two minutes long. Animal videos retain their 10–600 second limits; rain/music use 1800–7200 seconds.

The short greeting lives in src/birthday_song.py: Today’s your day, the candles glow; There’s someone special we all know; <Name>, let’s celebrate with you; With love and laughter all day through; Happy Birthday <Name>! Every <Name> is replaced by the CSV name. This complete greeting repeats with short pauses until the requested minimum duration is reached. Nothing is cut mid-line. Soft, cheerful instrumental music plays underneath.

Piper is a speech engine: this is spoken birthday lyrics over instrumental music, not a sung vocal performance. True singing would need a separate singing model or a supplied licensed song recording. Background artwork and thumbnails continue to show Happy Birthday and the person's name; there are no synchronized lyric captions in this version.

Replace code files and keep existing CSV records/secrets. Completed uploads are unchanged. Use a new Pending row to make a new longer version. Preview first; longer renders use more GitHub runner time. The ZIP's CSV is a sample, not a replacement for your upload history.

## Rain and relaxing music: minimum 30 minutes

Rain and music now default to 1800 seconds (30 minutes). Column I Duration Seconds accepts 1800–7200 seconds for these types. Any positive value below 1800 (including old sample rows with 60) is automatically raised to 1800. Zero, negative or invalid values fail validation. Examples: 1800 = 30 minutes, 3600 = 1 hour, 7200 = 2 hours. Birthday and animal duration rules are unchanged.

The renderer encodes a short illustrated animation once, loops its visual track, and generates the audio for the full requested duration with opening/closing fades. This reduces encoding time and does not repeat the short clip's faded audio. The visual loop may have a visible reset; this version uses a repeating illustrated scene rather than unique footage throughout. The generated music uses a repeating chord progression; rain remains synthetic noise.

Preview also generates the full requested 30-minute-or-longer video. Workflow batches now process one new video per run, with a 180-minute timeout. GitHub runner/storage quotas and YouTube limits still apply. Your channel must support uploads longer than 15 minutes. Test a private upload first. Previously Uploaded rows are not recreated.

## Coverr upgrade

Save your Coverr key as repository secret COVERR_API_KEY. Replace src/stock_animals.py, src/content.py, src/youtube.py and .github/workflows/birthday-upload.yml, plus README.md and the updated tests (or upload all code while preserving your CSV). PEXELS_API_KEY is no longer used. Birthday/Piper, rain and music do not require Coverr.

This adapter uses Coverr's documented /videos endpoint with Bearer authentication, query/page_size/urls parameters and hits response. Signed mp4_download URLs are used for tracked downloads, and are not written into public source credits. Search is limited to at most three calls per animal job. Your dashboard's Demo allowance is 50 requests/hour; account restrictions and Coverr's current terms still apply. Source availability is not guaranteed.

For a new animal request, use cat,Pending,,,,,,animal,60,real. Keep Uploaded rows unchanged; use a NEW row for a replacement video. If an older unsuccessful request is Error or Paused and has no YouTube URL, set it Pending after fixing setup. Never reset Uploading/Needs Review without checking YouTube Studio first.

Preview first. Metadata filtering checks animal/activity keywords and excludes explicitly flagged AI footage, but cannot prove that the animal is playing or that an unflagged clip is camera footage. Human review is recommended before the first public batch. Missing or unrecognized media fields cause a failure instead of a cartoon fallback. This update has fixture-based API tests; live use of your GitHub secret must be tested in Actions because it is not available in this chat runtime.

## Diagnosing a failed row

Failures now report the stage and a safe explanation in Error and Actions logs. The old generic billing/permissions message did not diagnose the cause. For Coverr, the logs include per-attempt result counts, and the Error cell distinguishes missing secrets, access errors and insufficient matching clips. Raw provider responses, API keys and signed media links are not printed.

After installing this update, retry only a row whose Status is Error and YouTube URL is blank: set Status to Pending and run a NEW workflow (preview recommended first). Preview does not edit the CSV, so read its Process queue log for the new diagnostic. Leave Uploaded, Uploading and Needs Review rows unchanged until inspected in Studio.
