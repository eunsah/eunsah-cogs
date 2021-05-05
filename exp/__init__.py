import asyncio
from redbot.core.bot import Red

from .exp import Exp

async def setup(bot):
    this = Exp(bot)
    bot.add_cog(this)