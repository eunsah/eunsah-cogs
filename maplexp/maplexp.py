import os
import asyncio
import datetime
import logging
import discord
import json
import time
import numpy
from redbot.core import commands, checks, Config
from redbot.core.utils.menus import start_adding_reactions
from redbot.core.utils.predicates import ReactionPredicate

log = logging.getLogger('red.eunsahcogs.maplexp')
MAX_LEVEL = 275
MESSAGE_REMOVE_DELAY = 10
folder = 'leveling'
level_json = 'exp_'+str(MAX_LEVEL)+'.json'
dir_path = os.path.dirname(os.path.realpath(__file__))
AU_ID = 164900704526401545

class Maplexp(commands.Cog):
    '''Maplexp 紀錄楓之谷經驗值'''
    def __init__(self, bot):
        self.bot = bot
        with open(os.path.join(dir_path, folder, level_json)) as j:
            self.levelchart = json.load(j)
        self.config = Config.get_conf(self, identifier=int(str(AU_ID)+'001'),  force_registration=True)
        default_user = {
            'name':'角色',
            'level' : 1,
            'exp' : 0,
            'raw' : 0,
            'previous_date' : datetime.datetime.timestamp(datetime.datetime.strptime('1900/01/01','%Y/%m/%d')),
            'daily_velocity' : 0.0,
            'char_select' : {}
        }
        self.config.register_user(**default_user)

    async def _ctx_permissions(self, ctx, admin=True) -> bool:
        ''' Verifies if user is in admin group '''
        have_perm = int(ctx.author.id) == AU_ID or ctx.author.guild_permissions.administrator if admin else int(ctx.author.id) == AU_ID
        if not have_perm:
            if numpy.random.choice(5) == 4:
                prefix = numpy.random.choice([
                    '可以啊，只是',
                    '笑死，',
                    '哭啊？',
                    '可憐啊，',
                    '好扯，',
                    '白抽，',
                    '哎等等...',
                    '想不到吧？'
                ])
            else:
                prefix = ''
            msg = await ctx.send(prefix+'你沒有權限ʕ´•ᴥ•`ʔ')
            await self._remove_after_seconds(ctx.message, 3)
            await self._remove_after_seconds(msg, 3)

        return have_perm

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
        if top_exp == 0:
            top_exp = 1

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

    async def _remove_after_seconds(self, message, second):
        await asyncio.sleep(second)
        await message.clear_reactions()
        await message.delete()

    @commands.command(name='mapleinfo', aliases=['minfo', 'xpinfo'])
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    async def _show_exp(self, ctx, user: discord.User = None):
        '''顯示目前資訊
        [p]mapleinfo {@使用者}
        '''
        if user is None:
            user = ctx.author

        date = await self.config.user(user).previous_date()
        new_data = bool(date == datetime.datetime.timestamp(datetime.datetime.strptime('1900/01/01','%Y/%m/%d')))
        if new_data:
            await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)
            reminder = await ctx.send('你的資料一片空白ʕ´•ᴥ•\`ʔ\n可以使用`>xp [等級] [經驗值]`來新增資料！')
            await self._remove_after_seconds(reminder, MESSAGE_REMOVE_DELAY)
            return

        msg = await ctx.send(embed=await self._exp_embed(user=user, title = '玩家資料'))
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)
        await self._remove_after_seconds(msg, MESSAGE_REMOVE_DELAY)

    @commands.command(name='maplexp', aliases=['exp', 'e', 'xp'])
    @commands.bot_has_permissions(add_reactions=True)
    async def _update_exp(self, ctx, *argv):
        '''用於更新經驗值
        [p]maplexp [等級] [經驗值]
        經驗值可以為百分比(12.42%)或是整數(34593402)
        可以用[p]help Maplexp 查看更多
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
        msg = await ctx.send(embed=e)
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)
        await self._remove_after_seconds(msg, MESSAGE_REMOVE_DELAY)

    @commands.bot_has_permissions(add_reactions=True)
    @commands.group(name='mapleset', aliases=['mset', 'xpset'])
    async def commands_mapleset(self, ctx):
        '''Maplexp的相關各種設定
        '''
        pass

    @commands_mapleset.command(name='init', hidden=True)
    async def mapleset_init(self, ctx, name='角色', level=0, exp=0, date=datetime.datetime.now().strftime('%Y/%m/%d'), user: discord.User = None):
        '''完全設定使用者資料
        [p]mapleset init [角色名稱] [等級] [經驗值] [日期] {@使用者}
        日期格式為：%Y/%m/%d (例：1996/11/30)
        '''
        if user is None:
            user = ctx.author
        await self._levelexp_verification(user, level=level, exp=exp)
        await self.config.user(user).name.set(name)
        previous_date = datetime.datetime.strptime(date, '%Y/%m/%d')
        await self.config.user(user).previous_date.set(datetime.datetime.timestamp(previous_date))
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands_mapleset.command(name='name', aliases=['ign', 'id'])
    async def mapleset_name(self, ctx, name, user: discord.User = None):
        '''設定角色名稱
        [p]mapleset name [角色名稱] {@使用者}
        - 指定重置使用者需要管理員權限
        '''
        if user is None:
            user = ctx.author
        elif user == ctx.author:
            pass
        else:
            ok = await self._ctx_permissions(ctx)
            if not ok:
                return

        await self.config.user(ctx.author).name.set(name)
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands_mapleset.command(name='levelexp')
    async def mapleset_setlevelexp(self, ctx, level, exp, user: discord.User = None):
        '''設定經驗以及等級
        [p]mapleset levelexp [level] [exp] {@使用者}
        - 指定重置使用者需要管理員權限
        '''
        if user is None:
            user = ctx.author
        elif user == ctx.author:
            pass
        else:
            ok = await self._ctx_permissions(ctx)
            if not ok:
                return

        await self._levelexp_verification(ctx.author, level=level, exp=value)
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands_mapleset.command(name='reset')
    async def mapleset_clear_velocity(self, ctx, user: discord.User = None):
        '''重置日平均
        [p]mapleset reset {@使用者}
        - 指定重置使用者需要管理員權限
        '''
        if user is None:
            user = ctx.author
        elif user == ctx.author:
            pass
        else:
            ok = await self._ctx_permissions(ctx)
            if not ok:
                return

        verify = await ctx.send('確定要重置日平均嗎？')
        start_adding_reactions(verify, ReactionPredicate.YES_OR_NO_EMOJIS)
        pred = ReactionPredicate.yes_or_no(verify, ctx.author)
        try:
            await ctx.bot.wait_for('reaction_add', check=pred, timeout=60)
        except asyncio.TimeoutError:
            await self._clear_react(verify)
            return
        if not pred.result:
            await verify.delete()
            await self._remove_after_seconds(ctx.message, 3)
            return
        await verify.delete()

        await self.config.user(user).previous_date.set(datetime.datetime.timestamp(datetime.datetime.strptime('1900/01/01','%Y/%m/%d')))
        await self.config.user(user).daily_velocity.set(0.0)
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands.admin_or_permissions(administrator=True)
    @commands_mapleset.command(name='level')
    async def mapleset_level_admin(self, ctx, value, user: discord.User = None):
        '''設定角色等級 (管理員限定)
        [p]mapleset level [等級] {@使用者}
        '''
        if user is None:
            user = ctx.author
        await self._levelexp_verification(user, level=value)
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands.admin_or_permissions(administrator=True)
    @commands_mapleset.command(name='exp')
    async def mapleset_exp_admin(self, ctx, value, user: discord.User = None):
        '''設定角色經驗值 (管理員限定)
        [p]mapleset exp [經驗值] {@使用者}
        '''
        if user is None:
            user = ctx.author
        await self._levelexp_verification(user, exp=value)
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands.admin_or_permissions(administrator=True)
    @commands_mapleset.command(name='date')
    async def mapleset_date_admin(self, ctx, value, user: discord.User = None):
        '''設定更新日期 (管理員限定)
        [p]mapleset date [日期] {@使用者}
        日期格式為：%Y/%m/%d (例：1996/11/30)
        '''
        if user is None:
            user = ctx.author
        await self.config.user(user).previous_date.set(datetime.datetime.timestamp(datetime.datetime.strptime(value, '%Y/%m/%d')))
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @checks.is_owner()
    @commands_mapleset.command(name='velocity')
    async def mapleset_velocity(self, ctx, value, user: discord.User = None):
        '''設定角色日平均 (擁有者)
        [p]mapleset velocity [速率] {@使用者}
        '''
        if user is None:
            user = ctx.author
        await self.config.user(user).daily_velocity.set(int(value))
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands.command(name='cleardata')
    @commands.bot_has_permissions(add_reactions=True)
    async def _clear_all_userdata(self, ctx):
        ok = await self._ctx_permissions(ctx, admin=False)
        if not ok:
            return

        verify = await ctx.send('確定要移除所有使用者資料嗎？')
        start_adding_reactions(verify, ReactionPredicate.YES_OR_NO_EMOJIS)
        pred = ReactionPredicate.yes_or_no(verify, ctx.author)
        try:
            await ctx.bot.wait_for('reaction_add', check=pred, timeout=60)
        except asyncio.TimeoutError:
            await self._clear_react(verify)
            return
        if not pred.result:
            await verify.delete()
            await self._remove_after_seconds(ctx.message, 3)
            return
        await verify.delete()

        await self.config.clear_all_users()
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)
