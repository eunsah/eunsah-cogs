import os
import asyncio
from datetime import datetime
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
        Maplexp 紀錄楓之谷等級&經驗值
    '''
    def __init__(self, bot):
        self.bot = bot
        with open(os.path.join(dir_path, folder, level_json)) as j:
            self.level_chart = json.load(j)
        self.config = Config.get_conf(self, identifier=int(str(AUTH_UID)+'001'),  force_registration=False)
        self.base_time = datetime.timestamp(datetime.strptime('1900/01/01','%Y/%m/%d'))
        self.default_profile = {
            'net_exp' : 0,
            'avg_exp' : 0.0,
            'date' : self.base_time
        }
        default_user = {
            'ptr_d' : '',
            'usr_d': {}
        }
        self.config.register_user(**default_user)

    def _dict_to_embed(
        self,
        title: str, name: str,
        data_d: dict,
        usr_c: discord.User.color
        ) -> discord.Embed:
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
        e.set_footer(text='更新日期: ' + datetime.fromtimestamp(data_d['date']).strftime('%Y/%m/%d'))

        return e

    def _net_levelexp(self, net_val: int) -> tuple:
        ''' Converts net to level, exp, req
        parameters : net_exp 
        return : level, exp, xp_req 
        '''
        for key in self.level_chart:
            xp_req = self.level_chart[key]
            if xp_req >= net_val:
                return int(key), net_val
            net_val -= xp_req

    def _levelexp_net(self, level: str, exp: str) -> int:
        ''' Converts level, exp to net
        parameters : level, exp
        return : net_exp
        '''
        try:
            if not (level.isdigit() and int(level) in range(MAX_LEVEL)):
                raise ValueError('等級')
            req = self.level_chart[level]
            level = int(level)
            if '.' in exp:
                exp = float(exp.strip('%'))
                if exp > 100.0:
                    raise ValueError('經驗值')
                exp = round((exp*req)/100)
            else:
                if exp >= req:
                    raise ValueError('經驗值')
            exp = int(exp)
        except ValueError as verr:
            self._error_out_of_range(ctx, verr)

        net = 0
        for key in self.level_chart:
            if int(key) == level:
                return net + exp
            net += self.level_chart[key]

    async def _remove_after_seconds(self, message, second):
        await asyncio.sleep(second)
        # await message.delete()

    async def _error_char_not_found(self, ctx, name: str):
        err = await ctx.send('查無角色名稱資料!')
        await self._remove_after_seconds(err, MESSAGE_REMOVE_DELAY)
        return

    async def _error_out_of_range(self, ctx, item: str):
        err = await ctx.send(f'{item}參數不在許可範圍!')
        await self._remove_after_seconds(err, MESSAGE_REMOVE_DELAY)
        return

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
            await self._remove_after_seconds(ctx.message, 3)
            await self._remove_after_seconds(msg, 20)


        return have_perm

    async def _user_check(self, ctx, user) -> discord.User:
        ''' Macro for user check'''
        if user is None:
            return ctx.author
        elif user == ctx.author:
            return user
        else:
            ok = await self._ctx_permissions(ctx)
            if not ok:
                return False
        return user

    async def _update(
        self,
        ctx: commands.Context,
        level: str, exp: str,
        char: str = None
        ):
        '''
        '''
        if char is None:
            char = await self.config.user(ctx.author).ptr_d() # str     
        usr_dict = await self.config.user(ctx.author).usr_d() # dict

        if char == '':
            async with self.config.user(ctx.author).usr_d() as ud:
                ud[ctx.author.display_name] = self.default_profile
            await self.config.user(ctx.author).ptr_d.set(ctx.author.display_name)
            char = ctx.author.display_name

        req = self.level_chart[level]
        exp_growth = 0
        new_avg = 0.0
        net = self._levelexp_net(level, exp)

        async with self.config.user(ctx.author).usr_d() as udc:
            # update dict net_exp, avg_exp, date
            try:
                exp_growth = net - udc[char]['net_exp']
                udc[char]['net_exp'] = net # update net
                old_date = udc[char]['date']
                if old_date != self.base_time:
                    date_timedelta = datetime.now() - datetime.fromtimestamp(old_date)
                    new_avg = round(exp_growth/(date_timedelta.total_seconds()/86400)) # 86400 is the total seconds in a day
                    udc[char]['avg_exp'] = round(((udc[char]['avg_exp']+new_avg)/2), 2)

                udc[char]['date'] = datetime.timestamp(datetime.now())
            except KeyError:
                await self._error_char_not_found(ctx, char)
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
            更新經驗值
            使用方式：[p]maplexp [等級] [經驗值]
            - 經驗值可以為百分比(12.42%)或是整數(34593402)

            其他使用:
                    [p]maplexp                      - 顯示
                    [p]maplexp [角色]                - 查看我的角色資料
                    [p]maplexp [使用者名稱]           - 查看對方資料
                    [p]maplexp [使用者名稱] [角色]     - 查看對方角色資料
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
                    await self._show_exp(ctx, char=None, user=user)
                    return

                else:
                    # args size: 2, show mentioned key character
                    await self._show_exp(ctx, char=argv[1], user=user)
                    return

            else:
                # if no mentions in argvs
                if arg_size == 1:
                    #　show char
                    await self._show_exp(ctx, char=argv[0], user=ctx.author)
                    return

                else:
                    # user update default
                    await self._update(ctx, level=argv[0], exp=argv[1])
                    return
        else:
            # length == 3, user update character
            await self._update(ctx, level=argv[1], exp=argv[2], char=argv[0])
            return


    @commands.group(name='maple', aliases=['m'])
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    async def commands_maple(self, ctx):
        '''
            楓之谷等級經驗資料
        '''
        pass

    @commands_maple.command(name='info')
    async def _show_exp(self, ctx, char: str = None, user: discord.User = None):
        '''
            顯示角色資訊 (mapleinfo | minfo | xpinfo)
            使用方式：[p]mapleinfo
        '''
        if user is None:
            user = ctx.author

        if char is None:
            char = await self.config.user(user).ptr_d() # str
        usr_dict = await self.config.user(user).usr_d() # dict

        if char == '':
            if ctx.author == user:
                p = '你'
            else:
                p = user.display_name

            reminder = await ctx.send(p+r'的資料一片空白ʕ´•ᴥ•\`ʔ'+'\n可以使用`>xp [等級] [經驗值]`來新增資料！')
            await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)
            await self._remove_after_seconds(reminder, 60)
            return

        tar_d = None
        try:
            tar_d = usr_dict[char]
        except KeyError:
            await self._error_char_not_found(ctx, char)
            return

        date = tar_d['date']

        e = self._dict_to_embed(
            title = str(user.display_name)+'的玩家資料',
            name = char,
            data_d = tar_d,
            usr_c = user.color
            )
        embed = await ctx.send(embed=e)
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)
        await self._remove_after_seconds(embed, MESSAGE_REMOVE_DELAY)

    @commands_maple.command(name='create')
    async def maple_create(
        self, ctx: commands.Context,
        char: str,
        level: str, exp: str,
        date = datetime.now().strftime('%Y/%m/%d'),
        user: discord.User = None):
        '''
            新增角色資料
            使用方式：[p]mapleset create [角色名稱] [等級] [經驗值] [日期]
            - 日期格式為：%Y/%m/%d (例：1996/11/30)
        '''
        # if user is None:
        #     user = ctx.author
        # elif user == ctx.author:
        #     pass
        # else:
        #     ok = await self._ctx_permissions(ctx)
        #     if not ok:
        #         return
        user = await self._user_check(ctx, user)
        if user is False:
            return
            
        net = self._levelexp_net(level=level, exp=exp)

        async with self.config.user(user).usr_d() as ud:
            ud[char] = self.default_profile
            ud[char]['net_exp'] = net
            ud[char]['date'] = datetime.timestamp(datetime.strptime(date, '%Y/%m/%d'))
            
        if await self.config.user(user).ptr_d() == '':
            await self.config.user(user).ptr_d.set(char)

        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands_maple.command(name='delete', aliases=['d', 'del'])
    async def maple_delete(self, ctx, char: str, user: discord.User = None):
        '''
            設定等級及經驗值
            使用方式：[p]maple delete [角色名稱]
        '''
        # if user is None:
        #     user = ctx.author
        # elif user == ctx.author:
        #     pass
        # else:
        #     ok = await self._ctx_permissions(ctx)
        #     if not ok:
        #         return
        user = await self._user_check(ctx, user)
        if user is False:
            return

        async with self.config.user(user).usr_d() as ud:
            try:
                del ud[char]
            except KeyError:
                await self._error_char_not_found(ctx, char)
                await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)
                return

        ud = await self.config.user(user).usr_d()
        if len(ud.keys()) == 0:
            next_key = ''
        else:
            next_key = list(ud.keys())[0]
        await self.config.user(user).ptr_d.set(next_key)

        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands_maple.command(name='list', aliases=['l'])
    async def maple_list(self, ctx, user: discord.User = None):
        '''
            顯示角色列表
            使用方式：[p]mapleset list {@使用者}
        '''
        if user is None:
            user = ctx.author
        u_name = str()
        u_level = str()
        u_date = str()
        u_size = 0
        async with self.config.user(user).usr_d() as ud:
            u_size = len(ud)
            for item in ud:
                date = datetime.fromtimestamp(ud[item]['date']).strftime('%Y/%m/%d')
                level, exp = self._net_levelexp(ud[item]['net_exp'])
                req = self.level_chart[str(level)]
                exp = (exp/req)*100 if req != 0 else 0.0
                u_name += str(item)+'\n'
                u_level += f'{level}({exp:.2f}%)\n'
                u_date += str(date)+'\n'

        if u_size == 0:
            if ctx.author == user:
                p = '你'
            else:
                p = user.display_name

            empty = await ctx.send(p+r'的資料列表一片空白ʕ´•ᴥ•\`ʔ'+'\n可以使用`>xp [等級] [經驗值]`來新增資料！')

            await self._remove_after_seconds(empty, MESSAGE_REMOVE_DELAY)
            return

        e = discord.Embed(
            description = user.display_name+'的角色列表',
            color = user.color
        )
        e.add_field(name='角色名稱', value=u_name, inline=True)
        e.add_field(name='等級', value=u_level, inline=True)
        e.add_field(name='最後更新時間', value=u_date, inline=True)

        await ctx.send(embed=e)
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)


    @commands.group(name='mapleset', aliases=['mset', 'xpset'])
    @commands.bot_has_permissions(add_reactions=True)
    async def commands_mapleset(self, ctx):
        '''
            楓之谷等級&經驗值設定
        '''
        pass

    @commands_mapleset.command(name='default', aliases=['d'])
    async def mapleset_default(self, ctx, char: str, user: discord.User = None):
        '''
            設定預設角色
            使用方式：[p]mapleset default [角色名稱]
            - 請確認自己擁有此角色
        '''
        user = await self._user_check(ctx, user)
        if user is False:
            return

        ud = await self.config.user(user).usr_d()
        if not char in ud.keys():
            await ctx.send('查無角色名稱!')
            return

        await self.config.user(user).ptr_d.set(char)
        await ctx.tick()
        return

    @commands_mapleset.command(name='name', aliases=['ign', 'id'])
    async def mapleset_name(self, ctx, o_id, n_id, user: discord.User = None):
        '''
            設定角色名稱
            使用方式：[p]mapleset name [舊角色名稱] [新角色名稱]
        '''
        # if user is None:
        #     user = ctx.author
        # elif user == ctx.author:
        #     pass
        # else:
        #     ok = await self._ctx_permissions(ctx)
        #     if not ok:
        #         return
        user = await self._user_check(ctx, user)
        if user is False:
            return

        async with self.config.user(user).usr_d() as ud:
            ud[n_id] = ud.pop(o_id)

        ptr = await self.config.user(user).ptr_d()
        if o_id == ptr_d:
            await self.config.user(user).ptr_d.set(n_id)

        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands_mapleset.command(name='levelexp')
    async def mapleset_setlevelexp(
        self, ctx: commands.Context,
        level: str, exp: str,
        char: str = None,
        user: discord.User = None
        ):
        '''
            設定等級及經驗值
            使用方式：[p]mapleset levelexp [level] [exp] [角色名稱]
        '''
        # if user is None:
        #     user = ctx.author
        # elif user == ctx.author:
        #     pass
        # else:
        #     ok = await self._ctx_permissions(ctx)
        #     if not ok:
        #         return
        user = await self._user_check(ctx, user)
        if user is False:
            return
        if char is None:
            char = self.config.user(user).ptr_d()


        net = self._levelexp_net(level=level, exp=exp)

        async with self.config.user(user).usr_d() as ud:
            ud[char]['net_exp'] = net

        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands_mapleset.command(name='reset')
    async def mapleset_clear_velocity(
        self,
        ctx: commands.Context,
        char: str = None,
        user: discord.User = None
        ):
        '''
            重置日平均
            使用方式：[p]mapleset reset
        '''
        # if user is None:
        #     user = ctx.author
        # elif user == ctx.author:
        #     pass
        # else:
        #     ok = await self._ctx_permissions(ctx)
        #     if not ok:
        #         return
        user = await self._user_check(ctx, user)
        if user is False:
            return
        if char is None:
            char = self.config.user(user).ptr_d()

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

        async with self.config.user(user).usr_d() as ud:
            ud[char]['avg_exp'] = 0.0
            ud[char]['date'] = self.base_time
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands.bot_has_permissions(add_reactions=True)
    @commands_mapleset.command(name='cleardata', hidden=True)
    async def _mapleset_clear_all_userdata(self, ctx):
        '''
            移除所有使用者資料 (擁有者限定)
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

        await self.config.user(ctx.author).clear()
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands.command(name='mapleinfo')
    @checks.is_owner()
    async def maple_info(self, ctx, user: discord.User = None):
        '''
            管理員後端
        '''
        if user is None:
            user = ctx.author
        data = await self.config.user(user)()
        await ctx.send(data)
