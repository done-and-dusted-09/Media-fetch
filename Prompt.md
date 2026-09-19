BUILD A FULLY SELF-CONTAINED yt-dlp MEDIA DOWNLOADER

Build a polished, production-quality media downloader application using yt-dlp as the core extraction and download engine.

The application must be designed as a standalone/self-contained application.

The most important requirements are:

1. The user installs the application once.
2. Python is already bundled inside the application.
3. yt-dlp is already bundled inside the application.
4. All required yt-dlp dependencies are already bundled.
5. FFmpeg/FFprobe are already bundled when required.
6. Normal application use must NOT download any software dependencies.
7. The user can paste a supported URL and retrieve its available formats.
8. The user can select a format and download only that media.
9. The application must provide an explicit Check for Updates / Update Components feature.
10. Updates must happen ONLY after the user explicitly requests them.
11. Updates must be capable of replacing outdated bundled components such as yt-dlp when websites change and the bundled version stops working.
12. There must be NO mandatory cloud backend for normal operation.

---

1. TARGET PLATFORM

First inspect the project/environment and determine the target platform.

If the platform has not been specified, ask for the target platform before implementing platform-specific packaging.

The architecture must support the following principle regardless of platform:

┌─────────────────────────────────────────┐
│          Standalone Application         │
│                                         │
│  UI                                     │
│  Downloader Controller                  │
│  Bundled Python                         │
│  Bundled yt-dlp                         │
│  Bundled dependencies                   │
│  Bundled FFmpeg / FFprobe               │
│  Update Manager                         │
│                                         │
└─────────────────────────────────────────┘
                    │
                    ▼
             Target website
                    │
                    ▼
             Selected media
                    │
                    ▼
              Local storage

For Android, investigate the most appropriate maintained embedded-Python approach.

For Windows/macOS/Linux, use an appropriate self-contained packaging approach.

Do not choose a framework merely because it is familiar. Choose the framework that provides the most reliable implementation for the selected target.

---

2. CORE PRINCIPLE

This application is a GUI frontend around yt-dlp.

Do NOT recreate yt-dlp.

Do NOT build a custom YouTube scraper.

Do NOT hard-code YouTube format IDs.

Do NOT manually reverse-engineer the website.

Use the official yt-dlp Python package/API as the extraction and download engine.

Conceptually:

User
 ↓
Application UI
 ↓
Download Controller
 ↓
Bundled yt-dlp
 ↓
Target website

---

3. FULLY SELF-CONTAINED INSTALLATION

The final application package must contain everything required for normal operation.

Bundle:

- Python runtime
- yt-dlp
- all required Python packages
- yt-dlp support components required by the chosen configuration
- FFmpeg
- FFprobe
- required native libraries
- application code
- UI assets
- configuration
- update manager
- required certificates/resources where applicable

The user should NOT need to separately install:

Python
pip
yt-dlp
FFmpeg
FFprobe
Node.js
Git
developer tools

Do not depend on anything being available in the system PATH.

---

4. ZERO RUNTIME DEPENDENCY DOWNLOADS

This is a NON-NEGOTIABLE requirement.

After installation, the application must NOT automatically download:

- Python
- yt-dlp
- pip
- Python packages
- FFmpeg
- FFprobe
- Node.js
- codecs
- native libraries
- plugins
- application dependencies
- runtime components

Normal operation must not contain any hidden bootstrapper.

Do NOT implement:

pip install ...
pip install yt-dlp
python -m pip install ...
download yt-dlp
download FFmpeg
download Python
download dependencies

The application must work without a package manager.

---

5. IMPORTANT NETWORK DISTINCTION

The application IS allowed to access the internet when the user asks it to process a media URL.

There are two types of network activity:

Allowed

User pastes URL
       ↓
yt-dlp contacts target website
       ↓
metadata/formats

and:

User selects format
       ↓
yt-dlp contacts target website
       ↓
selected media downloaded

NOT allowed during normal use

download Python
download yt-dlp
download FFmpeg
download dependencies
download packages
automatic software updates
automatic component updates

The application must never confuse "fetching video metadata" with "downloading application dependencies."

