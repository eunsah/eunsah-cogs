import asyncio
from redbot.core.bot import Red

from .mapletcp import Mapletcp

async def setup(bot):
    this = Mapletcp(bot)
    bot.add_cog(this)