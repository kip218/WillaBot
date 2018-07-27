import discord
from discord.ext import commands
import psycopg2
import os
from datetime import datetime

DATABASE_URL = os.environ['DATABASE_URL']


class General:
    '''
    Commands for the bot owner.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pfp(self, ctx, *, user: str=None):
        '''
        Sends profile picture
        w.pfp [user]
        Sends your profile picture if [user] not specified.
        '''
        # gets embed msg of member's avatar
        def get_pfp(member):
            pic_url = member.avatar_url
            title = 'Profile picture of ' + str(member)
            color = member.color
            embed = discord.Embed(title=title, color=color)
            embed.set_image(url=pic_url)
            return embed

        if user is None:
            member = ctx.message.author
            embed = get_pfp(member)
            await ctx.send(embed=embed)
        elif len(ctx.message.mentions) > 0:
            member = ctx.message.mentions[0]
            embed = get_pfp(member)
            await ctx.send(embed=embed)
        else:
            lst_members = ctx.guild.members
            # loop to search name
            ind = 0
            found = False
            while found is False and ind < len(lst_members):
                curr_member = lst_members[ind]
                if user.lower() in curr_member.name.lower():
                    member = curr_member
                    found = True
                elif user.lower() in curr_member.display_name.lower():
                    member = curr_member
                    found = True
                else:
                    ind += 1
            if found is False:
                await ctx.send("Could not find user named \"" + user + "\" in the server.")
            else:
                embed = get_pfp(member)
                await ctx.send(embed=embed)

    @commands.command()
    async def daily(self, ctx):
        '''
        Get your daily Willacoins!
        w.daily
        '''
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT daily_time, balance FROM users
                    WHERE ID = %s; """, (str(ctx.message.author.id), ))
        fetch = c.fetchone()
        timestamp = fetch[0]
        balance = int(fetch[1])
        if timestamp is None:
            balance += 200
            timestamp = datetime.utcnow()
            c.execute(""" UPDATE users
                        SET daily_time = %s, balance = %s
                        WHERE ID = %s; """, (timestamp, balance, str(ctx.message.author.id)))
            await ctx.send("You got 200 WillaCoins!")
        else:
            delta = datetime.utcnow() - timestamp
            if delta.total_seconds() > 86400:
                balance += 200
                timestamp = datetime.utcnow()
                c.execute(""" UPDATE users
                            SET daily_time = %s, balance = %s
                            WHERE ID = %s; """, (timestamp, balance, str(ctx.message.author.id)))
            else:
                await ctx.send("Daily WillaCoins can only be claimed once every 24 hours!")
        conn.commit()
        conn.close()

    @commands.command()
    async def profile(self, ctx, *, user: str=None):
        '''
        Your profile
        w.profile
        '''
        def get_profile(member):
            try:
                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                c = conn.cursor()
                c.execute(""" SELECT username, xp, balance FROM users
                            WHERE ID = %s; """, (str(member.id), ))
                profile_lst = c.fetchone()
                embed = discord.Embed(title="XP", description=profile_lst[1], color=member.color)
                embed.add_field(name="WillaCoins", value=profile_lst[2])
                embed.set_author(name=profile_lst[0])
                embed.set_thumbnail(url=member.avatar_url)
                conn.commit()
                conn.close()
            except TypeError:
                print("get_profile Error")
                return
            else:
                return embed

        if user is None:
            member = ctx.message.author
            try:
                embed = get_profile(member)
                await ctx.send(embed=embed)
            except commands.CommandInvokeError:
                await ctx.send("Error")
                return
        elif len(ctx.message.mentions) > 0:
            member = ctx.message.mentions[0]
            if not member.bot:
                try:
                    embed = get_profile(member)
                    await ctx.send(embed=embed)
                except:
                    await ctx.send("Could not find user.")
                    return
            else:
                await ctx.send("Bots don't have profiles!")
        else:
            lst_members = ctx.guild.members
            # loop to search name
            ind = 0
            found = False
            while found is False and ind < len(lst_members):
                curr_member = lst_members[ind]
                if user.lower() in curr_member.name.lower():
                    member = curr_member
                    found = True
                elif user.lower() in curr_member.display_name.lower():
                    member = curr_member
                    found = True
                else:
                    ind += 1
            if found is False:
                await ctx.send("Could not find user named \"" + user + "\" in the server.")
            else:
                if member.bot:
                    await ctx.send(member.mention + " is a bot. Bots don't have profiles!")
                else:
                    try:
                        embed = get_profile(member)
                        await ctx.send(embed=embed)
                    except:
                        await ctx.send("Could not find user name \"" + user + "\" in the database.")
                        return

    @commands.group()
    async def todo(self, ctx):
        '''
        To-do list commands
        w.todo <subcommand>
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommands: list, add, remove, check")

    @todo.command()
    async def list(self, ctx):
        '''
        Your to-do list
        w.todo list
        '''
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT todo_list FROM users
                    WHERE ID = %s; """, (str(ctx.message.author.id), ))
        todo_list = c.fetchone()[0]
        if todo_list is None:
            await ctx.send("Your to-do list is empty!")
        else:
            embed = discord.Embed(title=str(ctx.message.author.name) + "'s to-do list", color=0x48d1cc)
            for i in range(len(todo_list)):
                embed.add_field(name="/u200b", value=str(i+1) + ". " + todo_list[i], inline=False)
            await ctx.send(embed=embed)
        conn.commit()
        conn.close()

    @todo.command()
    async def add(self, ctx, *, task):
        '''
        Adds to your to-do list
        w.todo add <task>
        '''
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" UPDATE users
                    SET todo_list = array_append(todo_list, %s) 
                    WHERE ID = %s; """, (str(task), str(ctx.message.author.id)))
        conn.commit()
        conn.close()

    @todo.command()
    async def remove(self, ctx, num):
        '''
        Removes a task from your to-do list
        w.todo remove <task number>
        '''
        try:
            num = int(num)
        except:
            await ctx.send("You must input an integer.")
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT todo_list FROM users
                    WHERE ID = %s; """, (str(ctx.message.author.id), ))
        todo_list = c.fetchone()[0]
        if 1 <= num <= len(todo_list):
            task_to_remove = todo_list[num-1]
            c.execute(""" UPDATE users
                        SET todo_list = array_remove(todo_list, %s)
                        WHERE ID = %s; """, (task_to_remove, str(ctx.message.author.id)))
        else:
            await ctx.send("You must input an integer between 1 and " + str(len(todo_list)))


# DON'T USE EVAL IT'S DANGEROUS
    # @commands.command(aliases=["math"])
    # async def calc(self, ctx, *, equation: str=None):
    #     '''
    #     Calculator for simple arithmetic operations (+, -, x, /, ^)
    #     w.calc <algebraic expression>
    #     A quick simple calculator for when you're feeling lazy.
    #     '''
    #     equation = equation.replace("^", "**")
    #     equation = equation.replace("x", "*")
    #     try:
    #         res = eval(equation)
    #     except SyntaxError:
    #         await ctx.send("Invalid input.")
    #     else:
    #         await ctx.send(res)


def setup(bot):
    bot.add_cog(General(bot))