import discord
from redbot.core import commands
from random import choice, randint

class Mock(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def mock(self, ctx):
        """
            Returns entered string with randomnized letter case
        """
        
