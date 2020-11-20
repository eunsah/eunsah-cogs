from .mock import Mock


def setup(bot):
    n = Mock(bot)
    bot.add_cog(n)
