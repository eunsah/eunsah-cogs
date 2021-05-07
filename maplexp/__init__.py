import asyncio
from redbot.core.bot import Red

from .maplexp import Maplexp

async def setup(bot):
    this = Maplexp(bot)
    bot.add_cog(this)