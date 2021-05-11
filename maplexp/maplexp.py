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
MESSAGE_REMOVE_DELAY = 30
folder = 'leveling'
level_json = 'exp_' + str(MAX_LEVEL) + '.json'
dir_path = os.path.dirname(os.path.realpath(__file__))
AUTH_UID = 164900704526401545

class Maplexp(commands.Cog):
    '''
        Maplexp 紀錄楓之谷經驗值
    '''
    def __init__(self, bot):
        self.bot = bot
        with open(os.path.join(dir_path, folder, level_json)) as j:
            self.level_chart = json.load(j)
        self.config = Config.get_conf(self, identifier=int(str(AUTH_UID)+'001'),  force_registration=True)
        self.base_time = datetime.datetime.timestamp(datetime.datetime.strptime('1900/01/01','%Y/%m/%d'))
        self.default_profile = {
            'net_exp' : 0,
            'date' : self.base_time,
            'avg_exp' : 0.0
        }
        default_user = {
            'ptr_d' : '角色',
            'usr_d': {
                '角色' : {**self.default_profile}
            }
        }
        self.config.register_user(**default_user)

    async def _ctx_permissions(self, ctx, admin=True) -> bool:
        ''' Verifies if user is in admin group '''
        have_perm = int(ctx.author.id) == AUTH_UID or ctx.author.guild_permissions.administrator if admin else int(ctx.author.id) == AUTH_UID
        if not have_perm:
            if numpy.random.arg_size(10) == 5:
                prefix = numpy.random.arg_size([
                    '可以啊，只是',
                    '笑死，',
                    '哭啊？',
                    '可憐啊，',
                    '好扯，',
                    '白抽，',
                    '哎等等...',
                    '想不到吧？',
                    '你有沒有想過',
                    '我希望你可以意識到',
                    '我ok啊? 但是'
                ])
            else:
                prefix = ''
            msg = await ctx.send(prefix+r'你沒有權限ʕ´•ᴥ•`ʔ')
            try:
                await self._remove_after_seconds(ctx.message, 3)
                await self._remove_after_seconds(msg, 20)
            except:
                pass

        return have_perm

    def _net_levelexp(self, net_val:int) -> tuple:
        ''' Converts net to level, exp, req
        parameters : net_exp 
        return : level, exp, xp_req 
        '''
        for key in self.level_chart:
            xp_req = self.level_chart[key]
            if xp_req >= net_val:
                return int(key), net_val
            net_val -= xp_req

    def _levelexp_net(self, level:int, exp:int) -> int:
        ''' Converts level, exp to net
        parameters : level, exp
        return : net_exp
        '''
        net = 0
        for key in self.level_chart:
            if int(key) == level:
                return net + exp
            net += self.level_chart[key]
    
    async def _remove_after_seconds(self, message, second):
        await asyncio.sleep(second)
        await message.delete()

    async def _char_not_found_error(self, ctx, name:str):
        err = await ctx.send('character not found!')
        await self._remove_after_seconds(err, MESSAGE_REMOVE_DELAY)
        return

    def _dict_to_embed(self, title:str, name:str, data_d:dict, usr_c:discord.User.color) -> discord.Embed:
        '''
        parameters : title, data_d, usr_c
        return : discord.Embed
        '''
        level, exp = self._net_levelexp(data_d['net_exp'])
        avg_exp = data_d['avg_exp']
        req = self.level_chart[str(level)]
        exp_perc = round((exp/req)*100, 2) if req != 0 else 0.0

        e = discord.Embed(
            description = title,
            color = usr_c
        )
        e.add_field(name='名稱', value=name, inline=True)
        e.add_field(name='等級', value=level, inline=True)
        e.add_field(name='經驗值', value=f'{exp:,} ({exp_perc:.2f}%)', inline=False)
        e.add_field(name='經驗成長日平均', value=f'{round(avg_exp):,}', inline=False)
        e.set_footer(text='更新日期: ' + datetime.datetime.fromtimestamp(data_d['date']).strftime('%Y/%m/%d'))

        return e

    @commands.command(name='mapleinfo', aliases=['minfo', 'xpinfo'], hidden=True)
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    async def _show_exp(self, ctx, user: discord.User = None, char: str = None):
        '''
            顯示角色資訊 (mapleinfo || minfo || xpinfo)
            使用方式：[p]mapleinfo {@使用者}
        '''
        if user is None:
            user = ctx.author

        if char is None:
            char = await self.config.user(user).ptr_d() # str
        usr_dict = await self.config.user(user).usr_d() # dict

        tar_d = None
        try:
            tar_d = usr_dict[char]
        except KeyError:
            await self._char_not_found_error(ctx, char)
            return

        date = tar_d['date']
        no_data = bool(date == self.base_time)
        if no_data:
            if ctx.author == user:
                p = '你'
            else:
                p = user.display_name

            reminder = await ctx.send(p+r'的資料一片空白ʕ´•ᴥ•\`ʔ'+'\n可以使用`>xp [等級] [經驗值]`來新增資料！')
            await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)
            await self._remove_after_seconds(reminder, 60)
            return

        e = self._dict_to_embed(
            title = str(user.display_name)+'的玩家資料', 
            name = char, 
            data_d = tar_d, 
            usr_c = user.color
            )
        embed = await ctx.send(embed=e)
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)
        # await self._remove_after_seconds(embed, MESSAGE_REMOVE_DELAY)

    async def _update(self, ctx:commands.Context, level:str, exp:str, char:str = None):
        '''
        '''
        if char is None:
            char = await self.config.user(ctx.author).ptr_d() # str     
        usr_dict = await self.config.user(ctx.author).usr_d() # dict

        if char == '角色':
            async with self.config.user(ctx.author).usr_d() as ud:
                del ud['角色']
                ud[ctx.author.display_name] = self.default_profile
            await self.config.user(ctx.author).ptr_d.set(ctx.author.display_name)
            char = ctx.author.display_name

        if not (level.isdigit() and int(level) in range(MAX_LEVEL)): 
            err = ctx.send('err in level')
            await self._remove_after_seconds(err, MESSAGE_REMOVE_DELAY)
            return            

        req = 0
        try:
            if '.' in exp:
                per = float(exp.strip('%'))/100
                req = self.level_chart[level]
                exp = per*req
            level = int(level)
            exp = int(exp)
        except ValueError:
            help_msg = ctx.send_help()
            await self._remove_after_seconds(help_msg, MESSAGE_REMOVE_DELAY)
            return

        exp_growth = 0
        new_avg = 0.0

        async with self.config.user(ctx.author).usr_d() as udc:
            # update dict net_exp, avg_exp, date
            try:
                net = self._levelexp_net(level, exp)
                exp_growth = net - udc[char]['net_exp']
                udc[char]['net_exp'] = net # update net
                old_date = udc[char]['date']
                if old_date != self.base_time:
                    date_timedelta = datetime.datetime.now() - datetime.datetime.fromtimestamp(old_date)
                    new_avg = round(exp_growth/(date_timedelta.total_seconds()/86400)) # 86400 is the total seconds in a day
                    udc[char]['avg_exp'] = round(((udc[char]['avg_exp']+new_avg)/2), 2)

                udc[char]['date'] = datetime.datetime.timestamp(datetime.datetime.now())
            except KeyError:
                await self._char_not_found_error(ctx, char)
                return


        usr_dict = await self.config.user(ctx.author).usr_d() # refesh usr_dict
        exp_growth_perc = round((exp_growth/req)*100, 2) if req != 0 else 0.0

        e = self._dict_to_embed(
            title = char+'的資料更新',
            name = char,
            data_d = usr_dict[char],
            usr_c = ctx.author.color
        )
        e.add_field(name="經驗成長日平均 (更新)", value=f'{new_avg:,}', inline=True)
        e.add_field(name="總經驗成長幅", value=f'{exp_growth:,} ({exp_growth_perc:,.2f}%)', inline=True)
        await ctx.send(embed=e) 
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)
        return

    @commands.command(name='maplexp', aliases=['exp', 'xp'])
    @commands.bot_has_permissions(add_reactions=True)
    async def _exp(self, ctx, *argv):
        '''
            用於更新經驗值
            使用方式：[p]maplexp [等級] [經驗值]
            - 經驗值可以為百分比(12.42%)或是整數(34593402)
            - 可以用[p]help Maplexp 查看更多
        '''
        if len(argv) not in range(4):
            # argv check
            await ctx.send_help()
            return

        arg_size = len(argv)
        ''' Function depends on argv len within 0~3
        0 -> show default
        1 -> show my character, show others' default
        2 -> update default, show others' character
        3 -> update character
        '''

        if arg_size == 0:
            # if no argvs, show self default character
            await self._show_exp(ctx)

        elif arg_size in range(1, 3):
            # if argvs in 1 or 2
            if '<@!' in argv[0] and len(argv[0].strip('<>@!')) == 18:
                # check if first argv is a mention
                user = await self.bot.get_or_fetch_user(int(argv[0].strip('<>!@')))

                if arg_size == 1:
                    # show mentioned default character
                    await self._show_exp(ctx, user=user)
                    return

                else:
                    # args size: 2, show mentioned key character
                    await self._show_exp(ctx, user=user, char=argv[1])
                    return

            else:
                # if no mentions in argvs
                if arg_size == 1:
                    #　show char
                    await self._show_exp(ctx, user=ctx.author, char=argv[0])
                    return

                else:
                    # user update default
                    await self._update(ctx, level=argv[0], exp=argv[1])
                    return
        else:
            # length == 3, user update character
            await self._update(ctx, level=argv[1], exp=argv[2], char=argv[0])
            return






    @commands.bot_has_permissions(add_reactions=True)
    @commands.group(name='mapleset', aliases=['mset', 'xpset'])
    async def commands_mapleset(self, ctx):
        '''Maplexp的相關各種設定
        '''
        pass

    @commands_mapleset.command(name='init', hidden=True)
    async def mapleset_init(self, ctx, name='角色', level=0, exp=0, date=datetime.datetime.now().strftime('%Y/%m/%d'), user: discord.User = None):
        '''完全設定使用者資料
        使用方式：[p]mapleset init [角色名稱] [等級] [經驗值] [日期] {@使用者}
        - 日期格式為：%Y/%m/%d (例：1996/11/30)
        '''
        if user is None:
            user = ctx.author
        await self._levelexp_verification(user, level=level, exp=exp)
        await self.config.user(user).name.set(name)
        date = datetime.datetime.strptime(date, '%Y/%m/%d')
        await self.config.user(user).date.set(datetime.datetime.timestamp(date))
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands_mapleset.command(name='name', aliases=['ign', 'id'])
    async def mapleset_name(self, ctx, name, user: discord.User = None):
        '''設定角色名稱
        使用方式：[p]mapleset name [角色名稱] {@使用者}
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
        '''設定等級及經驗值
        使用方式：[p]mapleset levelexp [level] [exp] {@使用者}
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
        使用方式：[p]mapleset reset {@使用者}
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

        await self.config.user(user).date.set(datetime.datetime.timestamp(datetime.datetime.strptime('1900/01/01','%Y/%m/%d')))
        await self.config.user(user).daily_velocity.set(0.0)
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands.admin_or_permissions(administrator=True)
    @commands_mapleset.command(name='level')
    async def mapleset_level_admin(self, ctx, value, user: discord.User = None):
        '''設定角色等級 (管理員限定)
        使用方式：[p]mapleset level [等級] {@使用者}
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
        使用方式：[p]mapleset exp [經驗值] {@使用者}
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
        使用方式：[p]mapleset date [日期] {@使用者}
        - 日期格式為：%Y/%m/%d (例：1996/11/30)
        '''
        if user is None:
            user = ctx.author
        await self.config.user(user).date.set(datetime.datetime.timestamp(datetime.datetime.strptime(value, '%Y/%m/%d')))
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @checks.is_owner()
    @commands_mapleset.command(name='velocity')
    async def mapleset_velocity(self, ctx, value, user: discord.User = None):
        '''設定角色日平均 (擁有者限定)
        使用方式：[p]mapleset velocity [速率] {@使用者}
        '''
        if user is None:
            user = ctx.author
        await self.config.user(user).daily_velocity.set(int(value))
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands.bot_has_permissions(add_reactions=True)
    @commands_mapleset.command(name='cleardata', hidden=True)
    async def _mapleset_clear_all_userdata(self, ctx):
        '''移除所有使用者資料 (擁有者限定)
        使用方式：[p]mapleset cleardata
        '''
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
            await self._remove_after_seconds(verify, 5)
            return
        if not pred.result:
            await verify.delete()
            await self._remove_after_seconds(ctx.message, 3)
            return
        await verify.delete()

        await self.config.clear_all()
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)
