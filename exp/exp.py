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
    '''Exp 紀錄楓之谷經驗值'''
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

    async def _levelexp_verification(self, user, level = None, exp = None) -> None:
        '''Verify level, exp and sets level, exp, raw
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
        '''Process Embeds
        '''
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
        time.sleep(second)
        await ctx.message.clear_reactions()
        await ctx.message.delete()

    @commands.command(name='expinfo', aliases=['einfo'])
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    async def _show_exp(self, ctx, user: discord.User = None):
        '''顯示目前資訊
        [p]expinfo {@使用者}
        '''
        if user is None:
            user = ctx.author
        await ctx.send(embed=await self._exp_embed(user=user, title = '玩家資料'))

    @commands.command(name='exp', aliases=['e'])
    @commands.bot_has_permissions(add_reactions=True)
    async def _update_exp(self, ctx, *argv):
        '''用於更新經驗值
        [p]exp [等級] [經驗值]
        經驗值可以為百分比(12.42%)或是整數(34593402)
        可以用[p]help Exp 查看更多
        '''
        if len(argv) != 2:
            # argv check
            await ctx.send_help()
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
        # await self._remove_after_seconds(ctx, 5)

    @commands.bot_has_permissions(add_reactions=True)
    @commands.group(name='expset')
    async def commands_expset(self, ctx):
        '''Exp相關各種設定
        '''
        pass

    @commands_expset.command(name='init')
    async def expset_init(self, ctx, name='角色', level=0, exp=0, date=datetime.datetime.now().strftime('%Y/%m/%d'), user: discord.User = None):
        '''完全設定使用者資料
        [p]expset init [角色名稱] [等級] [經驗值] [日期] {@使用者}
        日期格式為：%Y/%m/%d (例：1996/11/30)
        '''
        if user is None:
            user = ctx.author
        await self._levelexp_verification(user, level=level, exp=exp)
        await self.config.user(user).name.set(name)
        previous_date = datetime.datetime.strptime(date, '%Y/%m/%d')
        await self.config.user(user).previous_date.set(datetime.datetime.timestamp(previous_date))
        await ctx.tick()
        await self._remove_after_seconds(ctx, 5)

    @commands_expset.command(name='name', aliases=['ign', 'id'])
    async def expset_name(self, ctx, value):
        '''設定角色名稱
        [p]expset name [角色名稱]
        '''
        await self.config.user(ctx.author).name.set(value)
        # await ctx.send(f'已變更名稱為：{value}')
        await ctx.tick()
        await self._remove_after_seconds(ctx, 5)

    @commands_expset.command(name='levelexp')
    async def expset_setlevelexp(self, ctx, level, exp):
        '''設定經驗以及等級
        [p]expset levelexp [level] [exp]
        '''
        await self._levelexp_verification(ctx.author, level=level, exp=value)
        await ctx.tick()
        await self._remove_after_seconds(ctx, 5)

    @commands_expset.command(name='resetavg')
    async def expset_clear_velocity(self, ctx, user: discord.User):
        '''重置日平均
        [p]expset resetavg [@使用者]
        '''
        await self.config.user(user).previous_date.set(datetime.datetime.timestamp(datetime.datetime.strptime('1900/01/01','%Y/%m/%d')))
        await self.config.user(user).daily_velocity.set(0.0)
        await ctx.tick()
        await self._remove_after_seconds(ctx, 5)

    @checks.is_owner()
    @checks.admin()
    @commands_expset.command(name='setname')
    async def expset_name_admin(self, ctx, value, user: discord.User = None):
        '''設定角色名稱 (管理員)
        [p]expset setname [角色名稱] [@使用者]
        '''
        if user is None:
            user = ctx.author
        await self.config.user(user).name.set(value)
        await ctx.tick()
        await self._remove_after_seconds(ctx, 5)

    @checks.is_owner()
    @checks.admin()
    @commands_expset.command(name='setlevel')
    async def expset_level_admin(self, ctx, value, user: discord.User = None):
        '''設定角色等級 (管理員)
        [p]expset setlevel [等級] {@使用者}
        '''
        if user is None:
            user = ctx.author
        await self._levelexp_verification(user, level=value)
        await ctx.tick()
        await self._remove_after_seconds(ctx, 5)

    @checks.is_owner()
    @checks.admin()
    @commands_expset.command(name='setexp')
    async def expset_exp_admin(self, ctx, value, user: discord.User = None):
        '''設定角色經驗值 (管理員)
        [p]expset setexp [經驗值] {@使用者}
        '''
        if user is None:
            user = ctx.author
        await self._levelexp_verification(user, exp=value)
        await ctx.tick()
        await self._remove_after_seconds(ctx, 5)

    @checks.is_owner()
    @checks.admin()
    @commands_expset.command(name='setdate')
    async def expset_date_admin(self, ctx, value, user: discord.User = None):
        '''設定更新日期 (管理員)
        [p]expset setdate [日期] {@使用者}
        日期格式為：%Y/%m/%d (例：1996/11/30)
        '''
        if user is None:
            user = ctx.author
        await self.config.user(user).previous_date.set(datetime.datetime.timestamp(datetime.datetime.strptime(value, '%Y/%m/%d')))
        await ctx.tick()
        await self._remove_after_seconds(ctx, 5)

    @checks.is_owner()
    @commands_expset.command(name='setvelocity')
    async def expset_velocity(self, ctx, value, user: discord.User = None):
        '''設定角色日平均 (擁有者)
        [p]expset setvelocity [速率] {@使用者}
        '''
        if user is None:
            user = ctx.author
        await self.config.user(user).daily_velocity.set(int(value))
        await ctx.tick()
        await self._remove_after_seconds(ctx, 5)

    @checks.is_owner()
    @checks.admin()
    @commands_expset.command(name='setlevelexp')
    async def expset_setlevelexp(self, ctx, level, exp, user: discord.User = None):
        '''設定使用者經驗以及等級 (管理員)
        [p]expset setlevelexp [level] [exp]
        '''
        if user is None:
            user = ctx.author
        await self._levelexp_verification(user, level=level, exp=value)
        await ctx.tick()
        await self._remove_after_seconds(ctx, 5)