---

6. EMBEDDED PYTHON

Bundle the Python runtime.

Never rely on:

python
python3
py

being installed on the user's machine.

The application must invoke its own bundled Python runtime.

Conceptually:

Application
   ↓
Bundled Python
   ↓
Bundled yt-dlp

The Python environment must contain all packages required by yt-dlp.

Do not execute "pip install" at runtime.

---

7. yt-dlp

Bundle a pinned, tested yt-dlp version.

The exact version should be recorded in the application's diagnostics/about information.

Example:

yt-dlp version: X.Y.Z

Do not dynamically fetch "latest yt-dlp" during normal application startup.

Do not silently update yt-dlp.

The installed version must remain deterministic until the user explicitly chooses to update components.

---

8. yt-dlp SUPPORT COMPONENTS

Before finalizing the architecture, inspect the current yt-dlp requirements for the selected release.

If the selected yt-dlp configuration requires additional components for supported extraction, those components must also be packaged.

Do not assume that:

Python + yt-dlp + FFmpeg

is necessarily sufficient for every current yt-dlp extraction scenario.

For example, if the selected yt-dlp version/configuration requires a JavaScript runtime or yt-dlp-supported companion package for certain sites, determine the correct supported approach and bundle it where technically/legal appropriate.

The user must not be required to install these separately.

---

9. FFmpeg AND FFPROBE

Bundle FFmpeg and FFprobe when required.

The application must explicitly configure yt-dlp to use the bundled binaries.

Never require the user to install FFmpeg.

Never silently download FFmpeg.

Use safe executable paths.

Respect all applicable FFmpeg licensing requirements.

---

10. URL INPUT

Main UI:

┌─────────────────────────────────────────┐
│           Media Downloader              │
│                                         │
│ Paste media URL                         │
│ ┌─────────────────────────────────────┐ │
│ │ https://...                         │ │
│ └─────────────────────────────────────┘ │
│                                         │
│           [ Fetch Formats ]             │
└─────────────────────────────────────────┘

Accept supported URLs that yt-dlp can process.

Do not hard-code support exclusively for YouTube if yt-dlp supports other sites.

The UI may describe the application as "powered by yt-dlp."

---

11. METADATA EXTRACTION

When the user presses Fetch Formats, invoke yt-dlp locally.

Use its Python API.

Conceptually:

info = ytdlp.extract_info(url, download=False)

Do not download the media during this operation.

Extract:

- title
- uploader/channel
- duration
- thumbnail URL if needed by the UI
- webpage URL
- formats
- available resolutions
- codecs
- extensions
- FPS
- audio information
- approximate sizes

Do not download every available format.

---

12. FORMAT LIST

Dynamically construct the format list from:

info["formats"]

Do not hard-code format IDs.

Each format should expose useful information such as:

- format ID
- extension
- resolution
- width
- height
- FPS
- video codec
- audio codec
- bitrate
- file size
- format note
- video/audio presence

Handle missing metadata gracefully.

For example, file size may not always be known.

---

13. USER-FRIENDLY FORMAT UI

Do not make normal users understand raw yt-dlp format IDs.

Group formats into:

VIDEO + AUDIO

1080p • MP4 • 30 FPS • Video + Audio
720p  • MP4 • 30 FPS • Video + Audio
480p  • MP4 • 30 FPS • Video + Audio

VIDEO ONLY

2160p • AV1 • Video Only
1440p • VP9 • Video Only
1080p • H.264 • Video Only

AUDIO ONLY

Best Audio • M4A
Best Audio • Opus

These entries must be generated dynamically.

Never promise a format that yt-dlp did not report.

---

14. DOWNLOAD

When the user chooses a format:

Selected format
       ↓
yt-dlp
       ↓
download

Only the requested media should be downloaded.

Do NOT automatically download all formats.

Do NOT pre-cache all media streams.

Do NOT download media before the user selects a format.

---

15. SEPARATE VIDEO + AUDIO

If the selected quality requires separate video and audio streams, use yt-dlp's format-selection mechanism and bundled FFmpeg.

Conceptually:

Video stream
     +
