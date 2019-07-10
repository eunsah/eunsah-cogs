import discord
from redbot.core import commands

link_string = ['https://discordapp.com/channels/{serverid}/{voicechannelid}']

class Screenshare(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def screenshare(self, ctx):
        """
            Creates a screenshare link for voicechannel
            
        """

        msg = " "
        user = ctx.message.author
        serverid = ctx.guild.id
        voicechannelid = ctx.message.author.voice.channel
        await ctx.send(str(serverid) + " : " + voicechannelid)
	


#        if victim.id == self.bot.user.id:
  #          await ctx.send("I refuse to kill myself!")
   #         
    #    elif victim.id == user.id:            
     #       await ctx.send(choice(kill_list).format(victim = user.display_name, killer = self.bot.user.display_name))
#
 #       else:
#            await ctx.send(choice(kill_list).format(victim = victim.display_name, killer = user.display_name))
