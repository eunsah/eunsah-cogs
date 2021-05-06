import os
import asyncio
import datetime
import logging
import discord
import json
from redbot.core import commands, checks, Config
log = logging.getLogger('red.eunsahcogs.exp')
MAX_LEVEL = 275
level_json = 'exp_'+str(MAX_LEVEL)+'.json'
dir_path = os.path.dirname(os.path.realpath(__file__))

class Exp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # with open(level_json) as j:
        #     self.levelchart = json.loads(j)
        self.config = Config.get_conf(self, identifier=164900704526401545001,  force_registration=True)
        default_user = {
            'name':'角色',
            'level' : 0,
            'exp' : 0,
            'previous_date' : datetime.datetime.timestamp(datetime.datetime.utcnow()),
            'daily_velocity' : 0.0,
            'char_select' : {}
        }
        self.config.register_user(**default_user)

    @checks.is_owner()
    @commands.command()
    async def msinfo(self,ctx):
        name = await self.config.user(ctx.author).name()
        level = await self.config.user(ctx.author).level()
        exp = await self.config.user(ctx.author).exp()
        previous_date = await self.config.user(ctx.author).previous_date()

        e = discord.Embed(
            title = 'Character Info',
            description = 'Last update: ' + datetime.datetime.fromtimestamp(previous_date).strftime('%Y/%m/%d'),
            color = ctx.author.color
        )
        e.add_field(name="Name", value=name, inline=False)
        e.add_field(name="Level", value=level, inline=True)
        e.add_field(name="Exp", value=exp, inline=True)

        await ctx.send(embed=e)

    @checks.is_owner()
    @commands.command()
    async def exp(self, ctx, *argv):
        '''
            [p]exp {level} {percentage || raw exp}
            Update exp
        '''
        if len(argv) != 2:
            # argv check
            await ctx.send(f'Not enough arguments')
            return
        level = int(argv[0])
        exp = argv[1]
        if level < 0 or level > MAX_LEVEL:
            # level verify
            await ctx.send(f'Invalid range for level')
        await ctx.send(type(exp))
        await ctx.send(os.path.dirname(os.path.realpath(__file__)))
)


    @checks.is_owner()
    @commands.group()
    async def expset(self, ctx):
        pass

    @checks.is_owner()
    @expset.command()
    async def init(self, ctx, name='角色', level=0, exp=0, date=datetime.datetime.utcnow().strftime('%Y/%m/%d')):

        previous_date = datetime.datetime.strptime(date, '%Y/%m/%d')
        await self.config.user(ctx.author).name.set(name)
        await self.config.user(ctx.author).level.set(level)
        await self.config.user(ctx.author).exp.set(exp)
        await self.config.user(ctx.author).previous_date.set(datetime.datetime.timestamp(previous_date))
        # await self.config.user(ctx.author).daily_velocity.set(default_user['daily_velocity'])

        await ctx.send(f'user value has been reseted.')

