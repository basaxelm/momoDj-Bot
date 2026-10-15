import discord
from discord.ext import commands
from typing import Dict, Optional

from config.settings import logger
from music.audio_source import AudioSourceExtractor, PlaylistResult
from music.player import GuildMusicPlayer
from music.song import Song


class MusicControlView(discord.ui.View):
    """Interactive Discord UI Buttons for controlling the music player."""

    def __init__(self, player: GuildMusicPlayer):
        super().__init__(timeout=180)
        self.player = player

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.voice or interaction.user.voice.channel != self.player.guild.voice_client.channel:
            await interaction.response.send_message("❌ Debes estar en el mismo canal de voz que momoDj para usar estos controles.", ephemeral=True)
            return False
        return True

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary, custom_id="btn_prev")
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player.queue.history:
            await interaction.response.send_message("ℹ️ No hay canciones previas en el historial.", ephemeral=True)
            return

        await interaction.response.send_message("⏮️ Volviendo a la canción anterior...", ephemeral=True)
        await self.player.play_previous()

    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.primary, custom_id="btn_pause_resume")
    async def pause_resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.player.is_paused:
            self.player.resume()
            await interaction.response.send_message("▶️ Reanudado.", ephemeral=True)
        elif self.player.is_playing:
            self.player.pause()
            await interaction.response.send_message("⏸️ Pausado.", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ No hay ninguna canción reproduciéndose.", ephemeral=True)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary, custom_id="btn_skip")
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player.is_playing and not self.player.is_paused:
            await interaction.response.send_message("ℹ️ No hay ninguna canción para saltar.", ephemeral=True)
            return

        self.player.skip()
        await interaction.response.send_message("⏭️ Canción saltada.", ephemeral=True)

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger, custom_id="btn_stop")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.player.stop()
        await interaction.response.send_message("⏹️ Música detenida y desconectado.", ephemeral=True)
        self.stop()


