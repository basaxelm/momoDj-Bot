import os
import shutil
import logging
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("momoDj")

# Discord Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "mm").strip()

# YouTube Cookies Path
cookies_env = os.getenv("YOUTUBE_COOKIES_PATH", "config/cookies.txt").strip()
cookies_candidate = Path(cookies_env)
if not cookies_candidate.is_absolute():
    cookies_candidate = BASE_DIR / cookies_candidate
YOUTUBE_COOKIES_PATH = str(cookies_candidate) if cookies_candidate.exists() else None

# FFmpeg Binary Resolution
ffmpeg_env = os.getenv("FFMPEG_PATH", "").strip()
FFMPEG_PATH = None
if ffmpeg_env and Path(ffmpeg_env).exists():
    FFMPEG_PATH = ffmpeg_env
elif shutil.which("ffmpeg"):
    FFMPEG_PATH = shutil.which("ffmpeg")
else:
    # Common winget location on Windows
    winget_ffmpeg = Path(os.path.expanduser("~")) / "AppData" / "Local" / "Microsoft" / "WinGet" / "Links" / "ffmpeg.exe"
    if winget_ffmpeg.exists():
        FFMPEG_PATH = str(winget_ffmpeg)

# Spotify Credentials (Optional)
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()
SPOTIFY_ENABLED = bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)

# Inactivity settings
INACTIVITY_DISCONNECT_SECONDS = int(os.getenv("INACTIVITY_DISCONNECT_SECONDS", "30"))

# Discord Opus loader for voice streaming
def ensure_opus():
    import discord.opus
    if not discord.opus.is_loaded():
        candidates = [
            "libopus-0.dll",
            "opus.dll",
            r"C:\msys64\ucrt64\bin\libopus-0.dll",
        ]
        for candidate in candidates:
            try:
                discord.opus.load_opus(candidate)
                if discord.opus.is_loaded():
                    logger.info(f"Loaded Opus library from: {candidate}")
                    break
            except Exception:
                continue
        if not discord.opus.is_loaded():
            logger.warning("Could not load Opus library. Voice playback might fail.")

ensure_opus()
