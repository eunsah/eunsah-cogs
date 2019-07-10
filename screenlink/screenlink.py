import discord
from redbot.core import commands

link_string = ['https://discordapp.com/channels/{serverid}/{voicechannelid}']

class ScreenLink(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def screenlink(self, ctx):
        """
            Creates a screenlink for voicechannel
            
        """

        msg = " "
        user = ctx.message.author
        serverid = ctx.guild.id
        voicechannelid = ctx.voicechannel.id
        await ctx.send(serverid+" : "+voicechannelid)
	


#        if victim.id == self.bot.user.id:
  #          await ctx.send("I refuse to kill myself!")
   #         
    #    elif victim.id == user.id:            
     #       await ctx.send(choice(kill_list).format(victim = user.display_name, killer = self.bot.user.display_name))
#
 #       else:
#            await ctx.send(choice(kill_list).format(victim = victim.display_name, killer = user.display_name))
