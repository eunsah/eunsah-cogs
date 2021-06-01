import os
import asyncio
# import logging
import discord
import json
import numpy
from datetime import datetime, timedelta
from typing import Optional
from redbot.core import commands, checks, Config
from redbot.core.utils.menus import start_adding_reactions
from redbot.core.utils.predicates import ReactionPredicate

# log = logging.getLogger('red.eunsahcogs.maplexp')
MAX_LEVEL = 275
MESSAGE_REMOVE_DELAY = 30
folder = 'leveling'
level_json = 'exp_' + str(MAX_LEVEL) + '.json'
dir_path = os.path.dirname(os.path.realpath(__file__))
AUTH_UID = 164900704526401545
up_arrow = '↑'
down_arrow = '↓'
flat_arrow = '-'
time_string_format = '%Y/%m/%d'

class Maplexp(commands.Cog):
    '''
        Maplexp 紀錄楓之谷等級&經驗值
    '''
    def __init__(self, bot):
        self.bot = bot
        with open(os.path.join(dir_path, folder, level_json)) as j:
            self.level_chart = json.load(j)
        self.total_net = sum(self.level_chart.values())
        self.config = Config.get_conf(self, identifier=int(str(AUTH_UID)+'001'),  force_registration=True)
        self.base_time = datetime.timestamp(datetime.strptime('1900/01/01', time_string_format))
        self.default_profile = {
            'net_exp' : 0,
            'avg_exp' : 0.0,
            'date' : self.base_time,
            'aim' : False,
            'pfp' : False
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
        net = data_d['net_exp']
        level, exp = self._net_levelexp(net)
        avg_exp = data_d['avg_exp']
        req = self.level_chart[str(level)]
        exp_perc = round((exp/req)*100, 2) if req != 0 else 0.0
        try:
            aim = data_d['aim']
        except KeyError:
            aim = False
        try:
            pfp = data_d['pfp']
        except KeyError:
            pfp = False


        footer_text = f'''最後更新日期：{datetime.fromtimestamp(data_d['date']).strftime(time_string_format)}'''
        e = discord.Embed(
            description = title,
            color = usr_c
        )
        e.add_field(name='名稱', value=name, inline=True)
        e.add_field(name='等級', value=level, inline=True)
        e.add_field(name='經驗值', value=f'{exp:,} ({exp_perc:.2f}%)', inline=False)
        if aim:
            e.add_field(name='目標等級%', value=f'{(net/aim)*100:.2f}%', inline=True)

            diff = aim - net
            if avg_exp != 0:
                day_req = round(diff/avg_exp+.5)
                try:
                    estimate_date = datetime.now() + timedelta(days=day_req)
                    val = estimate_date.strftime(time_string_format)
                except OverflowError:
                    val = '有生之年不可能'
            else:
                val = '未知'

            footer_text = f'預計完成：{val}\n' + footer_text
        e.add_field(name='平均經驗成長', value=f'{round(avg_exp):,}', inline=True)

        if pfp:
            e.set_thumbnail(url=pfp)

        e.set_footer(text=footer_text)

        return e

    def _net_levelexp(self, net_val: int) -> tuple:
        ''' Converts net to level, exp, req
        parameters : net_exp
        return : level, exp, xp_req
        '''
        for key in range(MAX_LEVEL+1):
            xp_req = self.level_chart[str(key)]
            if xp_req == net_val:
                return key+1, 0
            if xp_req > net_val:
                return key, net_val
            net_val -= xp_req

    async def _levelexp_net(self, ctx, level: str, exp: str) -> int:
        ''' Converts level, exp to net
        parameters : level, exp
        return : net_exp
        '''
        try:
            if not (level.isdigit() and int(level) in range(MAX_LEVEL+1)):
                raise ValueError('等級')
            req = self.level_chart[level]
            if '.' in exp or '%' in exp:
                exp = float(exp.strip('%'))
                if exp > 100.1:
                    raise ValueError('經驗值')
                exp = round((exp*req)/100)
            else:
                if int(exp) > req:
                    raise ValueError('經驗值')
            if int(exp) < 0:
                raise ValueError('經驗值')
        except ValueError as verr:
            await self._error_out_of_range(ctx, verr)
            return False

        level = int(level)
        exp = int(exp)

        net = 0
        for key in range(MAX_LEVEL+1):
            if int(key) == level:
                return net + exp
            net += self.level_chart[str(key)]

    async def _remove_after_seconds(self, message, second):
        await asyncio.sleep(second)
        # await message.delete()

    async def _error_char_not_found(self, ctx, name: str):
        err = await ctx.send(f'{name}, 查無角色名稱資料!')
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

        exp_growth = 0
        new_avg = 0.0
        old_net = 0
        net = await self._levelexp_net(ctx, level, exp)
        aim = False
        if net is False:
            await ctx.send('經驗錯誤，請聯繫作者')
            return

        async with self.config.user(ctx.author).usr_d() as udc:
            # update dict net_exp, avg_exp, date
            try:
                old_net = udc[char]['net_exp']
                if old_net > net:
                    await ctx.send('欸，你不可以降...\n如需重置等級，可以用`>m reset char [角色名稱]`')
                    return
                # exp_growth = net - udc[char]['net_exp']
                udc[char]['net_exp'] = net # update net
                old_date = udc[char]['date']
                if old_date != self.base_time:
                    date_td = datetime.now() - datetime.fromtimestamp(old_date)
                    new_avg = round((net - old_net)/(date_td.total_seconds()/86400)) # 86400 is the total seconds in a day
                    updated_avg = round(((udc[char]['avg_exp']+new_avg)/2), 2)
                    udc[char]['avg_exp'] = updated_avg
                else:
                    new_avg = 0

                udc[char]['date'] = datetime.timestamp(datetime.now())
                try:
                    aim = udc[char]['aim']
                except KeyError:
                    aim = False
            except KeyError:
                await self._error_char_not_found(ctx, char)
                return


        old_level, old_exp = self._net_levelexp(old_net)
        level, exp = self._net_levelexp(net)
        old_req = self.level_chart[str(old_level)]
        req = self.level_chart[str(level)]

        growth_perc = 0
        if level == old_level:
            growth = exp - old_exp
            growth_perc = round((growth/req)*100, 2) if req != 0 else 0.0

        elif level > old_level:
            growth_perc += (old_req-old_exp)/old_req if old_req != 0 else 0
            growth_perc += (exp)/req if req != 0 else 0
            growth_perc += (level - old_level) - 1
            growth_perc = round(growth_perc*100, 2)

        elif level < old_level:
            growth_perc += (old_exp)/old_req if old_req != 0 else 0
            growth_perc += (req-exp)/req if req != 0 else 0
            growth_perc += (old_level - level) - 1
            growth_perc = -(round(growth_perc*100, 2))

        else:
            await ctx.send('Unknown error L222. check logs')
            log.debug(f'level:{old_level}|{level}, exp:{old_exp}|{exp}, req:{old_req}|{req}')
            return

        exp_growth = net - old_net

        usr_dict = await self.config.user(ctx.author).usr_d() # refesh usr_dict

        e = self._dict_to_embed(
            title = ctx.author.name+'的角色資料更新',
            name = char,
            data_d = usr_dict[char],
            usr_c = ctx.author.color
        )
        val = exp_growth
        symbol = up_arrow if val > 0 else flat_arrow if val == 0 else down_arrow
        e.add_field(name="經驗成長幅度", value=f'{exp_growth:,} ({growth_perc:,.2f}%) {symbol}', inline=False)
        if aim:
            val = exp_growth/aim
            e.add_field(name='目標進度更新', value=f'{val*100:.2f}% {symbol}', inline=True)
        e.add_field(name="本次成長(經驗/日)", value=f'{new_avg:,}', inline=True)


        await ctx.send(embed=e)
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)
        return

    @commands.command(name='maplexp', aliases=['exp', 'xp'])
    @commands.bot_has_permissions(add_reactions=True)
    async def _exp(
        self, ctx: commands.Context,
        user: Optional[discord.User],
        *, argv: Optional[str]
        ):
        '''
            更新角色經驗值
            使用方式：[p]maplexp <等級> <經驗值>
            - 經驗值可以為百分比(12.42%)或是整數(34593402)

            其他使用:
                    [p]maplexp                      - 顯示我的資訊
                    [p]maplexp <角色>                - 查看我的角色資料
                    [p]maplexp <使用者名稱>           - 查看對方資料
                    [p]maplexp <使用者名稱> <角色>     - 查看對方角色資料
                    [p]maplexp <角色> <等級> <經驗值>  - 更新角色經驗值
        '''

        if user is not None:
            if argv is None:
                await self._show_info(ctx, user=user)
                return
            else:
                await self._show_info(ctx, char=argv, user=user)
                return

        elif argv is not None:
            args = argv.split()
            if len(args) == 1:
                char = args[0]
                await self._show_info(ctx, char=char)
                return
            elif len(args) == 2:
                level = args[0]
                exp = args[1]
                await self._update(ctx, level=level, exp=exp)
                return
            elif len(args) == 3:
                char = args[0]
                level = args[1]
                exp = args[2]
                await self._update(ctx, level=level, exp=exp, char=char)
                return

        elif argv is None and user is None:
            await self._show_info(ctx)
            return

        # if not returned #
        await ctx.send_help()
        return


    @commands.group(name='maple', aliases=['m'])
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    async def commands_maple(self, ctx):
        '''
            楓之谷等級經驗資料
        '''
        pass

    @commands_maple.command(name='info', hidden=True)
    async def _show_info(self, ctx, char: str = None, user: discord.User = None):
        '''
            顯示角色資訊
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
            title = str(user.name)+'的玩家資料',
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
        date = datetime.now().strftime(time_string_format),
        user: discord.User = None):
        '''
            新增角色資料
            使用方式：[p]maple create <角色名稱> <等級> <經驗值> [創角日期]
            - 日期格式為：%Y/%m/%d (例：1996/11/30)
        '''
        user = await self._user_check(ctx, user)
        if user is False:
            return

        net = await self._levelexp_net(ctx, level=level, exp=exp)
        if net is False:
            return

        async with self.config.user(user).usr_d() as ud:
            ud[char] = self.default_profile
            ud[char]['net_exp'] = net
            ud[char]['date'] = datetime.timestamp(datetime.strptime(date, time_string_format))

        if await self.config.user(user).ptr_d() == '':
            await self.config.user(user).ptr_d.set(char)

        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands_maple.command(name='delete', aliases=['d', 'del'])
    async def maple_delete(self, ctx, char: str, user: discord.User = None):
        '''
            刪除指定角色資料
            使用方式：[p]maple delete <角色名稱>
        '''
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
            使用方式：[p]mapleset list [@使用者]
        '''
        if user is None:
            user = ctx.author

        u_size = 0
        sum_level = 0
        char_list = list()
        async with self.config.user(user).usr_d() as ud:
            u_size = len(ud)
            for item in ud:
                date = datetime.fromtimestamp(ud[item]['date']).strftime(time_string_format)
                net = ud[item]['net_exp']
                level, exp = self._net_levelexp(net)
                req = self.level_chart[str(level)]
                exp = (exp/req)*100 if req != 0 else 0.0

                char_list.append((net, f'{level}({exp:.2f}%)', str(item), str(date)))
                sum_level += level

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
        char_list.sort(reverse=True)
        u_name = str()
        u_level = str()
        u_date = str()

        for item in char_list:
            u_name += str(item[2])+'\n'
            u_level += str(item[1])+'\n'
            u_date += str(item[3])+'\n'

        e.add_field(name='角色名稱', value=u_name, inline=True)
        e.add_field(name='等級', value=u_level, inline=True)
        e.add_field(name='最後更新時間', value=u_date, inline=True)
        e.set_footer(text=f'平均等級：{round(sum_level/u_size)}     總等級：{sum_level}')

        await ctx.send(embed=e)
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands_maple.group(name='set')
    @commands.bot_has_permissions(add_reactions=True)
    async def maple_set(self, ctx):
        '''
            楓之谷資料相關設定
        '''
        pass

    @maple_set.command(name='default', aliases=['d'])
    async def maple_set_default(self, ctx, char: str, user: discord.User = None):
        '''
            設定預設角色
            使用方式：[p]maple set default <角色名稱>
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

    @maple_set.command(name='name', aliases=['ign', 'id'])
    async def maple_set_name(self, ctx, o_id, n_id, user: discord.User = None):
        '''
            設定角色名稱
            使用方式：[p]maple set name <舊角色名稱> <新角色名稱>
        '''
        user = await self._user_check(ctx, user)
        if user is False:
            return

        try:
            async with self.config.user(user).usr_d() as ud:
                ud[n_id] = ud.pop(o_id)
        except KeyError:
            await ctx.send('找不到該角色名稱')
            await ctx.send_help()
            return

        ptr = await self.config.user(user).ptr_d()
        if o_id == ptr:
            await self.config.user(user).ptr_d.set(n_id)

        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @maple_set.command(name='levelexp', hidden=True)
    async def maple_set_setlevelexp(
        self, ctx: commands.Context,
        level: str, exp: str,
        char: str = None,
        user: discord.User = None
        ):
        '''
            設定等級及經驗值
            使用方式：[p]mapleset levelexp <等級> <經驗值>
        '''
        user = await self._user_check(ctx, user)
        if user is False:
            return
        if char is None:
            char = await self.config.user(user).ptr_d()


        net = await self._levelexp_net(ctx, level=level, exp=exp)
        if net is False:
            return

        async with self.config.user(user).usr_d() as ud:
            ud[char]['net_exp'] = net

        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @maple_set.command(name='aim')
    async def maple_set_aim(self, ctx, target_level: Optional[int], char: Optional[str]):
        '''
            設定目標等級 空白或是0可以移除
            [p]maple set aim <目標等級> [角色名稱]
        '''
        if char is None:
            char = await self.config.user(ctx.author).ptr_d()

        target_level = 0 if target_level is None else target_level

        if target_level not in range(0, MAX_LEVEL+1):
            await self._error_out_of_range(ctx, '目標等級')
            return

        async with self.config.user(ctx.author).usr_d() as udc:
            if target_level == 0:
                target_level = False
                net_target = False
            else:
                aim_net = 0
                for k in self.level_chart:
                    if int(k) == target_level:
                        break
                    aim_net += self.level_chart[k]
                net_target = aim_net

            try:
                udc[char]['aim'] = net_target
            except KeyError:
                await self._error_char_not_found(ctx, char)
                return

        await ctx.tick()
        if target_level:
            await ctx.send(f'設定{char}的目標等級為{target_level}等')
        else:
            await ctx.send(f'移除了{char}的目標等級')

    @maple_set.command(name='image')
    async def maple_set_image(self, ctx, link :str, char: Optional[str]):
        '''
            設定角色圖
            使用方式：[p]maple set image <圖片連結> [角色名稱]
            注意! 圖片連結需要為.png .jpg或是其他圖片檔結尾

            捏角色連結在：https://maples.im/
            使用方式去問小佑#8565
        '''
        if char is None:
            char = await self.config.user(ctx.author).ptr_d()

        if link is None:
            try:
                link = ctx.message.attachments[0].url
            except:
                link = None

        async with self.config.user(ctx.author).usr_d() as udc:
            udc[char]['pfp'] = link

        await ctx.tick()

    @commands_maple.group(name='reset')
    async def maple_reset(self, ctx):
        '''
            清除或是重置資料
        '''
        pass

    @maple_reset.command(name='average')
    async def maple_set_reset_avg(
        self,
        ctx: commands.Context,
        char: Optional[str],
        user: Optional[discord.User]
        ):
        '''
            重置日平均
            使用方式：[p]maple reset average <角色名稱>
        '''
        user = await self._user_check(ctx, user)
        if user is False:
            return
        if char is None:
            char = await self.config.user(user).ptr_d()

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
    @maple_reset.command(name='mydata')
    async def maple_set_reset_mydata(self, ctx):
        '''
            移除你的使用者資料
            使用方式：[p]maple reset mydata
        '''
        verify = await ctx.send('確定要移除你的使用者資料嗎？')
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

    @maple_reset.command(name='char')
    async def maple_set_reset_char(
        self,
        ctx: commands.Context,
        char: Optional[str],
        user: Optional[discord.User]
        ):
        '''
            重置角色經驗等級進度
            [p]maple reset char [角色名稱]
        '''
        user = await self._user_check(ctx, user)
        if user is False:
            return
        if char is None:
            char = await self.config.user(user).ptr_d()

        verify = await ctx.send(f'確定要去重置角色\'{char}\'嗎?')
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
            ud[char]['net_exp'] = 0
            ud[char]['aim'] = False
            ud[char]['pfp'] = False
            ud[char]['avg_exp'] = 0.0
            ud[char]['date'] = self.base_time
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)

    @commands.bot_has_permissions(add_reactions=True)
    @maple_reset.command(name='alluserdata', hidden=True)
    async def maple_set_reset_alluserdata(self, ctx):
        '''
            移除所有使用者資料 (擁有者限定)
            使用方式：[p]maple reset alluserdata
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

        await self.config.clear_all_users()
        await ctx.tick()
        await self._remove_after_seconds(ctx.message, MESSAGE_REMOVE_DELAY)


    @commands.command(name='maplend', hidden=True)
    @checks.admin()
    async def maple_backend(self, ctx, user: discord.User = None):
        '''
            管理員後端
        '''
        id_list = list()
        if user is not None:
            data = await self.config.user(user)()
            await ctx.send(data)
            return
        else:
            users_d = await self.config.all_users()
            for usr_id in list(users_d.keys()):
                user = await self.bot.get_or_fetch_user(usr_id)
                id_list.append(user)

            await ctx.send(f'目前使用者數量：{len(id_list)}')
            import random
            await ctx.send(f'使用者列表：{[id.name for id in id_list]}')
            result = await ctx.send(f'隨機抽：{random.choice(id_list)}')

    @commands.command(name='xpraffle')
    #@checks.admin_or_permissions(administrator=True)
    async def maple_raffle(
        self,
        ctx: commands.Context,
        winner: Optional[int]
        ):
        '''
            xp 抽獎系統
        '''
        usr_l = []
        users_d = await self.config.all_users()
        for usr_id in list(users_d.keys()):
            user = await self.bot.get_or_fetch_user(usr_id)
            usr_l.append(user.__str__())

        

        import random

        if winner is None:
            winner = 1
            
        if winner > len(usr_l):
            await ctx.send(f'抽獎人數超過總人數 {len(usr_l)}... ')
            return

        await ctx.send(f'Maplexp 隨機抽 {winner} 位')
        result = await ctx.send(f'開始隨機抽獎...')
        win_res = ''

        rand = random.randint(5, 30) # n/rand sleep time
        for n in range(rand):
            choice = random.sample(usr_l, k = winner)
            win_res = ' | '.join(choice)
            if n == rand:
                break
            await result.edit(content=win_res)
            await asyncio.sleep(int(n/rand)+1)

        await result.edit(content='```'+win_res+'```')


    @commands.command(name='fuckmylife', hidden=True)
    @checks.is_owner()
    async def fuckmesideways(self, ctx, user: discord.User, item: str):
        async with self.config.user(user)() as user_d:
            del user_d[item]

        await ctx.tick()


# end of file
