import discord
from discord.ext import commands
import psycopg2
import os

DATABASE_URL = os.environ['DATABASE_URL']


class Brawlhalla:
    '''
    Commands for the to-do list.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def b(self, ctx):
        '''
        Brawlhalla commands
        '''

    @b.command()
    async def test(self, ctx):
        '''
        test
        '''
        await ctx.send(file=discord.File("http://s3.amazonaws.com/willabot-assets/images/legends/ADA_Atlantean_Ada_Black.png"))

def setup(bot):
    bot.add_cog(Brawlhalla(bot))