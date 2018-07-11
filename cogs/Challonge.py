import discord
from discord.ext import commands
import challonge


class Challonge:
    '''
    Commands for the bot owner.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pfp(self, ctx, *, user: str=None):
        '''
        Sends profi
        '''


def setup(bot):
    bot.add_cog(Challonge(bot))