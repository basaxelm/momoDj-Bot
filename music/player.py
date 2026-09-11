import asyncio
import logging
from typing import Optional
import discord
from discord.ext import commands

from config.settings import logger
from music.audio_source import AudioSourceExtractor
from music.queue import MusicQueue
from music.song import Song


class GuildMusicPlayer:
    """Manages audio playback, queue progression, and voice connection for a single Discord guild."""

    def __init__(self, bot: commands.Bot, guild: discord.Guild):
        self.bot = bot
        self.guild = guild
        self.queue = MusicQueue()
        self.text_channel: Optional[discord.TextChannel] = None
        self._lock = asyncio.Lock()

    @property
    def voice_client(self) -> Optional[discord.VoiceClient]:
        return self.guild.voice_client

    @property
    def is_playing(self) -> bool:
        vc = self.voice_client
        return vc is not None and vc.is_playing()

    @property
    def is_paused(self) -> bool:
        vc = self.voice_client
        return vc is not None and vc.is_paused()

    @property
    def current(self) -> Optional[Song]:
        return self.queue.current

    async def play_song(self, song: Song) -> None:
        """Plays the specified song on the guild's voice client."""
        vc = self.voice_client
        if not vc or not vc.is_connected():
            logger.warning(f"Attempted to play song in {self.guild.name} but not connected to voice.")
            if self.text_channel:
                await self.text_channel.send(f"⚠️ No estoy conectado al canal de voz para reproducir **{song.title}**.")
            return

        async with self._lock:
            # Stop any currently playing audio cleanly without triggering next prematurely
            if vc.is_playing() or vc.is_paused():
                vc.stop()

            try:
                source = AudioSourceExtractor.create_ffmpeg_source(song.stream_url)
                vc.play(source, after=lambda error: self._after_playback(error))
                logger.info(f"Started playing '{song.title}' in guild '{self.guild.name}'")

                if self.text_channel:
                    embed = song.to_embed(title_prefix="▶️ Reproduciendo ahora")
                    await self.text_channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Error creating audio source or playing in guild '{self.guild.name}': {e}", exc_info=True)
                if self.text_channel:
                    await self.text_channel.send(f"❌ Error al reproducir **{song.title}**: {e}")
                # Try next song if this one failed
                await self.play_next()

    def _after_playback(self, error: Optional[Exception]) -> None:
        """Callback executed by discord.py voice client in a worker thread when playback stops."""
        if error:
            logger.error(f"Playback error in guild '{self.guild.name}': {error}")
        
        # Schedule the coroutine to advance the queue asynchronously without blocking the audio worker thread
        fut = asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop)
        def _check_result(f):
            try:
                f.result()
            except Exception as e:
                logger.error(f"Error advancing queue in _after_playback: {e}")
        fut.add_done_callback(_check_result)

    async def play_next(self) -> Optional[Song]:
        """Advances to the next song in the queue and plays it."""
        next_song = self.queue.get_next()
        if next_song:
            await self.play_song(next_song)
            return next_song
        else:
            logger.info(f"Queue finished in guild '{self.guild.name}'")
            if self.text_channel:
                embed = discord.Embed(
                    title="⏹️ Cola finalizada",
                    description="No hay más canciones en la cola. Añade más con `mmplay <canción>`",
                    color=discord.Color.light_grey()
                )
                await self.text_channel.send(embed=embed)
            return None

    async def play_previous(self) -> Optional[Song]:
        """Rewinds to the previously played song from the history stack."""
        prev_song = self.queue.get_previous()
        if prev_song:
            await self.play_song(prev_song)
            return prev_song
        return None

    def pause(self) -> bool:
        vc = self.voice_client
        if vc and vc.is_playing():
            vc.pause()
            return True
        return False

    def resume(self) -> bool:
        vc = self.voice_client
        if vc and vc.is_paused():
            vc.resume()
            return True
        return False

    def skip(self) -> bool:
        """Stops the current track, which automatically triggers _after_playback to advance to next."""
        vc = self.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            return True
        return False

    async def stop(self) -> None:
        """Stops playback, clears queue and history, and disconnects."""
        self.queue.clear()
        vc = self.voice_client
        if vc:
            if vc.is_playing() or vc.is_paused():
                vc.stop()
            if vc.is_connected():
                await vc.disconnect()
        logger.info(f"Stopped and disconnected from guild '{self.guild.name}'")
