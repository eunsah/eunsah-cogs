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

    async def embedout(self, target, title) -> discord.Embed:
        name = await self.config.user(target).name()
        level = await self.config.user(target).level()
        exp = await self.config.user(target).exp()
        previous_date = await self.config.user(target).previous_date()
        daily_velocity = await self.config.user(target).daily_velocity()

        e = discord.Embed(
            title = title,
            description = 'Last update: ' + datetime.datetime.fromtimestamp(previous_date).strftime('%Y/%m/%d'),
            color = ctx.author.color
        )
        e.add_field(name="Name", value=name, inline=True)
        e.add_field(name="Level", value=level, inline=True)
        e.add_field(name="Exp", value=f'{exp:,}', inline=False)
        e.add_field(name="Average Daily Exp (Total)", value=f'{round(daily_velocity,2):,.2f} exp per day', inline=False)
        return e

    @commands.command()
    async def msinfo(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author
        await ctx.send(embed=await self.embedout(target=user, title = 'Charactor Info'))

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

        daily_velocity = await self.config.user(ctx.author).daily_velocity()
        await self.config.user(ctx.author).daily_velocity.set(round(((avg_exp+daily_velocity)/2), 2))

        e = await self.embedout(target=ctx.author, title='Character Update')
        e.add_field(name="Average Daily Exp (Update)", value=f'{avg_exp:,}', inline=True)
        # e.add_field(name="Total Exp Growth", value=str(raw_diff) + ' (' + str(raw_diff_percentage) + '%)', inline=True)
        e.add_field(name="Total Exp Growth", value=f'{raw_diff:,} ({raw_diff_percentage:,.2f}%)', inline=True)
        await ctx.send(embed=e)

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

    @expset.command()
    async def name(self, ctx, value):
        await self.config.user(ctx.author).name.set(value)
        await ctx.send(f'Name set to {value}')

    @expset.command()
    async def _name(self, ctx, value, user: discord.User = None):
        if user is None:
            user = ctx.author
        await self.config.user(user).name.set(value)
        await ctx.send('Done')

    @checks.is_owner()
    @expset.command()
    async def _level(self, ctx, value, user: discord.User = None):
        if user is None:
            user = ctx.author
        exp = await self.config.user(user).exp()
        self.levelexp_verification(ctx, level=value, exp=exp)
        await ctx.send('Done')

    @checks.is_owner()
    @expset.command()
    async def _exp(self, ctx, value, user: discord.User = None):
        if user is None:
            user = ctx.author
        level = await self.config.user(user).level()
        self.levelexp_verification(ctx, level=level, exp=value)
        await ctx.send('Done')

    @checks.is_owner()
    @expset.command()
    async def _date(self, ctx, value, user: discord.User = None):
        if user is None:
            user = ctx.author
        await self.config.user(user).previous_date.set(datetime.datetime.timestamp(datetime.datetime.strptime(value, '%Y/%m/%d')))
        await ctx.send('Done')

    @checks.is_owner()
    @expset.command()
    async def _average(self, ctx, value, user: discord.User = None):
        if user is None:
            user = ctx.author
        await self.config.user(user).daily_velocity.set(int(value))
        await ctx.send('Done')

