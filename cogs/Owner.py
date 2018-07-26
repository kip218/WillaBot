import psycopg2
from discord.ext import commands
import random
import sqlite3
import challonge


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
        w.shutdown
        '''
        if await self.bot.is_owner(ctx.message.author):
            await ctx.send("I need to go take a shit brb")
            await self.bot.close()
        else:
            num = random.randint(0, 2)
            if num == 0:
                await ctx.send("y tho")
            elif num == 1:
                await ctx.send("no u")
            elif num == 2:
                await ctx.send("아니")

    @commands.group()
    async def reset(self, ctx):
        '''
        Resetting commands
        '''

    @reset.command()
    async def db(self, ctx):
        '''
        Reset 'tournaments' table from database
        w.reset db
        '''
        if await self.bot.is_owner(ctx.message.author):
            await ctx.send("Resetting database...")
            conn = psycopg2.connect(database='willabot_db')
            c = conn.cursor()
            c.execute("DELETE FROM tournaments;")
            conn.commit()
            conn.close()
            await ctx.send("Database reset.")
        else:
            num = random.randint(0, 2)
            if num == 0:
                await ctx.send("y tho")
            elif num == 1:
                await ctx.send("no u")
            elif num == 2:
                await ctx.send("아니")

    @reset.command()
    async def chal(self, ctx):
        '''
        Reset challonge
        w.reset chal
        '''
        if await self.bot.is_owner(ctx.message.author):
            await ctx.send("Resetting challonge...")
            tournaments_lst = challonge.tournaments.index()
            for tournament in tournaments_lst:
                tournament_id = tournament['id']
                challonge.tournaments.destroy(tournament_id)
            await ctx.send("Challonge reset.")
        else:
            num = random.randint(0, 2)
            if num == 0:
                await ctx.send("y tho")
            elif num == 1:
                await ctx.send("no u")
            elif num == 2:
                await ctx.send("아니")


def setup(bot):
    bot.add_cog(Owner(bot))
