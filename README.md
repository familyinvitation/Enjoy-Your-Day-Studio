# Enjoy Your Day Studio — multi-format update

**Celebrate. Relax. Enjoy Your Day.**

This update supports personalized birthday Shorts, synthesized rain ambience and original gentle instrumental videos in the same automatic queue. Purple, coral and turquoise artwork matches the latest channel direction.

## Updated Sheet (existing birthday rows still work)

Keep columns A–G exactly as before. Add optional column H named `Type` and column I named `Duration Seconds`.

| Name (A) | Status (B) | Type (H) | Duration Seconds (I) |
|---|---|---|---|
| Amit | Pending | birthday | blank |
| Gentle Rain | Pending | rain | 60 |
| Peaceful Moments | Pending | music | 60 |

Leave C–G for automation. Blank Type means birthday, so your existing name sheet still works. Rain/music labels become the video title; they are not spoken. Use 10–600 seconds for rain/music (default 60). Birthday videos remain short vertical videos with English female narration; ambience videos are landscape 1280×720 with animated illustrated scenes and no narration. The code generates both audio and artwork locally for rain/music; it does not download recordings or produce AI music. Rain is filtered synthetic noise; music is a simple original procedural instrumental, not a commercial-quality song generator.

Each type receives its own title, description, tags and personalized thumbnail. The same automatic upload, Sheet status, preview mode and thumbnail recovery apply. No new secrets are needed. Preview uses the requested duration too. Start with 10–60 seconds before rendering longer videos. Long-form hours-long videos are outside this starter version.

## Upgrade on GitHub

1. Replace the previous project files with this version, including `.github/workflows/birthday-upload.yml`.
2. Preserve your existing Secrets and Variables. Add H/I to the Sheet only when you need the new formats.
3. Run Actions manually with preview checked. Download the MP4/JPG artifacts and listen to each audio type.
4. Run with preview unchecked when ready; scheduled jobs continue automatically when UPLOADS_ENABLED=true.

The generated profile and banner are included under `assets/branding` for reference/manual channel setup. This project does not change your channel profile, banner or description through the API. Set those in YouTube Studio. No playlist creation is performed automatically.

# Enjoy Your Day Studio

Google Sheet → hourly GitHub Actions → animated vertical birthday video with English female narration → YouTube upload + personalized thumbnail → Sheet updated.

Birthday format includes original procedural cake, balloons and confetti, four palettes and four spoken wishes. Outputs 1080×1920 MP4 at 24 fps, approximately 12–20 seconds. No external pictures are required. The generated background melody is original; no downloaded songs are used. These modest variations do not guarantee YouTube monetization eligibility.

## 1. Upload the project to GitHub

Create `enjoy-your-day-studio` (a private repository is recommended). Extract this ZIP and upload the CONTENTS of the project folder into the repository root. Ensure `.github/workflows/birthday-upload.yml` is included. GitHub's web upload may omit hidden folders on your computer; use Add file → Create new file and paste the workflow using that full path if needed. Commit to your default branch.

## 2. Create the Google Sheet

Create a spreadsheet and rename the first tab `Names`. Import `names-template.csv`, or put these EXACT headers in row 1, columns A–G:

| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| Name | Status | YouTube URL | Uploaded Date | Job ID | Updated At | Error |

Add each name on its own row. Set Status to `Pending`, or leave it blank. Keep the other columns empty. The same name on two different rows deliberately creates two videos; deduplication is per row, not per name.

While a workflow is running, only append new names at the bottom. Do not sort, insert, delete, or edit existing queue rows: the queue uses row positions. Use only one repository/workflow against this Sheet. GitHub concurrency prevents overlapping runs within this repository, not external workers.

Copy the spreadsheet ID from the URL between `/d/` and `/edit`.

## 3. Google Cloud setup

At https://console.cloud.google.com/ create a project. Enable:

- Google Sheets API
- YouTube Data API v3
- Cloud Text-to-Speech API

Enable billing for Text-to-Speech and set a budget alert. Usage may incur charges; GitHub Actions usage may also incur charges based on your plan.

Under IAM & Admin → Service Accounts, create an account for the automation. Grant the Text-to-Speech User role (or the documented equivalent for your project). Create/download a JSON key. Share the Google Sheet with the JSON's `client_email`, giving Editor access. Do not make the Sheet public.

## 4. Authorize YouTube once

Configure Google Auth Platform / OAuth consent. Choose External if needed; add your own Google account as a test user. Create an OAuth client of type Desktop app; download its JSON.

A one-time authorization needs a browser on your own computer; the hourly jobs run entirely on GitHub afterward. On Windows 11, install Python 3.12, then run these commands from the project folder:

```powershell
py -m pip install -r requirements.txt
py scripts/authorize_youtube.py client_secret.json
```

Replace `client_secret.json` with the downloaded filename. Sign in and select the actual Enjoy Your Day Studio channel (including the correct Brand Account if applicable). The script prints the channel name and saves credentials in `youtube-token.json`. It never prints the refresh token.

For unattended operation, move the OAuth app from Testing to Production when appropriate and reauthorize. External apps in Testing generally have seven-day refresh tokens for these scopes. Production status is separate from OAuth verification and YouTube's API compliance audit. Tokens can still expire or be revoked; if authentication fails, authorize again and replace the secret.

## 5. GitHub Secrets

Repository → Settings → Secrets and variables → Actions → Secrets → New repository secret:

