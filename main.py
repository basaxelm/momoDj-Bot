import asyncio
import sys
from typing import Dict
import discord
from discord.ext import commands

from config.settings import DISCORD_TOKEN, COMMAND_PREFIX, logger, YOUTUBE_COOKIES_PATH, FFMPEG_PATH
from music.player import GuildMusicPlayer
from utils.inactivity import InactivityMonitor
from cogs.music_commands import MusicCommands


# Configure bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

# Bot initialization with 'mm' prefix (supports 'mmplay', 'mm play', etc.)
bot = commands.Bot(
    command_prefix=[COMMAND_PREFIX, f"{COMMAND_PREFIX} ", COMMAND_PREFIX.upper(), f"{COMMAND_PREFIX.upper()} "],
    intents=intents,
    help_command=None
)

# Active guild players store
players: Dict[int, GuildMusicPlayer] = {}

def get_player(guild: discord.Guild) -> GuildMusicPlayer:
    """Returns or instantiates a GuildMusicPlayer for the given guild."""
    if guild.id not in players:
        players[guild.id] = GuildMusicPlayer(bot, guild)
    return players[guild.id]

# Inactivity Monitor
inactivity_monitor = InactivityMonitor(bot, get_player)


@bot.event
async def on_ready():
    logger.info("=" * 50)
    logger.info(f"🎶 momoDj conectado exitosamente como: {bot.user.name}#{bot.user.discriminator} (ID: {bot.user.id})")
    logger.info(f"Servidores conectados: {len(bot.guilds)}")
    for g in bot.guilds:
        logger.info(f" - {g.name} (ID: {g.id})")
    logger.info(f"Prefijo configurado: '{COMMAND_PREFIX}' (ejemplo: {COMMAND_PREFIX}play)")
    logger.info(f"FFmpeg path: {FFMPEG_PATH if FFMPEG_PATH else 'Sistema default'}")
    logger.info(f"Cookies de YouTube: {'Detectadas' if YOUTUBE_COOKIES_PATH else 'No configuradas'}")
    logger.info("=" * 50)

    # Set status activity
    activity = discord.Activity(type=discord.ActivityType.listening, name=f"{COMMAND_PREFIX}play | momoDj")
    await bot.change_presence(status=discord.Status.online, activity=activity)


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    """Monitors voice state changes to handle 30s auto-disconnect on empty channels."""
    await inactivity_monitor.handle_voice_state_update(member, before, after)


@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    """Global error handler for cleaner chat experience."""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands to avoid chat spam
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"⚠️ Parámetro faltante: `{error.param.name}`. Usa `{COMMAND_PREFIX}help` para ver el uso.")
    elif isinstance(error, commands.CommandInvokeError):
        logger.error(f"Error invocando comando '{ctx.command}': {error.original}", exc_info=True)
        await ctx.send(f"❌ Ocurrió un error al ejecutar el comando: {error.original}")
    else:
        logger.error(f"Error en comando: {error}", exc_info=True)
        await ctx.send(f"❌ Error inesperado: {error}")


async def main():
    if not DISCORD_TOKEN:
        logger.error("No se encontró DISCORD_TOKEN en la configuración ni en el archivo .env. Abortando.")
        sys.exit(1)

    async with bot:
        await bot.add_cog(MusicCommands(bot, get_player, inactivity_monitor))
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario.")