Audio stream
     ↓
yt-dlp
     ↓
Bundled FFmpeg
     ↓
Final media file

Do not write unnecessary custom merging logic.

---

16. DOWNLOAD PROGRESS

Use yt-dlp progress hooks.

Display:

- filename
- percentage
- downloaded bytes
- total bytes when known
- speed
- ETA
- current status

Example:

Downloading

My Video.mp4

████████████████░░░░ 78%

78%
5.2 MB/s
ETA 00:16

[ Cancel ]

Downloading must happen asynchronously.

Never block the UI thread.

---

17. CANCELLATION

Provide:

[ Cancel Download ]

Cancellation must stop the current yt-dlp operation safely.

Do not terminate the entire application.

Clean up incomplete temporary files when appropriate.

---

18. DOWNLOAD DIRECTORY

Allow the user to select a download directory.

Use the platform's recommended storage APIs.

Do not request unnecessary filesystem permissions.

Support:

- default Downloads directory
- custom directory
- filename display
- open containing folder
- completed-file access

---

19. FILENAMES

Use yt-dlp's output template functionality where appropriate.

Safely handle:

- Unicode
- long titles
- invalid filename characters
- duplicate filenames
- missing titles

Prevent path traversal.

Do not allow metadata to escape the selected download directory.

---

20. ERROR HANDLING

Handle:

- invalid URL
- unsupported URL
- unavailable media
- private media
- authentication-required content
- geographic restrictions
- network failures
- extraction failures
- FFmpeg failures
- insufficient storage
- permissions
- interrupted downloads
- changed website behavior

User-facing error:

Unable to retrieve this video's formats.

Provide an expandable technical diagnostics section for developers.

Do not dump raw Python tracebacks onto normal users.

---

21. OFFLINE STARTUP

The application itself must launch without internet access.

Offline mode must allow:

- opening the app
- opening settings
- viewing About
- viewing bundled component versions
- checking local runtime health
- viewing existing downloads

Only network-dependent operations should fail while offline:

- fetching URL metadata
- downloading media
- checking for updates

---

22. LOCAL STARTUP HEALTH CHECK

At application startup, verify locally:

Bundled Python       ✓
yt-dlp               ✓
FFmpeg               ✓
FFprobe              ✓
Required components  ✓

Do not contact the internet to perform this check.

If something is missing:

The application installation appears to be incomplete.

Please reinstall the application.

Do NOT download the missing component automatically.

---

23. UPDATE SYSTEM

The application must include:

Settings → Updates

and:

Check for Updates

The updater is the ONE intentional mechanism that may retrieve new application components.

Normal downloading must never invoke the updater.

---

24. UPDATE BUTTON

Provide a visible button:

[ Check for Updates ]

When pressed, the application may contact the official update source.

It should check for:

- newer yt-dlp version
- newer required support components
- newer FFmpeg/FFprobe when applicable
- newer application release
- other bundled extraction dependencies when required

Do not update anything automatically.

---

25. UPDATE PROCESS

If no update exists:

You're up to date.

Current version:
yt-dlp X.Y.Z

If an update exists:

Update available

Current yt-dlp:
X.Y.Z

New yt-dlp:
A.B.C

Reason:
Compatibility improvements and bug fixes.

[ Update Now ]
[ Later ]

The user must explicitly press Update Now.

---

26. WHAT THE UPDATE MAY CHANGE

The updater may replace bundled components such as:

yt-dlp
yt-dlp support packages
required runtime components
FFmpeg/FFprobe
other approved bundled extraction components

depending on the release manifest.

Do not describe these as "backend services" because the normal application does not have a remote backend.

Call them:

Bundled Components

or:

Downloader Components

---

27. WHY UPDATES EXIST

The application must explain that website behavior can change.

Example:

Some websites periodically change their delivery
or extraction systems.

Updating the downloader components can restore
compatibility when a newer yt-dlp release contains
the required fix.

Do not claim that an update guarantees support for every future website change.

---

28. UPDATE SECURITY

Do NOT simply download an arbitrary executable/package and replace the existing component.

Implement secure update verification.

The update system should use:

