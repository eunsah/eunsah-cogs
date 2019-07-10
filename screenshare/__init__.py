from .screenshare import Screenshare


def setup(bot):
    ss = Screenshare(bot)
    bot.add_cog(ss)
