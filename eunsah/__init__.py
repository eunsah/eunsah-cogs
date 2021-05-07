import asyncio
from redbot.core.bot import Red

from .eunsah import Eunsah

async def setup(bot):
    this = Eunsah(bot)
    bot.add_cog(this)