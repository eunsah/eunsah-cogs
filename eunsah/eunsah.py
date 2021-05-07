from redbot.cogs.downloader.converters import InstalledCog
from redbot.core import commands

class Eunsah(commands.Cog):
    def __init__(self, bot):
        pass

@commands.command()
@commands.max_concurrency(1)
@commands.is_owner()
async def cur(ctx, *cogs: InstalledCog):
    """Update cogs without questioning about reload"""
    ctx.assume_yes = True
    await ctx.invoke(bot.get_command("cog update"), *cogs)

return cur

