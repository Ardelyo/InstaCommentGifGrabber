# Instagram GIF Grabber

A fast, enterprise-grade tool to extract GIF stickers from Instagram comments.

## Features

- **Parallel Downloads** - Grabs multiple files simultaneously
- **Smart Detection** - Automatically knows when all comments are loaded
- **Session Persistence** - Login once, use forever
- **Smooth Scrolling** - Natural interaction with Instagram's interface
- **Clean Output** - Downloads saved as organized ZIP archives

## Requirements

- Python 3.8+
- Windows/macOS/Linux

## Quick Start

### Windows
Double-click `setup_and_run.bat`

### Manual Setup
```bash
pip install -r requirements.txt
playwright install chromium
python grabber_browser.py
```

## Usage

1. Run the tool
2. Paste an Instagram post/reel URL
3. Login manually if prompted (first time only)
4. Wait for extraction to complete
5. Choose where to save your ZIP file

## Configuration

Edit these values in `grabber_browser.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_SCROLLS` | 150 | Maximum scroll attempts |
| `MAX_WORKERS` | 5 | Parallel download threads |
| `SCROLL_PAUSE` | 2.0 | Seconds between scrolls |

## File Structure

```
instagramgif/
├── grabber_browser.py   # Main application
├── requirements.txt     # Python dependencies
├── setup_and_run.bat    # Windows launcher
└── .gitignore           # Git ignore rules
```

## Credits

Created by [@ardel.yo](https://instagram.com/ardel.yo) (Instagram/TikTok) | [@ardelyo](https://github.com/ardelyo) (GitHub)

## License

MIT License - Use freely, credit appreciated.
