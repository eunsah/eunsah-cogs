import os
import asyncio
import datetime
import logging
import discord
import json
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


    @checks.is_owner()
    @commands.group()
    async def exp(self, ctx):
        pass

    @checks.is_owner()
    @exp.command()
    async def info(self,ctx):
        name = self.config.user(ctx.author).name
        level = self.config.user(ctx.author).level
        exp = self.config.user(ctx.author).exp
        previous_date = self.config.user(ctx.author).previous_date

        e = discord.Embed(
            title = "Character Info",
            description = "Last update: "+str(previous_date),
            color = ctx.author.color
        )
        e.add_field(name="Name", value=name, inline=False)
        e.add_field(name="Exp", value=exp, inline=True)
        e.add_field(name="Level", value=level, inline=True)

        await ctx.send(e)