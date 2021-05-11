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
            'char_name' : '角色',
            'net_exp' : 0,
            'previous_date' : self.base_time,
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

    def _dict_to_embed(self, title:str, data_d:dict, usr_c:discord.User.color) -> discord.Embed:
        '''
        parameters : title, data_d, usr_c
        return : discord.Embed
        '''
        level, exp = self._net_levelexp(data_d['net_exp'])
        avg_exp = data_d['avg_exp']

        e = discord.Embed(
            description = title,
            color = usr_c
        )
        e.add_field(name='名稱', value=data_d['name'], inline=True)
        e.add_field(name='等級', value=level, inline=True)
        e.add_field(name='經驗值', value=f'{exp:,} ({round((exp/self.level_chart[str(level)])*100, 2):.2f}%)', inline=False)
        e.add_field(name='經驗成長日平均', value=f'{round(avg_exp):,}', inline=False)
        e.set_footer(text='更新日期: ' + datetime.datetime.fromtimestamp(data_d['previous_date']).strftime('%Y/%m/%d'))

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

        try:
            await ctx.send(char)
            await ctx.send(usr_dict)
            tar_d = usr_dict[char]
        except KeyError:
            err = await ctx.send('character not found!')
            await self._remove_after_seconds(err, MESSAGE_REMOVE_DELAY)
            return

        date = tar_d['previous_date']
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

        e = self._dict_to_embed(title=str(user.display_name)+'的玩家資料', data_d=tar_d, usr_c=user.color)
        embed = await ctx.send(embed=e)
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)
        # await self._remove_after_seconds(embed, MESSAGE_REMOVE_DELAY)

    def _exp_updateinfo(self, ctx: commands.Context, usr_d: dict, usr_c: str, net_exp: int):
        '''
        '''
        pass

    @commands.command(name='maplexp', aliases=['exp', 'e', 'xp'])
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

                else:
                    # args size: 2, show mentioned key character
                    await self._show_exp(ctx, user=user, char=argv[1])
            else:
                # if no mentions in argvs
                if arg_size == 1:
                    #　show char
                    await self._show_exp(ctx, user=ctx.author, char=argv[0])
        

        # if arg_size in [0, 1]:
        #     if arg_size == 0:
        #         await self._show_exp(ctx, ctx.author)
        #     else: # 1
        #         char_list = await self.config.user(ctx.author).char_list() 
        #         if argv[0] in char_list: # if parameter in char list, return their character
        #             return

        #         else:
        #             try:
        #                 user_mention = argv[0] # then this is discord.user
        #                 user = await self.bot.get_or_fetch_user(int(user_mention.strip('<>!@')))
        #                 await self._show_exp(ctx, user)
        #                 return
        #             except ValueError: # if argv is not in list nor a user
        #                 await ctx.send('User not found!!')
        #                 return

        # elif arg_size in [2, 3]:
        #     if arg_size == 2:

        #         if str(argv[0]).isdigit(): # if in 2 args, first is digit, then assuming user is updating default character

        #             level = argv[0]
        #             raw = await self.config.user(ctx.author).raw()
        #             previous_date_datetime = datetime.datetime.fromtimestamp(await self.config.user(ctx.author).previous_date())
        #             name = await self.config.user(ctx.author).name()
        #             if name == '角色':
        #                 await self.config.user(ctx.author).name.set(ctx.author.display_name)

        #             await self._levelexp_verification(ctx.author, level=argv[0], exp=argv[1].strip('%'))

        #             await self.config.user(ctx.author).previous_date.set(datetime.datetime.timestamp(datetime.datetime.now()))

        #             daily_velocity = await self.config.user(ctx.author).daily_velocity()
        #             raw_diff = await self.config.user(ctx.author).raw() - raw
        #             raw_diff_percentage = round((raw_diff / self.level_chart[str(level)])*100, 2)

        #             if previous_date_datetime != datetime.datetime.timestamp(datetime.datetime.strptime('1900/01/01','%Y/%m/%d')):
        #                 date_diff_timedelta = datetime.datetime.fromtimestamp(await self.config.user(ctx.author).previous_date()) - previous_date_datetime
        #                 avg_exp = round(raw_diff/(date_diff_timedelta.total_seconds()/86400)) # 86400 is the total seconds in a day
        #                 await self.config.user(ctx.author).daily_velocity.set(round(((avg_exp+daily_velocity)/2), 2))
        #             else:
        #                 avg_exp = 0
        #         else: # else
        #             pass 
        # else:
        #     await ctx.send('Something went wrong')
        #     await ctx.send_help()
        #     return
        
        # e = await self._get_user_embed(user=ctx.author, title='更新'+str(ctx.author.display_name)+'的經驗值')
        # e.add_field(name="經驗成長日平均 (更新)", value=f'{avg_exp:,}', inline=True)
        # e.add_field(name="總經驗成長幅", value=f'{raw_diff:,} ({raw_diff_percentage:,.2f}%)', inline=True)
        # await ctx.tick()
        # msg = await ctx.send(embed=e)
        # await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)
        # return

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
        previous_date = datetime.datetime.strptime(date, '%Y/%m/%d')
        await self.config.user(user).previous_date.set(datetime.datetime.timestamp(previous_date))
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

        await self.config.user(user).previous_date.set(datetime.datetime.timestamp(datetime.datetime.strptime('1900/01/01','%Y/%m/%d')))
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
        await self.config.user(user).previous_date.set(datetime.datetime.timestamp(datetime.datetime.strptime(value, '%Y/%m/%d')))
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
