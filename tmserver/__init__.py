import asyncio
from redbot.core.bot import Red

from .tmserver import Tmserver

async def setup(bot):
    this = Tmserver(bot)
    bot.add_cog(this)