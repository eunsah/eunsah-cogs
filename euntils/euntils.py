from typing import Literal

import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.config import Config

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]


class Euntils(commands.Cog):
    """
    Utility cogs from eunsah
    """

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=164900704526401545003,
            force_registration=True,
        )

    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int) -> None:
        # TODO: Replace this with the proper end user data removal handling.
        # i don't think i will
        super().red_delete_data_for_user(requester=requester, user_id=user_id)
