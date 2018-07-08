import discord
from discord.ext import commands
import random


class Owner:
    '''
    Commands for the bot owner.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def shutdown(self, ctx):
        '''
        Shut down WillaBot
        '''
        author_id = ctx.message.author.id
        if author_id == 161774631303249921:
            await ctx.send("I need to go take a shit brb")
            await self.bot.close()
        else:
            num = random.randint(0, 1)
            if num == 0:
                await ctx.send("y tho")
            elif num == 1:
                await ctx.send("no u")


def setup(bot):
    bot.add_cog(Owner(bot))
