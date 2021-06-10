from typing import Literal
from time import time
import asyncio
from collections import defaultdict

import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.config import Config

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]


class Redeem(commands.Cog):
    """
    Redeem code without struggle
    """

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.lock_emoji = '🔒'
        self.config = Config.get_conf(
            self,
            identifier=164900704526401545004,
            force_registration=True,
        )
        default_global = {
            'redeem' : {}
        }

        self.config.register_global(**default_global)

        self.redeem_task = self.bot.loop.create_task(self._redeem_handler())

    def cog_unload(self):
        self.redeem_task.cancel()

    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int) -> None:
        super().red_delete_data_for_user(requester=requester, user_id=user_id)

    @commands.guild_only()
    @commands.command(name='redeem')
    @commands.bot_has_permissions(add_reactions=True, manage_messages=True)
    async def redeem(self, ctx: commands.Context, title: str, *codes: str):
        '''
            # 贈送序號指令
            使用方式：[p]redeem <名稱> <序號1 序號2...>
            ※序號請用空白隔開
        '''
        await ctx.message.delete()

        content = f'{ctx.author}提供{title}序號 {codes.__len__()} 組\n目前剩餘 {codes.__len__()} 組，反應{self.lock_emoji}來領取'

        message = await ctx.send(content)
        await message.add_reaction(self.lock_emoji)

        async with self.config.redeem() as redeem:
            redeem[str(message.id)] = {
                'msg' : [ctx.channel.id, message.id],
                'author' : str(ctx.author),
                'title' : title,
                'count' : codes.__len__(),
                'codes' : codes,
                'time' : time(),
                'leech' : {}
            }

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        msg_id =  str(reaction.message.id)
        msg_list = await self.config.redeem()
        msg_list = list(msg_list.keys())
        remain = int()
        if reaction.emoji == self.lock_emoji and msg_id in msg_list and user.id != self.bot.user.id:
            async with self.config.redeem() as redeem:
                leech = redeem[msg_id]['leech']
                if str(user.id) in leech:
                    leech[str(user.id)] += 1
                else:
                    leech[str(user.id)] = 1
                rc = redeem[msg_id]['codes'].pop()
                ch = self.bot.get_channel(redeem[msg_id]['msg'][0])
                msg = await ch.fetch_message(redeem[msg_id]['msg'][1])
                remain = redeem[msg_id]['codes'].__len__()
                await user.send(f'獲得了{redeem[msg_id]["title"]}序號：{rc}')
                if remain != 0:
                    await msg.edit(content=f'{redeem[msg_id]["author"]}提供{redeem[msg_id]["title"]}序號 {redeem[msg_id]["count"]} 組\n目前剩餘 {remain} 組，反應{self.lock_emoji}來領取')
                else:
                    await msg.edit(content=f'{redeem[msg_id]["author"]}提供{redeem[msg_id]["title"]}序號 {redeem[msg_id]["count"]} 組\n目前已經領取完畢~ 下次請早')
                    await self._redeem_delete(msg_id)



    @commands.command(name='redeemed')
    @checks.admin_or_permissions()
    async def redeemed(self, ctx: commands.Context, message: discord.Message):
        msg_id =  str(message.id)
        msg_list = await self.config.redeem()
        msg_list = list(msg_list.keys())
        if msg_id in msg_list and ctx.author.id != self.bot.user.id:
            async with self.config.redeem() as redeem:
                await ctx.send(content=redeem[msg_id]['leech'])

    async def _redeem_delete(self, msg_id):
        async with self.config.redeem() as redeem:
            del redeem[msg_id]

    async def _redeem_countdown(self, msg_id):
        thirtyDays = 86400*30
        redeem = self.config.redeem()
        reaminingtime = time() - redeem[msg_id]['time']
        if reaminingtime > 0:
            await asyncio.sleep(int(reaminingtime))
        await self._redeem_delete(msg_id)

    async def _redeem_handler(self):
        await self.bot.wait_until_red_ready()
        try:
            _redeem_coros = []
            rd = await self.config.redeem()
            for msg_id in rd:
                _redeem_coros.append(self._redeem_countdown(msg_id))
            await asyncio.gather(*_redeem_coros)
        except Exception:
            pass

    @commands.group(name='devredeem')
    @checks.admin_or_permissions()
    async def commands_devredeem(self, ctx: commands.Context):
        pass

    @commands_devredeem.command(name='showall')
    @checks.is_owner()
    async def devredeem_showall(self, ctx: commands.Context):
        async with self.config.redeem() as redeem:
            await ctx.send(redeem)

    @commands_devredeem.command(name='remove')
    async def devredeem_remove(self, ctx: commands.Context, msg_id: str):
        msg_list = await self.config.redeem()
        msg_list = list(msg_list.keys())
        if msg_id in msg_list:
            async with self.config.redeem() as redeem:
                del redeem[msg_id]
            await ctx.tick()