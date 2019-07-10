from .screenlink import ScreenLink


def setup(bot):
    n = ScreenLink(bot)
    bot.add_cog(n)
