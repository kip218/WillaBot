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

        def check(m):
            return not m.author.bot and m.author == ctx.message.author

        options = [1, 2, 3]
        car = random.randint(1, 3)
        msg = await ctx.send("Choose a door to open (1, 2, 3)\n\n:one: :two: :three:\n:door: :door: :door:")
        answered = False
        while answered is False:
            answer = await self.bot.wait_for('message', check=check, timeout=180)
            try:
                answer = int(answer.content)
                options.remove(answer)
                options.append(answer)
            except:
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
                    switch = await self.bot.wait_for('message', check=check, timeout=180)
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
                                        WHERE ID = %s; """, (str(ctx.message.author.id), ))
                            fetch = c.fetchone()
                            xp = int(fetch[0])
                            balance = int(fetch[1])
                            xp_increase = random.randint(10, 20)
                            balance_increase = random.randint(20, 40)
                            xp += xp_increase
                            balance += balance_increase
                            c.execute(""" UPDATE users SET xp = %s, balance = %s WHERE ID = %s; """, (xp, balance, str(ctx.message.author.id)))
                            conn.commit()
                            conn.close()
                            await msg.edit(content="You found the car!\n\nYou got " + str(xp_increase) + " XP and " + str(balance_increase) + " WillaCoins.\n\n" + emotes)
                        else:
                            await msg.edit(content="You did not find the car. Try again!\n\n" + emotes)

    @commands.command()
    async def pw(self, ctx, user):
        '''
        The Peace War game.
        w.pw <user>
        '''
        if len(ctx.message.mentions) == 0:
            await ctx.send("You must mention a user to play against!")
            return

        player = ctx.message.author
        opponent = ctx.message.mentions[0]
        if opponent.bot:
            await ctx.send("You can't challenge a bot!")
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
            if player_balance < 300 or opponent_balance < 300:
                await ctx.send("One player does not have enough WillaCoins to play. You must have more than 300 WillaCoins to play the Peace War game.")
                conn.close()
                return

        challenge_msg = await ctx.send(opponent.mention + "! " + player.mention + " challenged you to a game of Peace/War! Type \"w.accept\" to accept!")

        # checking if opponent accepts challenge
        def check_accept(m):
            return m.author == opponent
        accepted = False
        while accepted is False:
            try:
                accept = await self.bot.wait_for('message', check=check_accept, timeout=120)
            except:
                await challenge_msg.edit(content=opponent.mention + "! " + player.mention + " challenged you to a game of Peace/War! Type \"w.accept\" to accept!\n\nThe challenge has timed out!")
                return
            else:
                if accept.content == "w.accept":
                    accepted = True
                    challenge_accepted = await ctx.send("Challenge accepted! Check your DMs!")

        prompt = "The rules of the Peace War game are as follows:\n\n- If both players declare peace, they both get 100 WillaCoins.\n- If one player declares war while the other declares peace, the player declaring war gets 300 WillaCoins, while the player declaring peace loses 300 WillaCoins\n- If both players declare war, they both lose 100 WillaCoins.\n\nType \"peace\" to declare peace and \"war\" to declare war."
        player_prompt = await player.send(prompt)
        opponent_prompt = await opponent.send(prompt)
        start_time = datetime.utcnow()

        # checking player's response
        def check_player(m):
            return m.channel == player.dm_channel

        def check_opponent(m):
            return m.channel == opponent.dm_channel

        # checking opponent's response
        timeout = False
        player_answered = False
        opponent_answered = False
        while timeout is False and (player_answered is False or opponent_answered is False):
            try:
                done, pending = await asyncio.wait([self.bot.wait_for('message', check=check_player), self.bot.wait_for('message', check=check_opponent)], return_when=asyncio.FIRST_COMPLETED)
                msg = done.pop().result()
                delta = datetime.utcnow() - start_time
                if delta.total_seconds() > 120:
                    await player_prompt.edit(content="The game has timed out!")
                    await opponent_prompt.edit(content="The game has timed out!")
                    await challenge_accepted.edit(content="Challenge accepted! Check your DMs!\nThe game has timed out!")
                    timeout = True
                    return
            except:
                await ctx.send("Sorry, something went wrong. Please tell Willa.")
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

        both_peace = "Both players declared **PEACE** and got 100 WillaCoins!"
        both_war = "Both players declared **WAR** and lost 100 WillaCoins!"
        war_peace = "You declared **WAR** while your opponent declared **PEACE**! You won 300 WillaCoins while your opponent lost 300 WillaCoins!"
        peace_war = "You declared **PEACE** while your opponent declared **WAR**! You lost 300 WillaCoins while your opponent won 300 WillaCoins!"

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT balance FROM users
                    WHERE ID = %s; """, (str(player.id), ))
        player_balance = int(c.fetchone()[0])
        c.execute(""" SELECT balance FROM users
                    WHERE ID = %s; """, (str(opponent.id), ))
        opponent_balance = int(c.fetchone()[0])

        if player_war is False and opponent_war is False:
            player_balance += 100
            opponent_balance += 100
            c.execute(""" UPDATE users
                        SET balance = %s
                        WHERE ID = %s; """, (str(player_balance), str(player.id)))
            c.execute(""" UPDATE users
                        SET balance = %s
                        WHERE ID = %s; """, (str(opponent_balance), str(opponent.id)))
            await player.send(both_peace)
            await opponent.send(both_peace)
            await ctx.send(player.mention + " and " + opponent.mention + " both declared **PEACE** and got 100 Willacoins!")
        elif player_war is True and opponent_war is False:
            player_balance += 300
            opponent_balance -= 300
            c.execute(""" UPDATE users
                        SET balance = %s
                        WHERE ID = %s; """, (str(player_balance), str(player.id)))
            c.execute(""" UPDATE users
                        SET balance = %s
                        WHERE ID = %s; """, (str(opponent_balance), str(opponent.id)))
            await player.send(war_peace)
            await opponent.send(peace_war)
            await ctx.send(player.mention + " declared **WAR** while " + opponent.mention + " declared **PEACE**. " + player.mention + " won 300 WillaCoins while " + opponent.mention + " lost 300 WillaCoins!")
        elif player_war is False and opponent_war is True:
            player_balance -= 300
            opponent_balance += 300
            c.execute(""" UPDATE users
                        SET balance = %s
                        WHERE ID = %s; """, (str(player_balance), str(player.id)))
            c.execute(""" UPDATE users
                        SET balance = %s
                        WHERE ID = %s; """, (str(opponent_balance), str(opponent.id)))
            await player.send(peace_war)
            await opponent.send(war_peace)
            await ctx.send(player.mention + " declared **WAR** while " + opponent.mention + " declared **PEACE**. " + player.mention + " won 300 WillaCoins while " + opponent.mention + " lost 300 WillaCoins!")
        else:
            player_balance -= 100
            opponent_balance -= 100
            c.execute(""" UPDATE users
                        SET balance = %s
                        WHERE ID = %s; """, (str(player_balance), str(player.id)))
            c.execute(""" UPDATE users
                        SET balance = %s
                        WHERE ID = %s; """, (str(opponent_balance), str(opponent.id)))
            await player.send(both_war)
            await opponent.send(both_war)
            await ctx.send(player.mention + " and " + opponent.mention + " both declared **WAR** and lost 100 WillaCoins!")

        conn.commit()
        conn.close()


def setup(bot):
    bot.add_cog(Game(bot))
