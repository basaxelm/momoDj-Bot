import asyncio
import json
import logging
import urllib.request
from typing import List, Optional, Tuple, Union
import discord
import yt_dlp

from config.settings import YOUTUBE_COOKIES_PATH, FFMPEG_PATH, logger
from music.song import Song

# FFmpeg streaming options
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# Base yt-dlp configuration
YTDL_BASE_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',  # Bind to ipv4 since ipv6 addresses often get ratelimited
    'js_runtimes': {'node': {}},
    'remote_components': ['ejs:github'],
}

if YOUTUBE_COOKIES_PATH:
    YTDL_BASE_OPTIONS['cookiefile'] = YOUTUBE_COOKIES_PATH
    logger.info(f"Using YouTube cookies from: {YOUTUBE_COOKIES_PATH}")


class AudioSourceExtractor:
    def __init__(self):
        self.ytdl = yt_dlp.YoutubeDL(YTDL_BASE_OPTIONS)

    @classmethod
    def create_ffmpeg_source(cls, stream_url: str) -> discord.AudioSource:
        """Creates a Discord FFmpeg audio source with the resolved binary path."""
        kwargs = dict(FFMPEG_OPTIONS)
        if FFMPEG_PATH:
            return discord.FFmpegPCMAudio(stream_url, executable=FFMPEG_PATH, **kwargs)
        return discord.FFmpegPCMAudio(stream_url, **kwargs)

    async def _resolve_spotify_oembed(self, url: str) -> Optional[str]:
        """Resolves Spotify track metadata via public oEmbed endpoint without API keys."""
        try:
            import requests

            def fetch():
                oembed_url = f"https://open.spotify.com/oembed?url={url}"
                headers = {'User-Agent': 'Mozilla/5.0'}
                resp = requests.get(oembed_url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    return resp.json().get("title")
                return None

            title = await asyncio.to_thread(fetch)
            return title
        except Exception as e:
            logger.warning(f"Error resolving Spotify oEmbed for {url}: {e}")
            return None

    async def extract_song(self, query: str, requester: Optional[discord.Member] = None) -> Union[Song, List[Song]]:
        """
        Extracts song metadata and stream URL from a search query or link.
        Supports YouTube URLs, text searches, and Spotify URLs via metadata resolution.
        """
        search_term = query.strip()

        # Check for Spotify links
        if "open.spotify.com" in search_term:
            spotify_title = await self._resolve_spotify_oembed(search_term)
            if spotify_title:
                logger.info(f"Resolved Spotify title: '{spotify_title}' - Searching on YouTube...")
                search_term = f"ytsearch:{spotify_title}"
            else:
                raise ValueError("No se pudo obtener la información de Spotify. Intenta buscar el nombre de la canción directamente.")

        # If not a direct URL, prepend ytsearch:
        if not search_term.startswith(("http://", "https://", "ytsearch:")):
            search_term = f"ytsearch:{search_term}"

        # Extract data asynchronously to prevent event loop blocking
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(
            None,
            lambda: self.ytdl.extract_info(search_term, download=False)
        )

        if not data:
            raise ValueError("No se encontraron resultados para la búsqueda.")

        # Handle search results / playlists
        if 'entries' in data:
            entries = [entry for entry in data['entries'] if entry is not None]
            if not entries:
                raise ValueError("No se encontraron canciones válidas.")
            
            # If it was a search, return only the top result
            if search_term.startswith("ytsearch:"):
                entry = entries[0]
            else:
                # Actual playlist
                songs = []
                for entry in entries:
                    stream_url = entry.get('url')
                    if stream_url:
                        songs.append(Song(
                            title=entry.get('title', 'Canción sin título'),
                            webpage_url=entry.get('webpage_url', entry.get('url')),
                            stream_url=stream_url,
                            duration=entry.get('duration', 0),
                            thumbnail=entry.get('thumbnail'),
                            requester=requester,
                            is_live=entry.get('is_live', False)
                        ))
                return songs
        else:
            entry = data

        stream_url = entry.get('url')
        if not stream_url:
            raise ValueError("No se pudo obtener el flujo de reproducción de audio.")

        return Song(
            title=entry.get('title', 'Canción sin título'),
            webpage_url=entry.get('webpage_url', search_term),
            stream_url=stream_url,
            duration=entry.get('duration', 0),
            thumbnail=entry.get('thumbnail'),
            requester=requester,
            is_live=entry.get('is_live', False)
        )
