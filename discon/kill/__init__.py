from .kill import Kill


def setup(bot):
    n = Kill(bot)
    bot.add_cog(n)
