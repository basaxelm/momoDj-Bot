import asyncio
from typing import Dict, Optional
import discord
from discord.ext import commands

from config.settings import logger, INACTIVITY_DISCONNECT_SECONDS

class InactivityMonitor:
    """Monitors voice channels for empty human participant state and schedules auto-disconnect after 30 seconds."""

    def __init__(self, bot: commands.Bot, get_player_func):
        self.bot = bot
        self.get_player = get_player_func
        self._disconnect_tasks: Dict[int, asyncio.Task] = {}

    def has_active_humans(self, channel: discord.VoiceChannel) -> bool:
        """Returns True if there is at least one non-bot member in the voice channel."""
        return any(not member.bot for member in channel.members)

    async def handle_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild
        vc = guild.voice_client

        # If bot is not connected to a voice channel in this guild, ignore
        if not vc or not vc.channel:
            self._cancel_task(guild.id)
            return

        bot_channel = vc.channel

        # Only care if the voice state update happened in the bot's channel
        if before.channel != bot_channel and after.channel != bot_channel:
            return

        humans = [m for m in bot_channel.members if not m.bot]

        if len(humans) == 0:
            # All humans left the channel
            if guild.id not in self._disconnect_tasks:
                logger.info(f"No human members in {bot_channel.name} ({guild.name}). Starting {INACTIVITY_DISCONNECT_SECONDS}s countdown...")
                self._disconnect_tasks[guild.id] = self.bot.loop.create_task(
                    self._auto_disconnect(guild, bot_channel)
                )
        else:
            # At least one human is in the channel
            if guild.id in self._disconnect_tasks:
                logger.info(f"Human member joined or active in {bot_channel.name} ({guild.name}). Canceling auto-disconnect.")
                self._cancel_task(guild.id)

    async def _auto_disconnect(self, guild: discord.Guild, channel: discord.VoiceChannel):
        try:
            await asyncio.sleep(INACTIVITY_DISCONNECT_SECONDS)
            
            # Re-verify after sleep
            vc = guild.voice_client
            if vc and vc.channel == channel:
                humans = [m for m in channel.members if not m.bot]
                if len(humans) == 0:
                    logger.info(f"Auto-disconnect timer expired for guild '{guild.name}'. Leaving channel.")
                    player = self.get_player(guild)
                    if player:
                        if player.text_channel:
                            embed = discord.Embed(
                                title="🚪 Desconexión por inactividad",
                                description=f"Me he desconectado automáticamente de **{channel.name}** porque pasaron 30 segundos sin participantes activos.",
                                color=discord.Color.orange()
                            )
                            try:
                                await player.text_channel.send(embed=embed)
                            except Exception:
                                pass
                        await player.stop()
                    else:
                        await vc.disconnect()
        except asyncio.CancelledError:
            logger.debug(f"Auto-disconnect task for guild '{guild.name}' was cancelled.")
        finally:
            self._disconnect_tasks.pop(guild.id, None)

    def _cancel_task(self, guild_id: int):
        task = self._disconnect_tasks.pop(guild_id, None)
        if task and not task.done():
            task.cancel()
