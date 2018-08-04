import discord
from discord.ext import commands
import psycopg2
import os
from datetime import datetime
import asyncio

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
        [user]'s profile picture. Sends your profile picture if [user] not specified.
        w.pfp [user]
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
                if user.lower() in (curr_member.name.lower() + "#" + curr_member.discriminator.lower()):
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
        Get your daily Coins!
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
            await ctx.send("You got 200 Coins!")
        else:
            delta = datetime.utcnow() - timestamp
            if delta.total_seconds() > 86400:
                balance += 200
                timestamp = datetime.utcnow()
                c.execute(""" UPDATE users
                            SET daily_time = %s, balance = %s
                            WHERE ID = %s; """, (timestamp, balance, str(ctx.message.author.id)))
                await ctx.send("You got 200 Coins!")
            else:
                time_remaining = 86400 - int(delta.total_seconds())
                hours, remainder = divmod(int(time_remaining), 3600)
                minutes, seconds = divmod(remainder, 60)
                await ctx.send("You can claim daily coins again in " + f"{hours}h {minutes}m {seconds}s")
        conn.commit()
        conn.close()

    @commands.command()
    async def profile(self, ctx, *, user: str=None):
        '''
        [user]'s profile. Sends your profile picture if [user] not specified.
        w.profile [user]
        '''
        def level_currxp_nextxp(xp):
            import math
            level = math.floor(0.25*((xp+16)**0.5))
            curr_xp = ((level*4)**2)-16
            next_level_xp = (((level+1)*4)**2)-16
            return level, curr_xp, next_level_xp

        def get_profile(member):
            try:
                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                c = conn.cursor()
                c.execute(""" UPDATE users SET username = %s
                                WHERE ID = %s
                                AND username != %s; """, (member.name, str(member.id), member.name))
                c.execute(""" SELECT username, xp, balance FROM users
                            WHERE ID = %s; """, (str(member.id), ))
                profile_lst = c.fetchone()
                xp = int(profile_lst[1])
                level, curr_xp, next_xp = level_currxp_nextxp(xp)
                balance = profile_lst[2]
                embed = discord.Embed(title=f"Level {level}", description=f"{curr_xp}/{next_xp}XP", color=member.color)
                embed.add_field(name="Coins", value=balance)
                embed.set_author(name=member.name)
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
                if user.lower() in (curr_member.name.lower() + "#" + curr_member.discriminator.lower()):
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

    @commands.command()
    async def pay(self, ctx, user, amount: int=None):
        '''
        Pay another use <amount> of coins.
        w.pay <@user> <amount>
        '''
        # checking if user has sufficient balance
        if len(ctx.message.mentions) == 0:
            await ctx.send("You must mention a user to pay!")
            return

        receiver = ctx.message.mentions[0]
        if receiver.bot:
            await ctx.send("You can't pay a bot!")
            return

        if amount is None:
            await ctx.send("You must specify the amount of payment!")
            return

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT balance FROM users
                    WHERE ID = %s; """, (str(ctx.author.id), ))
        payer_balance = int(c.fetchone()[0])
        if payer_balance < amount:
            await ctx.send("You don't have enough coins to pay that much!")
            conn.close()
            return

        confirm_msg = await ctx.send(f"{ctx.author.mention} Are you sure you want to pay {receiver.mention} {amount} coins?\nType \"w.confirm\" to confirm payment.")

        def check_confirm(m):
            return m.author == ctx.author

        confirmed = False
        while confirmed is False:
            try:
                confirm = await self.bot.wait_for('message', check=check_confirm, timeout=20)
            except asyncio.TimeoutError:
                await confirm_msg.edit(content=confirm_msg.content + "\n*The payment has timed out!*")
                return
            else:
                if confirm.content == 'w.confirm':
                    payer_balance -= amount
                    c.execute(""" SELECT balance FROM users
                                WHERE ID = %s; """, (str(receiver.id),))
                    receiver_balance = int(c.fetchone()[0])
                    receiver_balance += amount
                    c.execute(""" UPDATE users SET balance = %s
                                WHERE ID = %s; """, (str(payer_balance), str(ctx.author.id)))
                    c.execute(""" UPDATE users SET balance = %s
                                WHERE ID = %s; """, (str(receiver_balance), str(receiver.id)))
                    await ctx.send(f"Payment confirmed. {ctx.author.mention} has paid {receiver.mention} {amount} coins.")
                    confirmed = True
        conn.commit()
        conn.close()

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