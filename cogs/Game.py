from discord.ext import commands
import random
import psycopg2
import os
import asyncio
from datetime import datetime

DATABASE_URL = os.environ['DATABASE_URL']


class Game:
    '''
    Game commands.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def montyhall(self, ctx):
        '''
        The famous Monty Hall problem.
        w.montyhall
        '''
        # Check that the user isn't already playing the game
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT status FROM users WHERE ID=%s;""", (str(ctx.author.id), ))
        status_lst = c.fetchone()[0]
        if status_lst is not None:
            if "montyhall" in status_lst:
                await ctx.send("You're already in a game of montyhall!")
                conn.commit()
                conn.close()
                return
        c.execute(""" UPDATE users
                    SET status = array_append(status, %s)
                    WHERE ID = %s; """, ('montyhall', str(ctx.author.id)))
        conn.commit()
        conn.close()

        def check(m):
            return not m.author.bot and m.author == ctx.author

        options = [1, 2, 3]
        car = random.randint(1, 3)
        msg = await ctx.send("Choose a door to open (1, 2, 3)\n\n:one: :two: :three:\n:door: :door: :door:")
        answered = False
        while answered is False:
            try:
                answer = await self.bot.wait_for('message', check=check, timeout=60)
                answer = int(answer.content)
                options.remove(answer)
                options.append(answer)
            except asyncio.TimeoutError:
                await msg.edit(content=msg.content + "\n\nThe game has timed out!")
                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                c = conn.cursor()
                c.execute(""" UPDATE users
                            SET status = array_remove(status, %s)
                            WHERE ID = %s; """, ('montyhall', str(ctx.author.id)))
                conn.commit()
                conn.close()
                return
            except ValueError:
                pass
            else:
                options.remove(car)
                choose_goat = False
                while choose_goat is False:
                    reveal_goat = random.randint(1, 3)
                    if reveal_goat in options and reveal_goat != answer:
                        choose_goat = True
                options.remove(reveal_goat)
                options.append(car)
                options.remove(answer)
                emotes = ""
                for i in range(1, 4):
                    if i == answer:
                        emotes += ":arrow_down: "
                    elif i == 1:
                        emotes += ":one: "
                    elif i == 2:
                        emotes += ":two: "
                    elif i == 3:
                        emotes += ":three: "
                emotes += "\n"
                for i in range(1, 4):
                    if i == reveal_goat:
                        emotes += ":goat: "
                    else:
                        emotes += ":door: "
                await msg.edit(content="You've chosen door number " + str(answer) + ".\n\nDoor number " + str(reveal_goat) + " has been opened, revealing a goat.\n\nWould you like to switch? (y/n)\n\n" + emotes)
                answered = True
        switch_answered = False
        while switch_answered is False:
            try:
                switch = await self.bot.wait_for('message', check=check, timeout=60)
            except asyncio.TimeoutError:
                await msg.edit(content=msg.content + "\n\nThe game has timed out!")
                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                c = conn.cursor()
                c.execute(""" UPDATE users
                            SET status = array_remove(status, %s)
                            WHERE ID = %s; """, ('montyhall', str(ctx.author.id)))
                conn.commit()
                conn.close()
                return
            else:
                if switch.content.lower() == 'y':
                    answer = options[0]
                    switch_answered = True
                elif switch.content.lower() == 'n':
                    switch_answered = True
                if switch_answered is True:
                    emotes = ""
                    for i in range(1, 4):
                        if i == answer:
                            emotes += ":arrow_down: "
                        elif i == 1:
                            emotes += ":one: "
                        elif i == 2:
                            emotes += ":two: "
                        elif i == 3:
                            emotes += ":three: "
                    emotes += "\n"
                    for i in range(1, 4):
                        if i == car:
                            emotes += ":red_car: "
                        else:
                            emotes += ":goat: "
                    if answer == car:
                        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                        c = conn.cursor()
                        c.execute(""" SELECT xp, balance FROM users
                                    WHERE ID = %s; """, (str(ctx.author.id), ))
                        fetch = c.fetchone()
                        xp = int(fetch[0])
                        balance = int(fetch[1])
                        xp_increase = random.randint(10, 20)
                        balance_increase = random.randint(20, 40)
                        xp += xp_increase
                        balance += balance_increase
                        c.execute(""" UPDATE users SET xp = %s, balance = %s WHERE ID = %s; """, (xp, balance, str(ctx.author.id)))
                        conn.commit()
                        conn.close()
                        await msg.edit(content="You found the car!\n\nYou got " + str(xp_increase) + " XP and " + str(balance_increase) + " Coins.\n\n" + emotes)
                    else:
                        await msg.edit(content="You did not find the car. Try again!\n\n" + emotes)
                    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" UPDATE users
                    SET status = array_remove(status, %s)
                    WHERE ID = %s; """, ('montyhall', str(ctx.author.id)))
        conn.commit()
        conn.close()

    @commands.command()
    async def pw(self, ctx, user, bet_amount: int=None):
        '''
        The Peace War game.
        w.pw <user> <bet amount>
        '''
        if len(ctx.message.mentions) == 0:
            await ctx.send("You must mention a user to play against!")
            return

        player = ctx.author
        opponent = ctx.message.mentions[0]
        if opponent.bot:
            await ctx.send("You can't challenge a bot!")
            return

        if bet_amount is None:
            await ctx.send("You must specify a bet amount!")
            return

        # checking if both players have sufficient balance
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT balance FROM users
                    WHERE ID = %s; """, (str(player.id), ))
        player_balance = int(c.fetchone()[0])

        try:
            c.execute(""" SELECT balance FROM users
                        WHERE ID = %s; """, (str(opponent.id), ))
            opponent_balance = int(c.fetchone()[0])
        except:
            await ctx.send("Player not found in database.")
            conn.close()
            return
        else:
            if player_balance < 3*bet_amount and opponent_balance < 3*bet_amount:
                await ctx.send("Both players do not have enough Coins to play. You must have more than **triple** the bet amount to play the Peace War game.")
                conn.close()
                return
            elif player_balance < 3*bet_amount:
                await ctx.send(f"{player.name} does not have enough Coins to play. You must have more than **triple** the bet amount to play the Peace War game.")
                conn.close()
                return
            elif opponent_balance < 3*bet_amount:
                await ctx.send(f"{opponent.name} does not have enough Coins to play. You must have more than **triple** the bet amount to play the Peace War game.")
                conn.close()
                return

        challenge_msg = await ctx.send(f"{opponent.mention}! {player.mention} challenged you to a game of Peace/War! Type \"w.accept <user>\" to accept!\n\nBet amount: {bet_amount}")

        # checking if opponent accepts challenge
        def check_accept(m):
            return m.author == opponent
        accepted = False
        while accepted is False:
            try:
                accept = await self.bot.wait_for('message', check=check_accept, timeout=60)
            except asyncio.TimeoutError:
                await challenge_msg.edit(content=challenge_msg.content + "\n\nThe challenge has timed out!")
                return
            else:
                if 'w.accept' in accept.content:
                    accept_user = accept.content.replace('w.accept', '')
                    if accept_user is '':
                        await ctx.send("You must specify the user that challenged you!")
                    elif accept_user == player.mention or accept_user in player.name or accept_user in player.display_name:
                        accepted = True

        # Check that the user isn't already playing the game with the same opponent
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT status FROM users WHERE ID=%s;""", (str(player.id), ))
        player_status_lst = c.fetchone()[0]
        c.execute(""" SELECT status FROM users WHERE ID=%s;""", (str(opponent.id), ))
        opponent_status_lst = c.fetchone()[0]
        if player_status_lst is not None and opponent_status_lst is not None:
            if f"pw{opponent.id}" in player_status_lst and f"pw{player.id}" in opponent_status_lst:
                await ctx.send(f"{player.mention} and {opponent.mention} are already in a game of Peace/War!")
                conn.commit()
                conn.close()
                return
        c.execute(""" UPDATE users
                    SET status = array_append(status, %s)
                    WHERE ID = %s; """, (f'pw{opponent.id}', str(player.id)))
        c.execute(""" UPDATE users
                    SET status = array_append(status, %s)
                    WHERE ID = %s; """, (f'pw{player.id}', str(opponent.id)))
        conn.commit()
        conn.close()

        challenge_accepted = await ctx.send(f"{player.mention} {opponent.mention} Challenge accepted! Check your DMs!")

        prompt = f"The rules of the Peace War game are as follows:\n\n- If both players declare peace, both get the bet amount of Coins.\n- If you declare war while your opponent declares peace, you get triple the bet amount, while your opponent loses triple the bet amount, and vice versa.\n- If both players declare war, both lose the bet amount of Coins.\n\nType \"peace\" to declare peace and \"war\" to declare war.\n\nBet amount: {bet_amount}"
        player_prompt = await player.send(f"{prompt}\nOpponent: {opponent.name}")
        opponent_prompt = await opponent.send(f"{prompt}\nOpponent: {player.name}")

        # checking player's response
        def check_player(m):
            return m.channel == player.dm_channel

        def check_opponent(m):
            return m.channel == opponent.dm_channel

        # checking opponent's response
        player_answered = False
        opponent_answered = False
        while player_answered is False or opponent_answered is False:
            try:
                done, pending = await asyncio.wait([self.bot.wait_for('message', check=check_player, timeout=120), self.bot.wait_for('message', check=check_opponent, timeout=120)], return_when=asyncio.FIRST_COMPLETED)
                msg = done.pop().result()
            except asyncio.TimeoutError:
                await player_prompt.edit(content="The game has timed out!")
                await opponent_prompt.edit(content="The game has timed out!")
                await challenge_accepted.edit(content="Challenge accepted! Check your DMs!\nThe game has timed out!")
                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                c = conn.cursor()
                c.execute(""" UPDATE users
                            SET status = array_remove(status, %s)
                            WHERE ID = %s; """, (f'pw{opponent.id}', str(player.id)))
                c.execute(""" UPDATE users
                            SET status = array_remove(status, %s)
                            WHERE ID = %s; """, (f'pw{player.id}', str(opponent.id)))
                conn.commit()
                conn.close()
                return
            else:
                if msg.author == player:
                    if msg.content.lower() == "peace":
                        player_war = False
                        player_answered = True
                    elif msg.content.lower() == "war":
                        player_war = True
                        player_answered = True
                elif msg.author == opponent:
                    if msg.content.lower() == "peace":
                        opponent_war = False
                        opponent_answered = True
                    elif msg.content.lower() == "war":
                        opponent_war = True
                        opponent_answered = True

        both_peace = f"Both players declared **PEACE** and got {bet_amount} Coins!"
        both_war = f"Both players declared **WAR** and lost {bet_amount} Coins!"
        war_peace = f"You declared **WAR** while your opponent declared **PEACE**! You won {3*bet_amount} Coins while your opponent lost {3*bet_amount} Coins!"
        peace_war = f"You declared **PEACE** while your opponent declared **WAR**! You lost {3*bet_amount} Coins while your opponent won {3*bet_amount} Coins!"

        def update_database_coins(player, opponent, player_add, opponent_add):
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute(""" SELECT balance FROM users
                        WHERE ID = %s; """, (str(player.id), ))
            player_balance = int(c.fetchone()[0])
            c.execute(""" SELECT balance FROM users
                        WHERE ID = %s; """, (str(opponent.id), ))
            opponent_balance = int(c.fetchone()[0])
            player_balance += player_add
            opponent_balance += opponent_add
            c.execute(""" UPDATE users
                        SET balance = %s
                        WHERE ID = %s; """, (str(player_balance), str(player.id)))
            c.execute(""" UPDATE users
                        SET balance = %s
                        WHERE ID = %s; """, (str(opponent_balance), str(opponent.id)))
            conn.commit()
            conn.close()

        if player_war is False and opponent_war is False:
            update_database_coins(player, opponent, bet_amount, bet_amount)
            await player.send(both_peace)
            await opponent.send(both_peace)
            await ctx.send(f"{player.mention} and {opponent.mention} both declared **PEACE** and got {bet_amount} Coins!")
        elif player_war is True and opponent_war is False:
            update_database_coins(player, opponent, 3*bet_amount, -3*bet_amount)
            await player.send(war_peace)
            await opponent.send(peace_war)
            await ctx.send(f"{player.mention} declared **WAR** while {opponent.mention} declared **PEACE**. {player.mention} won {3*bet_amount} Coins while {opponent.mention} lost {3*bet_amount} Coins!")
        elif player_war is False and opponent_war is True:
            update_database_coins(player, opponent, -3*bet_amount, 3*bet_amount)
            await player.send(peace_war)
            await opponent.send(war_peace)
            await ctx.send(f"{player.mention} declared **PEACE** while {opponent.mention} declared **WAR**. {player.mention} won {3*bet_amount} Coins while {opponent.mention} lost {3*bet_amount} Coins!")
        else:
            update_database_coins(player, opponent, -bet_amount, -bet_amount)
            await player.send(both_war)
            await opponent.send(both_war)
            await ctx.send(f"{player.mention} and {opponent.mention} both declared **WAR** and lost {bet_amount} Coins!")

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" UPDATE users
                    SET status = array_remove(status, %s)
                    WHERE ID = %s; """, (f'pw{opponent.id}', str(player.id)))
        c.execute(""" UPDATE users
                    SET status = array_remove(status, %s)
                    WHERE ID = %s; """, (f'pw{player.id}', str(opponent.id)))
        conn.commit()
        conn.close()


def setup(bot):
    bot.add_cog(Game(bot))
