import asyncio
from redbot.core.bot import Red

from .exp import Exp

async def setup(bot):
    this = Exp(bot)
    await this.initialize()
    bot.add_cog(this)