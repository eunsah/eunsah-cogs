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
        found = True
        
        user = ctx.message.author
        sid = str(ctx.guild.id)
        # get guild(server id)
        
        try:
                vc = ctx.message.author.voice.channel
                vcid = str(ctx.message.author.voice.channel.id)
        except:
                await ctx.send("{name}, Join a voice channel first.".format(name = user.name))
                found = False
        # try except block to handle if user not in vc        
        
        if found:
            await ctx.send(text_string.format(voicechannel = vc))
            await ctx.send(link_string.format(serverid = sid, voicechannelid = vcid))
