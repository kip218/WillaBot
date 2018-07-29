import psycopg2
from discord.ext import commands
import random
import os
import challonge
import discord

DATABASE_URL = os.environ['DATABASE_URL']


class Owner:
    '''
    Commands for the bot owner.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def shutdown(self, ctx):
        '''
        Shut down WillaBot.
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
        Reset all tables from database.
        w.reset db
        '''
        if await self.bot.is_owner(ctx.message.author):
            await ctx.send("Resetting database...")
            # conn = psycopg2.connect(database='willabot_db')
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute("DELETE FROM tournaments;")
            c.execute("DELETE FROM users;")
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
    async def drop(self, ctx):
        '''
        Drop all tables from database and recreate them.
        w.reset drop
        '''
        if await self.bot.is_owner(ctx.message.author):
            await ctx.send("Dropping tables...")
            # conn = psycopg2.connect(database='willabot_db')
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute("DROP TABLE IF EXISTS tournaments, users;")
            await ctx.send("Tables dropped.")
            await ctx.send("Recreating tables...")

            # Tables must be exactly same as the ones in run.py
            create_tournaments_table = """ CREATE TABLE IF NOT EXISTS tournaments (
                                        ID text PRIMARY KEY,
                                        url text NOT NULL,
                                        name text NOT NULL,
                                        creator_id text NOT NULL,
                                        admin_list text[]
                                        ); """
            create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                        ID text PRIMARY KEY,
                                        username text NOT NULL,
                                        xp text NOT NULL,
                                        balance text NOT NULL,
                                        tournament_url_list text[],
                                        todo_list text[],
                                        daily_time timestamp
                                        ); """

            c.execute(create_tournaments_table)
            c.execute(create_users_table)
            conn.commit()
            conn.close()
            await ctx.send("Tables created.")
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
        Reset challonge.
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
