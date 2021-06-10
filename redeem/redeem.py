from typing import Literal
from time import time
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

    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int) -> None:
        super().red_delete_data_for_user(requester=requester, user_id=user_id)


    @commands.guild_only()
    @commands.command(name='redeem')
    @commands.bot_has_permissions(add_reactions=True, manage_messages=True)
    async def redeem(self, ctx: commands.Context, title: str, *codes: str):
        '''
            help message here
        '''
        await ctx.message.delete()

        content_0 = f'{ctx.author} 提供了{title}序號\n剩餘 '
        content_1 = f' 組，反應{self.lock_emoji}來領取'
        content = content_0 + "{}" + content_1

        message = await ctx.send(content.format(codes.__len__()))
        await message.add_reaction(self.lock_emoji)

        async with self.config.redeem() as redeem:
            redeem[str(message.id)] = {
                'msg' : [ctx.channel.id, message.id],
                'content' : content,
                'codes' : codes,
                'time' : time(),
                'leech' : {}
            }

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        msg_id =  str(reaction.message.id)
        msg_list = await self.config.redeem()
        msg_list = list(msg_list.keys())
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
                await msg.edit(content=redeem[msg_id]['content'].format(redeem[msg_id]['codes'].__len__()))
                await user.send(f'序號：{rc}')

    @commands.command(name='redeemed')
    @checks.admin_or_permissions()
    async def redeemed(self, ctx: commands.Context, message: discord.Message):
        msg_id =  str(message.id)
        msg_list = await self.config.redeem()
        msg_list = list(msg_list.keys())
        if msg_id in msg_list and ctx.author.id != self.bot.user.id:
            async with self.config.redeem() as redeem:
                await ctx.send(content=redeem[msg_id]['leech'])


    @commands.command(name = 'devredeem')
    @checks.is_owner()
    async def devredeem(self, ctx: commands.Context):
        async with self.config.redeem() as redeem:
            await ctx.send(redeem)