- HTTPS
- signed update manifests where practical
- cryptographic checksums
- version validation
- package validation
- platform validation
- atomic replacement
- rollback support

Conceptually:

Check update
      ↓
Download update package
      ↓
Verify signature/checksum
      ↓
Verify expected version
      ↓
Install to temporary location
      ↓
Validate component
      ↓
Atomically replace old component
      ↓
Restart if necessary

If verification fails:

Update could not be verified.
The existing installation has not been changed.

---

29. ROLLBACK

Before replacing a working component:

Current version
      ↓
Backup/transaction
      ↓
Install new version
      ↓
Validate

If installation or validation fails:

Restore previous working version.

Never leave the application in a partially updated state.

---

30. UPDATE FAILURE

If the update server cannot be reached:

Unable to check for updates.

Your currently installed downloader components
will continue to be used.

Do not break existing functionality because the update service is unavailable.

---

31. NO SILENT UPDATES

Do NOT:

auto-update on startup
auto-update in background
auto-update when fetching formats
auto-update when downloading

Only:

Settings
 ↓
Check for Updates
 ↓
User chooses Update

---

32. NO CLOUD DOWNLOAD BACKEND

The actual media download must happen locally.

Do not create:

User
 ↓
Your server
 ↓
YouTube
 ↓
Your server
 ↓
User

Instead:

User
 ↓
Local yt-dlp
 ↓
Target website
 ↓
User

No cloud server is required for normal media downloading.

---

33. PRIVACY

Do not send the user's URLs to your own server.

Do not upload:

- downloaded files
- filenames
- media metadata
- download history
- user identity

The application should perform normal extraction locally.

Update checks may communicate with the official update infrastructure, but this should be limited to update information/download packages.

---

34. SECURITY

Treat URLs and website metadata as untrusted.

Never construct unsafe shell commands.

Do not concatenate user input into shell commands.

Use safe process argument arrays.

Sanitize filenames.

Prevent:

- command injection
- path traversal
- arbitrary executable execution
- writing outside the selected directory

---

35. ARCHITECTURE

Separate the application into modules.

Suggested structure:

app/
│
├── ui/
│   ├── main_screen
│   ├── url_input
│   ├── video_info
│   ├── format_list
│   ├── download_progress
│   ├── downloads_screen
│   └── settings_screen
│
├── downloader/
│   ├── ytdlp_service
│   ├── format_parser
│   ├── format_selector
│   ├── download_manager
│   └── progress_handler
│
├── runtime/
│   ├── python_manager
│   ├── ffmpeg_manager
│   └── component_health
│
├── updater/
│   ├── update_checker
│   ├── manifest_verifier
│   ├── package_downloader
│   ├── installer
│   └── rollback_manager
│
├── storage/
│   ├── download_directory
│   └── download_history
│
├── models/
│   ├── video_info
│   ├── media_format
│   ├── download_state
│   └── update_info
│
└── tests/

Adapt this structure to the chosen framework.

---

36. NO UI THREAD BLOCKING

Never perform yt-dlp extraction directly on the UI thread.

Never perform downloads directly on the UI thread.

Never perform large file operations directly on the UI thread.

Use the platform's asynchronous/background facilities.

---

37. DOWNLOAD MANAGER

Create a dedicated DownloadManager.

It should handle:

- starting
- progress
- cancellation
- completion
- failure
- temporary files
- final filenames
- download state

Initially support one active download if that provides greater reliability.

Multiple concurrent downloads can be added later.

---

38. DOWNLOAD HISTORY

Maintain local download history if implemented.

Store it locally.

Do not upload it.

Example:

Downloads

My Video
1080p • MP4
Completed
September 19, 2026

[ Open File ]

---

39. ABOUT SCREEN

Provide:

Media Downloader

Application version: X.Y.Z

yt-dlp: X.Y.Z
FFmpeg: X.Y.Z
FFprobe: X.Y.Z

Bundled runtime: ✓

Also show:

Last component update:
[date/time]

if update tracking is implemented.

---

40. UPDATE SETTINGS

Settings should contain:

Updates

Current application version
Current yt-dlp version
Current FFmpeg version

