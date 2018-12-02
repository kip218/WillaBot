import discord
from discord.ext import commands
import psycopg2
import os
from datetime import datetime
import asyncio

DATABASE_URL = os.environ['DATABASE_URL']


class General:
    '''
    General commands.
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
            conn.commit()
            embed_name = "You got 200 Coins!"
        else:
            delta = datetime.utcnow() - timestamp
            if delta.total_seconds() > 86400:
                balance += 200
                timestamp = datetime.utcnow()
                c.execute(""" UPDATE users
                            SET daily_time = %s, balance = %s
                            WHERE ID = %s; """, (timestamp, balance, str(ctx.message.author.id)))
                conn.commit()
                embed_name = "You got 200 Coins!"
            else:
                time_remaining = 86400 - int(delta.total_seconds())
                hours, remainder = divmod(int(time_remaining), 3600)
                minutes, seconds = divmod(remainder, 60)
                embed_name = f"You can claim daily coins again in {hours}h {minutes}m {seconds}s"
        conn.close()
        embed = discord.Embed(color=0x48d1cc)
        embed.set_author(name=embed_name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name="WillaBot Updates:", value="- Brawl (beta) has been added!\nTry it out and give feedback using \"w.report\"!\n\"w.help brawl\" for more info.")
        await ctx.send(embed=embed)

    @commands.command()
    async def profile(self, ctx, *, user: str=None):
        '''
        [user]'s profile. Sends your profile picture if [user] not specified.
        w.profile [user]
        '''
        def level_currxp_nextxp(xp):
            import math
            level = math.floor(0.25*((xp+16)**0.5))
            floor_level_xp = ((level*4)**2)-16
            curr_xp = xp - floor_level_xp
            next_level_xp_total = (((level+1)*4)**2)-16
            next_level_xp = next_level_xp_total - floor_level_xp
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
                await ctx.send(f"{member.mention} is a bot. Bots don't have profiles!")
        else:
            lst_members = []
            # loop to search name and retrieve list of members from server that match
            for guild_member in ctx.guild.members:
                curr_member = guild_member
                if user.lower() in (curr_member.name.lower() + "#" + curr_member.discriminator.lower()):
                    # inserting to prioritize member.name over member.display_name
                    lst_members.insert(0, curr_member)
                elif user.lower() in curr_member.display_name.lower():
                    lst_members.append(curr_member)
            if len(lst_members) == 0:
                await ctx.send("Could not find user named \"" + user + "\" in the server.")
            else:
                found_in_db = False
                i = 0
                while found_in_db is False and i < len(lst_members):
                    try:
                        member = lst_members[i]
                        embed = get_profile(member)
                        await ctx.send(embed=embed)
                        found_in_db = True
                    except:
                        i += 1
                        pass
                # sending error message if user not found in database
                if found_in_db is False:
                    await ctx.send("Could not find user named \"" + user + "\" in the database.")

    @commands.command(usage="<user> <amount>")
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

        if amount <= 0:
            await ctx.send("Payment amount must be positive!")
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

        confirm_msg = await ctx.send(f"{ctx.author.mention} Are you sure you want to pay {receiver.mention} {amount} coins?\nType \"w.confirm\" to confirm payment and \"w.cancel\" to cancel payment.")

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
                    await confirm_msg.edit(content=f"Payment confirmed. {ctx.author.mention} has paid {receiver.mention} {amount} coins.")
                    confirmed = True
                elif confirm.content == 'w.cancel':
                    await confirm_msg.edit(content="Payment canceled.")
                    confirmed = True
        conn.commit()
        conn.close()


def setup(bot):
    bot.add_cog(General(bot))