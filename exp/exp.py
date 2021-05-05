import os
import asyncio
import datetime
import logging
import discord
from redbot.core import commands, checks, Config
log=logging.getLogger("red.eunsahcogs.exp")


class Exp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=164900704526401545001, force_registration=True)
        default_user = {
            "name":"我的角色",
            "level" : 0,
            "exp" : 0,
            "previous_date": 0.0,
            "daily_velocity": 0.0,
            "char_select":{}
        }
        self.config.register_user(**default_user)


    @commands.command()
    async def return_some_data(self, ctx):
        await ctx.send(await self.config.foo())