[ Check for Updates ]

Last checked:
Never / date

Automatic updates:
OFF

For this version, automatic component updates should remain OFF.

---

41. TESTING

Create unit tests for:

- URL validation
- format parsing
- missing fields
- missing filesize
- missing FPS
- video-only formats
- audio-only formats
- combined formats
- Unicode filenames
- invalid filenames
- duplicate filenames
- progress events
- cancellation
- errors
- update manifest parsing
- update verification
- rollback

Mock yt-dlp responses where possible.

Do not make all tests depend on live YouTube.

---

42. INTEGRATION TESTING

Create separate integration tests that verify:

URL
 ↓
yt-dlp
 ↓
metadata
 ↓
formats

and:

URL
 ↓
selected format
 ↓
yt-dlp
 ↓
FFmpeg if required
 ↓
final file

Use an appropriate public test URL.

Do not embed a specific real-world video URL as an application dependency.

---

43. CLEAN MACHINE TEST

Before declaring the project finished:

Create a clean test environment.

Ensure there is no:

Python
pip
yt-dlp
FFmpeg
FFprobe
Node
Git

available through PATH.

Install ONLY the generated application.

Then verify:

1. App launches.
2. Bundled Python works.
3. Bundled yt-dlp works.
4. Bundled FFmpeg works.
5. Format extraction works.
6. Format list appears.
7. Download works.
8. FFmpeg merging works when necessary.
9. Final file is playable.
10. Application works without external runtime dependencies.

---

44. NETWORK AUDIT

During testing, monitor network traffic.

Normal download workflow should contain only traffic necessary for:

metadata extraction
media download

It must NOT contain unexpected requests to:

Python download servers
pip
package registries
yt-dlp download servers
FFmpeg download servers
dependency CDNs

The only additional network operation should be an explicit user-requested update check/update.

---

45. UPDATE TEST

Create a test update environment.

Verify:

Current component
      ↓
Update available
      ↓
User clicks Update
      ↓
Update package downloaded
      ↓
Signature/checksum verified
      ↓
New component installed
      ↓
Old component backed up
      ↓
New component tested

Then test a deliberately invalid update package.

Verify:

Invalid package
      ↓
Verification fails
      ↓
Old version remains untouched

Then test an interrupted update.

Verify rollback.

---

46. WEBSITE COMPATIBILITY FAILURE

If a website changes and the bundled yt-dlp version stops working:

The application should NOT automatically download a new version.

Instead show:

This URL could not be processed by the currently
installed downloader components.

Check for a downloader component update in:

Settings → Updates

Then the user can explicitly select:

[ Check for Updates ]

If an appropriate newer component exists:

[ Update Now ]

After updating, retry the URL.

---

47. DO NOT GUARANTEE FUTURE COMPATIBILITY

Do not claim:

Works with every future YouTube update forever.

Instead state:

The application includes an update mechanism so that
newer downloader components can be installed when
compatibility fixes become available.

This is technically accurate.

---

48. USER EXPERIENCE

The application should feel like a polished native application, not a developer tool.

The normal workflow should be extremely simple:

Paste URL
   ↓
Fetch Formats
   ↓
Choose Format
   ↓
Download

Advanced diagnostics should remain hidden unless requested.

---

49. FINAL USER EXPERIENCE

Example:

╔══════════════════════════════════════╗
║          MEDIA DOWNLOADER            ║
╠══════════════════════════════════════╣
║                                      ║
║ Paste URL                            ║
║ ┌──────────────────────────────────┐ ║
║ │ https://youtube.com/watch?...    │ ║
║ └──────────────────────────────────┘ ║
║                                      ║
║          [ Fetch Formats ]           ║
║                                      ║
╠══════════════════════════════════════╣
║ Video Title                          ║
║                                      ║
║ VIDEO + AUDIO                        ║
║                                      ║
║ 1080p • MP4 • 30 FPS     [Download] ║
║ 720p  • MP4 • 30 FPS     [Download] ║
║ 480p  • MP4 • 30 FPS     [Download] ║
║                                      ║
║ VIDEO ONLY                           ║
║                                      ║
║ 1080p • AV1             [Download]  ║
║                                      ║
║ AUDIO ONLY                           ║
║                                      ║
║ Best Audio • M4A        [Download]  ║
╚══════════════════════════════════════╝

