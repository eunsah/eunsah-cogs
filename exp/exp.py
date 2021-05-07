import os
import asyncio
import datetime
import logging
import discord
import json
import time
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
            'previous_date' : datetime.datetime.timestamp(datetime.datetime.strptime('1900/01/01','%Y/%m/%d')),
            'daily_velocity' : 0.0,
            'char_select' : {}
        }
        self.config.register_user(**default_user)

    async def __levelexp_verification(self, user, level = None, exp = None) -> None:
        '''
        Verify level, exp and sets level, exp, raw
        parameters : user, level, exp
        '''
        if level is None:
            level = await self.config.user(user).level()
        if exp is None:
            exp = await self.config.user(user).exp()
        try:
            level = int(level)
            if level < 0 or level > MAX_LEVEL:
                # level verify
                raise ValueError
            level_exp = self.levelchart[str(level)]
            if '.' in str(exp):
                exp = float(exp)
                exp = round(level_exp*(exp/100))
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
        await self.config.user(user).level.set(int(level))
        await self.config.user(user).exp.set(int(exp))
        await self.config.user(user).raw.set(int(raw))

    async def _exp_embed(self, user, title) -> discord.Embed:
        name = await self.config.user(user).name()
        level = await self.config.user(user).level()
        exp = await self.config.user(user).exp()
        previous_date = await self.config.user(user).previous_date()
        daily_velocity = await self.config.user(user).daily_velocity()

        top_exp = self.levelchart[str(level)]

        e = discord.Embed(
            title = title,
            color = user.color
        )
        e.add_field(name="名稱", value=name, inline=True)
        e.add_field(name="等級", value=level, inline=True)
        e.add_field(name="經驗值", value=f'{exp:,} ({round((exp/top_exp)*100, 2):.2f}%)', inline=False)
        e.add_field(name="經驗成長日平均", value=f'{round(daily_velocity):,}', inline=False)
        e.set_footer(text='更新日期: ' + datetime.datetime.fromtimestamp(previous_date).strftime('%Y/%m/%d'))
        return e

    async def _remove_after_seconds(self, ctx, second):
        await time.sleep(second)
        ctx.message.clear_reactions()
        ctx.message.delete()

    @commands.command()
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    async def expinfo(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author
        await ctx.send(embed=await self._exp_embed(user=user, title = '玩家資料'))
        await self._remove_after_seconds(5)

    @commands.command(name = 'exp', aliases = ['e'])
    @commands.bot_has_permissions(add_reactions=True)
    async def _update_exp(self, ctx, *argv):
        '''
            [p]exp {等級} {經驗值 || 經驗值%}
            用於更新經驗值
        '''
        if len(argv) != 2:
            # argv check
            await ctx.send(f'參數不足')
            return

        level = argv[0]
        raw = await self.config.user(ctx.author).raw()
        previous_date_datetime = datetime.datetime.fromtimestamp(await self.config.user(ctx.author).previous_date())
        name = await self.config.user(ctx.author).name()
        if name == '角色':
            await self.config.user(ctx.author).name.set(ctx.author.name)

        await self._levelexp_verification(ctx.author, level=argv[0], exp=argv[1].strip('%'))

        await self.config.user(ctx.author).previous_date.set(datetime.datetime.timestamp(datetime.datetime.now()))

        daily_velocity = await self.config.user(ctx.author).daily_velocity()
        raw_diff = await self.config.user(ctx.author).raw() - raw
        raw_diff_percentage = round((raw_diff / self.levelchart[str(level)])*100, 2)

        if previous_date_datetime != datetime.datetime.timestamp(datetime.datetime.strptime('1900/01/01','%Y/%m/%d')):
            date_diff_timedelta = datetime.datetime.fromtimestamp(await self.config.user(ctx.author).previous_date()) - previous_date_datetime
            avg_exp = round(raw_diff/(date_diff_timedelta.total_seconds()/86400)) # 86400 is the total seconds in a day
            await self.config.user(ctx.author).daily_velocity.set(round(((avg_exp+daily_velocity)/2), 2))
        else:
            avg_exp = 0

        e = await self._exp_embed(user=ctx.author, title='經驗值更新')
        e.add_field(name="經驗成長日平均 (更新)", value=f'{avg_exp:,}', inline=True)
        e.add_field(name="總經驗成長幅", value=f'{raw_diff:,} ({raw_diff_percentage:,.2f}%)', inline=True)
        await ctx.tick()
        await ctx.send(embed=e)
        await self._remove_after_seconds(5)


    @checks.is_owner()
    @commands.group()
    async def expset(self, ctx):
        pass

    @checks.is_owner()
    @expset.command()
    async def init(self, ctx, name='角色', level=0, exp=0, date=datetime.datetime.now().strftime('%Y/%m/%d'), user: discord.User = None):
        if user is None:
            user = ctx.author
        await self._levelexp_verification(user, level=level, exp=exp)
        await self.config.user(user).name.set(name)
        previous_date = datetime.datetime.strptime(date, '%Y/%m/%d')
        await self.config.user(user).previous_date.set(datetime.datetime.timestamp(previous_date))
        await ctx.tick()
        await self._remove_after_seconds(5)

    @expset.command()
    async def name(self, ctx, value):
        await self.config.user(ctx.author).name.set(value)
        # await ctx.send(f'已變更名稱為：{value}')
        await ctx.tick()
        await self._remove_after_seconds(5)

    @checks.is_owner()
    @expset.command()
    async def _name(self, ctx, value, user: discord.User = None):
        if user is None:
            user = ctx.author
        await self.config.user(user).name.set(value)
        await ctx.tick()
        await self._remove_after_seconds(5)

    @checks.is_owner()
    @expset.command()
    async def _level(self, ctx, value, user: discord.User = None):
        if user is None:
            user = ctx.author
        await self._levelexp_verification(user, level=value)
        await ctx.tick()
        await self._remove_after_seconds(5)

    @checks.is_owner()
    @expset.command()
    async def _exp(self, ctx, value, user: discord.User = None):
        if user is None:
            user = ctx.author
        await self._levelexp_verification(user, exp=value)
        await ctx.tick()
        await self._remove_after_seconds(5)

    @checks.is_owner()
    @expset.command()
    async def _date(self, ctx, value, user: discord.User = None):
        '''
        date format = 2020/03/14
        '''
        if user is None:
            user = ctx.author
        await self.config.user(user).previous_date.set(datetime.datetime.timestamp(datetime.datetime.strptime(value, '%Y/%m/%d')))
        await ctx.tick()
        await self._remove_after_seconds(5)

    @checks.is_owner()
    @expset.command()
    async def _average(self, ctx, value, user: discord.User = None):
        if user is None:
            user = ctx.author
        await self.config.user(user).daily_velocity.set(int(value))
        await ctx.tick()
        await self._remove_after_seconds(5)

