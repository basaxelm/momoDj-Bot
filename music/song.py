import discord
from dataclasses import dataclass
from typing import Optional

@dataclass
class Song:
    title: str
    webpage_url: str
    stream_url: str
    duration: int  # in seconds
    thumbnail: Optional[str] = None
    requester: Optional[discord.Member] = None
    is_live: bool = False

    @property
    def formatted_duration(self) -> str:
        if self.is_live:
            return "🔴 EN VIVO"
        if not self.duration or self.duration <= 0:
            return "Desconocida"
        
        minutes, seconds = divmod(int(self.duration), 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def to_embed(self, title_prefix: str = "🎶 Reproduciendo ahora") -> discord.Embed:
        embed = discord.Embed(
            title=title_prefix,
            description=f"[{self.title}]({self.webpage_url})",
            color=discord.Color.blurple()
        )
        embed.add_field(name="⏱️ Duración", value=self.formatted_duration, inline=True)
        if self.requester:
            embed.add_field(name="👤 Pedido por", value=self.requester.mention, inline=True)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        embed.set_footer(text="momoDj • Control de música", icon_url="https://cdn.discordapp.com/emojis/853304403759398932.webp?size=96")
        return embed