| Secret | Value |
|---|---|
| GOOGLE_SERVICE_ACCOUNT_JSON | Entire service-account JSON file |
| GOOGLE_SHEET_ID | Spreadsheet ID |
| YOUTUBE_CLIENT_ID | Corresponding value in youtube-token.json |
| YOUTUBE_CLIENT_SECRET | Corresponding value in youtube-token.json |
| YOUTUBE_REFRESH_TOKEN | Corresponding value in youtube-token.json |
| YOUTUBE_CHANNEL_ID | Corresponding value in youtube-token.json |

Never upload either JSON credential file to GitHub or paste credentials into chat. `.gitignore` protects ordinary git commits, but cannot prevent manual web uploads. Revoke and replace exposed credentials immediately.

Under the Variables tab, create:

| Variable | Initial value |
|---|---|
| UPLOADS_ENABLED | false |
| YOUTUBE_PRIVACY | private |
| MADE_FOR_KIDS | true or false, based on the actual intended audience |

Birthday visuals alone do not decide whether content is made for kids. You must set the accurate audience classification yourself. The workflow refuses uploads if it is unset.

## 6. Preview test

GitHub → Actions → Enjoy Your Day Studio videos → Run workflow. Leave `preview` checked. It reads up to three Pending names and generates videos WITHOUT uploading or changing the Sheet. Text-to-Speech usage is still billed. Open the finished run and download `birthday-previews` under Artifacts to watch the MP4 files and inspect the personalized JPG thumbnails.

## 7. Upload test and automatic operation

Set `UPLOADS_ENABLED=true`. Run workflow manually with `preview` unchecked. The videos upload as private by default, and URLs appear in the Sheet. `Uploaded` means YouTube accepted the upload; processing and visibility may take additional time.

Once ready, set `YOUTUBE_PRIVACY=public` if desired. YouTube may restrict uploads from unverified API projects to private pending a compliance audit; setting public in this code does not override Google's restriction. Check current project eligibility and documentation.

The schedule runs at minute 17 of every hour, processing at most three rows. New pending names wait for the next available scheduled run. Scheduled jobs are best effort and may be delayed. They run from the default branch. Public repositories can have schedules disabled after 60 days without repository activity; check Actions if runs stop.

Daily routine: append names, then look for `Uploaded` and a link. No manual YouTube upload is required after setup.

## Recovery and avoiding duplicates

| Status | Meaning / action |
|---|---|
| Pending or blank | Eligible for next run |
| Processing | Rendering started; left here after a killed run. Check logs and YouTube before resetting to Pending |
| Uploading | Upload may be in progress or have succeeded. Do not blindly reset |
| Uploaded | Accepted by YouTube, skipped on subsequent runs |
| Error | Pre-upload failure. Fix credentials/API/billing/input, then set Pending |
| Needs Review | Upload outcome uncertain. Inspect YouTube Studio before retrying |

For Uploading/Needs Review, search YouTube Studio for the birthday title and check the video description's `Reference: JOB-ID` against Sheet column E. If found, fill the URL and set Uploaded. If absent, wait for processing and confirm no upload exists before setting Pending. The job ID is reused on retry. There is no atomic transaction spanning Sheets and YouTube, so this system intentionally blocks ambiguous retries instead of claiming perfect exactly-once delivery.

API errors are summarized without dumping provider responses or secrets into logs. Check APIs, billing, token validity and permissions when a row fails. A failed row makes the GitHub job fail visibly. Other Pending rows can run next time. If Sheet access fails completely, the workflow stops.

## Customize

Edit workflow env: `MAX_PER_RUN` (1–10), `TTS_VOICE`, `GOOGLE_SHEET_TAB`. The supplied female voice is `en-US-Neural2-F`. Edit `src/video.py` for palettes, artwork and scripts. Dependencies use compatible ranges; resolve and lock exact versions for long-term reproducibility.

## Validation

```bash
python -m compileall -q src scripts
python -m unittest discover -s tests
```

Real API calls require your credentials. No channel has been connected or videos uploaded as part of creating this project.

## Official references

- https://developers.google.com/youtube/v3/docs/videos/insert
- https://developers.google.com/identity/protocols/oauth2#expiration
- https://docs.cloud.google.com/text-to-speech/docs/create-audio-text-client-libraries
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows

## Automatic personalized thumbnails

Every new video also gets a 1080×1920 portrait JPEG with HAPPY BIRTHDAY, the name, cake, balloons and matching colors. The thumbnail is created with Pillow inside GitHub Actions, requiring no extra key or image-generation fees. Preview artifacts contain both MP4 and JPG files.

The program first saves the successfully uploaded video's URL in the Sheet, then calls YouTube `thumbnails.set`. The existing `youtube.upload` permission covers this; no new OAuth scope is required.

If thumbnail upload fails, Status stays Uploaded, and Error shows `Thumbnail pending:`. Later runs retry ONLY that thumbnail (up to MAX_PER_RUN thumbnail retries in addition to new videos). They never upload the birthday video again. Fix channel eligibility, permissions or quota before retrying. To stop retrying an unavailable thumbnail, clear its Error cell; do not set that video's Status back to Pending. Existing Uploaded rows without that marker are unchanged. To apply thumbnails to older uploads, fill Job ID if missing and set Error to `Thumbnail pending: requested`.

Custom thumbnail permission must be enabled on the channel. Shorts thumbnail access depends on channel eligibility; YouTube announced a rollout starting with YouTube Partner Program creators. API acceptance/display for your channel must be tested, and a custom thumbnail is not guaranteed to appear on every Shorts surface. The video itself already displays Happy Birthday and the name, even when a custom image is unavailable.

References:
- https://developers.google.com/youtube/v3/docs/thumbnails/set
- https://blog.youtube/news-and-events/youtube-studio-custom-thumbnail-updates/