class MusicCommands(commands.Cog):
    """Cog que implementa los comandos de música con prefijo 'mm'."""

    def __init__(self, bot: commands.Bot, get_player_func, inactivity_monitor):
        self.bot = bot
        self.get_player = get_player_func
        self.inactivity_monitor = inactivity_monitor
        self.extractor = AudioSourceExtractor()

    async def _ensure_voice_connection(self, ctx: commands.Context) -> Optional[discord.VoiceClient]:
        """Validates conditions and connects the bot to the caller's voice channel."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ Debes estar conectado a un canal de voz para reproducir música.")
            return None

        channel = ctx.author.voice.channel

        # Validate that the voice channel has at least 1 active human member
        if not self.inactivity_monitor.has_active_humans(channel):
            await ctx.send("❌ Solo se puede activar el bot si hay al menos una persona activa en el canal de voz.")
            return None

        vc = ctx.guild.voice_client
        if vc and not vc.is_connected():
            logger.info(f"Conexión previa de voz en {ctx.guild.name} no está activa. Limpiando...")
            try:
                await vc.disconnect(force=True)
            except Exception:
                pass
            vc = None

        if vc:
            if vc.channel != channel:
                await vc.move_to(channel)
        else:
            vc = await channel.connect(reconnect=True, timeout=20.0)

        return vc

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx: commands.Context, *, query: str = None):
        """Reproduce una canción o playlist desde YouTube/Spotify o busca por nombre."""
        if not query:
            # If paused, resume
            player = self.get_player(ctx.guild)
            if player.is_paused:
                player.resume()
                await ctx.send("▶️ Reproducción reanudada.")
                return
            await ctx.send("❓ Uso: `mmplay <nombre de la canción o enlace>`")
            return

        vc = await self._ensure_voice_connection(ctx)
        if not vc:
            return

        player = self.get_player(ctx.guild)
        player.text_channel = ctx.channel

        loading_msg = await ctx.send("🔍 Buscando y procesando audio...")

        try:
            result = await self.extractor.extract_song(query, requester=ctx.author)

            # Asegurar que la conexión de voz sigue activa tras la búsqueda/extracción
            if not player.voice_client or not player.voice_client.is_connected():
                logger.warning(f"Conexión de voz perdida durante extracción en {ctx.guild.name}. Reconectando...")
                vc = await self._ensure_voice_connection(ctx)
                if not vc or not vc.is_connected():
                    await loading_msg.edit(content="❌ Se perdió la conexión con el canal de voz.")
                    return

            if isinstance(result, PlaylistResult):
                # Playlist
                player.queue.add_multiple(result.songs)
                description = f"Se agregaron **{len(result.songs)}** canciones a la cola."
                if result.skipped_count:
                    description += f"\n⚠️ Se omitieron **{result.skipped_count}** entradas que no se pudieron reproducir."
                embed = discord.Embed(
                    title="🎶 Lista de reproducción añadida",
                    description=description,
                    color=discord.Color.green()
                )
                await loading_msg.edit(content=None, embed=embed)

                if not player.is_playing and not player.is_paused:
                    await player.play_next()
            else:
                # Single song
                song = result
                if player.is_playing or player.is_paused:
                    player.queue.add(song)
                    position = len(player.queue.upcoming)
                    embed = discord.Embed(
                        title="➕ Añadido a la cola",
                        description=f"[{song.title}]({song.webpage_url})\n\n**Posición:** #{position} | **Duración:** {song.formatted_duration}",
                        color=discord.Color.blue()
                    )
                    if song.thumbnail:
                        embed.set_thumbnail(url=song.thumbnail)
                    await loading_msg.edit(content=None, embed=embed)
                else:
                    player.queue.add(song)
                    await loading_msg.delete()
                    await player.play_next()

        except Exception as e:
            logger.error(f"Error executing play command: {e}", exc_info=True)
            await loading_msg.edit(content=f"❌ Error al procesar la solicitud: {e}")

    @commands.command(name="pause")
    async def pause(self, ctx: commands.Context):
        """Pausa la reproducción actual."""
        player = self.get_player(ctx.guild)
        if player.pause():
            await ctx.send("⏸️ Reproducción pausada.")
        else:
            await ctx.send("ℹ️ No hay ninguna canción reproduciéndose o ya está pausada.")

    @commands.command(name="resume")
    async def resume(self, ctx: commands.Context):
        """Reanuda la reproducción pausada."""
        player = self.get_player(ctx.guild)
        if player.resume():
            await ctx.send("▶️ Reproducción reanudada.")
        else:
            await ctx.send("ℹ️ La reproducción no está pausada o no hay canciones activas.")

    @commands.command(name="skip", aliases=["next", "s"])
    async def skip(self, ctx: commands.Context):
        """Salta a la siguiente canción de la cola."""
        player = self.get_player(ctx.guild)
        if player.is_playing or player.is_paused:
            player.skip()
            await ctx.send("⏭️ Canción saltada a la siguiente.")
        else:
            await ctx.send("ℹ️ No hay ninguna canción para saltar.")

    @commands.command(name="prev", aliases=["previous", "anterior"])
    async def previous(self, ctx: commands.Context):
        """Regresa a la canción anterior en el historial."""
        player = self.get_player(ctx.guild)
        if not player.queue.history:
            await ctx.send("ℹ️ No hay canciones previas en el historial.")
            return

        await ctx.send("⏮️ Regresando a la canción anterior...")
        await player.play_previous()

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx: commands.Context):
        """Muestra las canciones actuales y pendientes en la cola."""
        player = self.get_player(ctx.guild)

        if player.queue.is_empty:
            await ctx.send("📭 La cola de música está vacía. Añade canciones con `mmplay <canción>`")
            return

        embed = discord.Embed(
            title="📜 Cola de Reproducción - momoDj",
            color=discord.Color.purple()
        )

        current = player.current
        if current:
            status = "⏸️ Pausado" if player.is_paused else "▶️ Sonando"
            embed.add_field(
                name="🎵 En curso",
                value=f"{status}: [{current.title}]({current.webpage_url}) (`{current.formatted_duration}`)\nPedido por: {current.requester.mention if current.requester else 'Desconocido'}",
                inline=False
            )

        upcoming = list(player.queue.upcoming)
        if upcoming:
            preview_items = upcoming[:10]
            lines = []
            for i, song in enumerate(preview_items, start=1):
                lines.append(f"`{i}.` [{song.title}]({song.webpage_url}) (`{song.formatted_duration}`) - {song.requester.mention if song.requester else 'Desconocido'}")
            
            field_val = "\n".join(lines)
            if len(upcoming) > 10:
                field_val += f"\n*... y {len(upcoming) - 10} canción(es) más.*"
            embed.add_field(name="⏳ Próximas canciones", value=field_val, inline=False)
        else:
            embed.add_field(name="⏳ Próximas canciones", value="No hay más canciones en espera.", inline=False)

        # History summary
        if player.queue.history:
            last_song = player.queue.history[-1]
            embed.add_field(name="⏮️ Anteriormente", value=f"[{last_song.title}]({last_song.webpage_url})", inline=False)

        embed.set_footer(text=f"Total en cola: {player.queue.total_count} canción(es)")
        await ctx.send(embed=embed)

    @commands.command(name="nowplaying", aliases=["np"])
    async def now_playing(self, ctx: commands.Context):
        """Muestra la canción actual y controles interactivos por botones."""
        player = self.get_player(ctx.guild)
        current = player.current

        if not current:
            await ctx.send("ℹ️ No hay ninguna canción reproduciéndose actualmente.")
            return

        embed = current.to_embed(title_prefix="🎶 En Reproducción")
        view = MusicControlView(player)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="stop", aliases=["leave", "disconnect"])
    async def stop(self, ctx: commands.Context):
        """Detiene la música, limpia la cola y desconecta al bot."""
        player = self.get_player(ctx.guild)
        await player.stop()
        await ctx.send("⏹️ Reproducción detenida, cola limpiada y bot desconectado.")

    @commands.command(name="help", aliases=["help_mm", "mmhelp", "mhelp", "ayuda", "comandos"])
    async def help_command(self, ctx: commands.Context):
        """Muestra la lista de comandos disponibles."""
        embed = discord.Embed(
            title="🎧 Comandos de momoDj",
            description="Todos los comandos comienzan con el prefijo **`mm`** para no interferir con otros bots:",
            color=discord.Color.gold()
        )
        embed.add_field(name="`mmplay <canción o link>`", value="Reproduce o añade a la cola desde YouTube, Spotify o por búsqueda.", inline=False)
        embed.add_field(name="`mmpause`", value="Pausa la reproducción actual.", inline=True)
        embed.add_field(name="`mmresume`", value="Reanuda la reproducción pausada.", inline=True)
        embed.add_field(name="`mmskip`", value="Salta a la siguiente canción en la cola.", inline=True)
        embed.add_field(name="`mmprev`", value="Vuelve a reproducir la canción anterior del historial.", inline=True)
        embed.add_field(name="`mmqueue`", value="Muestra la lista de canciones en la cola.", inline=True)
        embed.add_field(name="`mmnowplaying` / `mmnp`", value="Muestra la canción actual con botones de control.", inline=True)
        embed.add_field(name="`mmstop` / `mmleave`", value="Detiene la música y desconecta al bot.", inline=True)
        embed.add_field(name="`mmhelp` / `mmayuda`", value="Muestra la lista de comandos disponibles.", inline=True)
        embed.set_footer(text="momoDj • Desconexión automática a los 30s sin participantes.")
        await ctx.send(embed=embed)