During download:

Downloading

video-title.mp4

█████████████████░░░ 82%

82% • 5.1 MB/s • ETA 00:11

[ Cancel ]

---

50. UPDATE UI

Settings:

╔══════════════════════════════════════╗
║               UPDATES                ║
╠══════════════════════════════════════╣
║ Application     1.0.0                ║
║ yt-dlp          2026.xx.xx           ║
║ FFmpeg          X.X.X                ║
║                                      ║
║ [ Check for Updates ]                ║
╚══════════════════════════════════════╝

If an update exists:

╔══════════════════════════════════════╗
║        DOWNLOADER UPDATE             ║
╠══════════════════════════════════════╣
║ yt-dlp update available              ║
║                                      ║
║ Current: 2026.xx                     ║
║ New:     2026.yy                     ║
║                                      ║
║ Compatibility improvements included. ║
║                                      ║
║ [ Update Now ]       [ Later ]       ║
╚══════════════════════════════════════╝

---

51. UPDATE ARCHITECTURE

Keep the updater independent from the downloader.

UI
 │
 ├── Downloader
 │      └── Bundled yt-dlp
 │
 └── Update Manager
        ├── Check manifest
        ├── Download package
        ├── Verify package
        ├── Install
        └── Rollback

The downloader must continue working even if the update service is unavailable.

---

52. BUILD REQUIREMENTS

The final build process must create a distributable package that includes all required runtime components.

Document:

- development setup
- dependency versions
- build command
- packaging command
- signing process where applicable
- release process
- update manifest format
- update package format
- rollback strategy

Do not require end users to perform these development steps.

---

53. VERSIONING

Use separate versions for:

Application
yt-dlp
FFmpeg
Support components

For example:

App: 1.0.0
yt-dlp: X.Y.Z
FFmpeg: A.B.C

The update manager must understand which component changed.

---

54. UPDATE MANIFEST

Design a secure update manifest containing information such as:

application version
component name
component version
platform
architecture
download location
file size
SHA-256 checksum
signature
release notes
minimum application version

Never trust an update merely because the HTTP request succeeded.

Verify the package cryptographically before installation.

---

55. ATOMIC UPDATE

Never overwrite the working component directly while it is in use.

Use:

download
 ↓
temporary location
 ↓
verify
 ↓
prepare new version
 ↓
backup old version
 ↓
atomic replacement
 ↓
health check

If anything fails:

rollback

---

56. LEGAL/USAGE NOTICE

Include a concise notice that users are responsible for complying with applicable copyright laws and the terms governing content they access.

Do not implement DRM circumvention or bypass authentication/access controls.

Use yt-dlp's normal supported behavior.

---

57. FINAL DEVELOPMENT INSTRUCTION

Do not stop after generating the initial UI.

Actually implement the complete application.

The coding agent must:

1. Inspect the environment.
2. Determine the correct platform architecture.
3. Create the project.
4. Implement the UI.
5. Integrate bundled Python.
6. Integrate bundled yt-dlp.
7. Integrate all required yt-dlp support components.
8. Integrate bundled FFmpeg/FFprobe.
9. Implement metadata extraction.
10. Implement dynamic format discovery.
11. Implement format selection.
12. Implement downloading.
13. Implement progress.
14. Implement cancellation.
15. Implement local storage.
16. Implement error handling.
17. Implement offline startup.
18. Implement component health checks.
19. Implement the update manager.
20. Implement secure update verification.
21. Implement rollback.
22. Add automated tests.
23. Build the final application.
24. Test it on a clean environment.
25. Perform a network audit.
26. Fix every discovered issue.
27. Only then consider the application complete.

Do not create fake buttons.

Do not create placeholder download functionality.

Do not simulate yt-dlp.

Do not hard-code fake formats.

Do not claim a component is bundled if it is actually downloaded at runtime.

The finished application must genuinely perform the complete workflow.
