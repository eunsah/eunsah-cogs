import os
import asyncio
import datetime
import logging
import discord
import json
from redbot.core import commands, checks, Config
log = logging.getLogger('red.eunsahcogs.exp')
MAX_LEVEL = 275
folder = 'leveling'
level_json = 'exp_'+str(MAX_LEVEL)+'.json'
dir_path = os.path.dirname(os.path.realpath(__file__))

class Exp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(os.path.join(dir_path, folder, level_json)) as j:
            self.levelchart = json.load(j)
        self.config = Config.get_conf(self, identifier=164900704526401545001,  force_registration=True)
        default_user = {
            'name':'角色',
            'level' : 0,
            'exp' : 0,
            'raw' : 0,
            'previous_date' : datetime.datetime.timestamp(datetime.datetime.now()),
            'daily_velocity' : 0.0,
            'char_select' : {}
        }
        self.config.register_user(**default_user)

    async def levelexp_verification(self, ctx, level, exp):
        '''
        Verify level, exp and sets level, exp, raw
        parameters : ctx, level, exp
        '''
        try:
            level = int(level)
            if level < 0 or level > MAX_LEVEL:
                # level verify
                raise ValueError
            level_exp = self.levelchart[str(level)]
            if '.' in exp:
                exp = float(exp)
                exp = round((level_exp*exp)/100)
            else:
                exp = int(exp)
        except ValueError:
            await ctx.send('Error when converting level and exp')
            return

        raw = 0
        for key in self.levelchart:
            raw += self.levelchart[key]
            if int(key) == level:
                break
        raw += exp

        await self.config.user(ctx.author).level.set(int(level))
        await self.config.user(ctx.author).exp.set(int(exp))
        await self.config.user(ctx.author).raw.set(int(raw))

    async def embedout(self, ctx) -> discord.Embed:
        name = await self.config.user(ctx.author).name()
        level = await self.config.user(ctx.author).level()
        exp = await self.config.user(ctx.author).exp()
        previous_date = await self.config.user(ctx.author).previous_date()
        daily_velocity = await self.config.user(ctx.author).daily_velocity()

        e = discord.Embed(
            title = 'Character Info',
            description = 'Last update: ' + datetime.datetime.fromtimestamp(previous_date).strftime('%Y/%m/%d'),
            color = ctx.author.color
        )
        e.add_field(name="Name", value=name, inline=True)
        e.add_field(name="Level", value=level, inline=True)
        e.add_field(name="Exp", value=exp, inline=False)
        e.add_field(name="Average Daily Exp (Total)", value=str(round(daily_velocity))+' exp per day', inline=False)

        return e

    @checks.is_owner()
    @commands.command()
    async def msinfo(self,ctx):
        await ctx.send(embed=await self.embedout(ctx))

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

        level = argv[0]
        raw = await self.config.user(ctx.author).raw()
        previous_date_datetime = datetime.datetime.fromtimestamp(await self.config.user(ctx.author).previous_date())

        await self.levelexp_verification(ctx, level=argv[0], exp=argv[1])

        await self.config.user(ctx.author).previous_date.set(datetime.datetime.timestamp(datetime.datetime.now()))

        raw_diff = await self.config.user(ctx.author).raw() - raw
        date_diff_timedelta = datetime.datetime.fromtimestamp(await self.config.user(ctx.author).previous_date()) - previous_date_datetime

        raw_diff_percentage = round((raw_diff / self.levelchart[str(level)])*100, 2)
        avg_exp = round(raw_diff/(date_diff_timedelta.total_seconds()/86400), 2) # 86400 is the total seconds in a day

        e = await self.embedout()
        e.add_field(name="Average Daily Exp (Update)", value=avg_exp, inline=True)
        e.add_field(name="Total Exp Growth", value=str(raw_diff) + ' (' + str(raw_diff_percentage) + '%)', inline=True)

    @checks.is_owner()
    @commands.group()
    async def expset(self, ctx):
        pass

    @checks.is_owner()
    @expset.command()
    async def init(self, ctx, name='角色', level=0, exp=0, date=datetime.datetime.now().strftime('%Y/%m/%d')):

        await self.levelexp_verification(ctx, level=level, exp=exp)
        await self.config.user(ctx.author).name.set(name)
        previous_date = datetime.datetime.strptime(date, '%Y/%m/%d')
        await self.config.user(ctx.author).previous_date.set(datetime.datetime.timestamp(previous_date))

        await ctx.send(f'user value has been initialized.')

