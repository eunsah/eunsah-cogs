import discord
from redbot.core import commands

text_string = "Join {voicechannel} and click on this link : "
link_string = "<https://discordapp.com/channels/{serverid}/{voicechannelid}>"

class Screenshare(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def screenshare(self, ctx):
        """
            Creates a screenshare link for voicechannel
            
        """

        user = ctx.message.author
        vc = ctx.message.author.voice.channel
        sid = str(ctx.guild.id)
        vcid = str(ctx.message.author.voice.channel.id)
        #await ctx.send(voicechannelid)
        await ctx.send(text_string.format(voicechannel = vc) + link_string.format(serverid = sid, voicechannelid = vcid))
	


#        if victim.id == self.bot.user.id:
  #          await ctx.send("I refuse to kill myself!")
   #         
    #    elif victim.id == user.id:            
     #       await ctx.send(choice(kill_list).format(victim = user.display_name, killer = self.bot.user.display_name))
#
 #       else:
#            await ctx.send(choice(kill_list).format(victim = victim.display_name, killer = user.display_name))