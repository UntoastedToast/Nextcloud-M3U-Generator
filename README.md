# Nextcloud M3U Playlist Generator

A Python script to create M3U playlists from Nextcloud shared folders containing video files. This tool allows you to generate playlists that work with video players like VLC, making it easy to stream your videos directly from Nextcloud.

## Features

- 🎬 Automatic detection of video files in Nextcloud shared folders
- 📋 Generates M3U playlists with direct streaming links
- 🎨 Interactive terminal UI with color-coded output
- 🌐 Supports both automatic (using Playwright) and manual HTML parsing
- 🔍 Debug mode with detailed logging
- 📁 Support for subfolder paths within shared folders

## Requirements

- Python 3.6+
- Optional: Playwright (for automatic HTML fetching)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/nextcloud-playlist.git
cd nextcloud-playlist
```

2. Install the required dependencies:
```bash
pip install playwright
python -m playwright install  # Only needed for automatic HTML fetching
```

## Usage

Run the script:
```bash
python nextcloud_m3u_generator.py
```

The script will guide you through:
1. Entering your Nextcloud share URL
2. Choosing between automatic or manual HTML input
3. Generating the M3U playlist

### Manual Mode
If you don't want to use automatic HTML fetching, you can:
- Paste HTML content directly
- Load HTML from a file
- Enter video filenames manually

## Generated Playlist

The script creates an M3U playlist file containing direct streaming links to your videos. This playlist can be opened in media players like VLC.

When using VLC:
1. Open the generated .m3u file
2. If prompted, enter credentials:
   - Username: [share token]
   - Password: [share password if any]
3. Optionally save credentials in VLC under Tools → Preferences → Input/Codecs

## Debug Features

The script creates a `debug_files` directory containing:
- HTML content for inspection
- List of found video files
- Other debug information

## License

MIT License - feel free to modify and share!
