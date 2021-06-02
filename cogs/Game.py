from discord.ext import commands
from discord.ext.commands.cog import Cog
import random
import psycopg2
import os
import asyncio
import discord
from random_word import RandomWords
from gibberish import Gibberish

DATABASE_URL = os.environ['DATABASE_URL']


class Game(Cog):
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

        https://en.wikipedia.org/wiki/Monty_Hall_problem
        '''
        # Check that the user isn't already playing the game
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT status FROM users WHERE ID = %s;""", (str(ctx.author.id), ))
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
            return not m.author.bot and m.author == ctx.author and m.content.lower() in ['1', '2', '3', 'y', 'n'] and m.channel == ctx.channel

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
                        xp_increase = random.randint(25, 40)
                        balance_increase = random.randint(100, 160)
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

    @commands.command(usage="<@user> [bet amount]")
    async def pw(self, ctx, user, bet_amount: int=None):
        '''
        The Peace War game.
        w.pw <@user> <bet amount>

        https://en.wikipedia.org/wiki/Peace_war_game
        '''
        if len(ctx.message.mentions) == 0:
            await ctx.send("You must mention a user to play against!")
            return

        player = ctx.author
        opponent = ctx.message.mentions[0]
        if opponent.bot:
            await ctx.send("You can't challenge a bot!")
            return
        elif player == opponent:
            await ctx.send("You can't challenge yourself!")
            return

        if bet_amount is None:
            await ctx.send("You must specify a bet amount!")
            return

        # checking if bet amount is less than limit
        if bet_amount > 5000:
            await ctx.send("Maximum bet amount is 5000 coins!")
            return

        if bet_amount <= 0:
            await ctx.send("Bet amount must be positive!")
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
                await ctx.send("Both players do not have enough Coins to play.\nYou must have more than **triple** the bet amount to play the Peace War game.")
                conn.close()
                return
            elif player_balance < 3*bet_amount:
                await ctx.send(f"{player.name} does not have enough Coins to play.\nYou must have more than **triple** the bet amount to play the Peace War game.")
                conn.close()
                return
            elif opponent_balance < 3*bet_amount:
                await ctx.send(f"{opponent.name} does not have enough Coins to play.\nYou must have more than **triple** the bet amount to play the Peace War game.")
                conn.close()
                return
        conn.close()

        challenge_msg = await ctx.send(f"{opponent.mention}! {player.mention} challenged you to a game of Peace/War!\nType \"w.accept <@user>\" to accept!\n**Bet amount:** {bet_amount}")

        # removing pw from status_lst
        def remove_status(player, opponent):
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

        # checking if opponent accepts challenge
        def check_accept(m):
            return m.author == opponent and m.content.startswith('w.accept') and m.channel == ctx.channel

        accepted = False
        while accepted is False:
            try:
                accept = await self.bot.wait_for('message', check=check_accept, timeout=60)
            except asyncio.TimeoutError:
                await challenge_msg.edit(content=challenge_msg.content + "\n*The challenge has timed out!*")
                return
            else:
                if accept.content == 'w.accept':
                    await ctx.send("You must specify the @user that challenged you!")
                elif accept.content == f'w.accept {player.mention}':
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

        title = "The rules of the Peace War game are as follows:"
        prompt = f"- If both players declare peace, both get <bet amount> of Coins.\n- If you declare war while your opponent declares peace, you get triple the <bet amount> while your opponent loses triple the <bet amount>, and vice versa.\n- If both players declare war, both lose <bet amount> of Coins.\n\nType \"peace\" to declare peace and \"war\" to declare war.\n\n**Bet amount:** {bet_amount}"
        player_embed = discord.Embed(title=title, description=f"{prompt}\n**Opponent:** {opponent.name}", color=0x48d1cc)
        opponent_embed = discord.Embed(title=title, description=f"{prompt}\n**Opponent:** {player.name}", color=0x48d1cc)
        player_prompt = await player.send(embed=player_embed)
        opponent_prompt = await opponent.send(embed=opponent_embed)

        # checking player's response
        def check_player(m):
            return m.channel == player.dm_channel and m.content.lower() in ['peace', 'war']

        def check_opponent(m):
            return m.channel == opponent.dm_channel and m.content.lower() in ['peace', 'war']

        # checking opponent's response
        player_answered = False
        opponent_answered = False
        while player_answered is False or opponent_answered is False:
            try:
                done, pending = await asyncio.wait([self.bot.wait_for('message', check=check_player, timeout=60), self.bot.wait_for('message', check=check_opponent, timeout=60)], return_when=asyncio.FIRST_COMPLETED)
                msg = done.pop().result()
            except asyncio.TimeoutError:
                player_prompt.embeds[0].set_footer(text="The game has timed out!")
                opponent_prompt.embeds[0].set_footer(text="The game has timed out!")
                await player_prompt.edit(embed=player_prompt.embeds[0])
                await opponent_prompt.edit(embed=opponent_prompt.embeds[0])
                await challenge_accepted.edit(content=f"{challenge_accepted.content}\n*The game has timed out!*")
                remove_status(player, opponent)
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
            await ctx.send(f"{player.mention} declared **PEACE** while {opponent.mention} declared **WAR**. {player.mention} lost {3*bet_amount} Coins while {opponent.mention} won {3*bet_amount} Coins!")
        else:
            update_database_coins(player, opponent, -bet_amount, -bet_amount)
            await player.send(both_war)
            await opponent.send(both_war)
            await ctx.send(f"{player.mention} and {opponent.mention} both declared **WAR** and lost {bet_amount} Coins!")

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT xp FROM users
                    WHERE ID = %s OR ID = %s; """, (str(player.id), str(opponent.id)))
        fetch = c.fetchall()
        player_xp = int(fetch[0][0])
        player_xp += random.randint(10, 20)
        opponent_xp = int(fetch[1][0])
        opponent_xp += random.randint(10, 20)
        c.execute(""" UPDATE users SET xp = %s WHERE ID = %s; """, (str(player_xp), str(player.id)))
        c.execute(""" UPDATE users SET xp = %s WHERE ID = %s; """, (str(opponent_xp), str(opponent.id)))
        conn.commit()
        conn.close()
        remove_status(player, opponent)

    # @commands.command()
    # async def speed(self):
    #     '''
    #     A game to test your reaction time
    #     w.speed
    #     '''

    @commands.command(usage="[number of words]")
    async def typeracer(self, ctx, num_words: int=5):
        '''
        A game to test your typing speed.
        w.typeracer [number of words]

        Number of words defaults to 5 if not specified.
        Type "w.stop" to stop the game. Only the game starter and server admins can stop the game.
        '''
        def get_scoreboard_embed(sorted_lst):
            embed = discord.Embed(color=0x48d1cc)
            temp = None
            offset = 0
            for i in range(len(sorted_lst)):
                player_score = sorted_lst[i]
                player = player_score[0]
                score = player_score[1]
                # checking to make sure people don't have same scores
                if score == temp:
                    offset += 1
                else:
                    offset = 0
                temp = score
                xp_increase, balance_increase = update_db_and_return_increase(player, score)
                embed.add_field(name=f"{i+1-offset}. {player.name}", value=f"**{score} words** *(+{xp_increase} XP, +{balance_increase} Coins)*", inline=False)
                embed.set_author(name="Final Scoreboard", icon_url=self.bot.user.avatar_url)
            return embed

        def update_db_and_return_increase(player, score):
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute(""" SELECT xp, balance FROM users
                        WHERE ID = %s; """, (str(player.id), ))
            fetch = c.fetchone()
            xp = int(fetch[0])
            balance = int(fetch[1])
            xp_increase = 0
            balance_increase = 0
            for i in range(score):
                xp_increase += random.randint(12, 20)
                balance_increase += random.randint(50, 80)
            xp += xp_increase
            balance += balance_increase
            c.execute(""" UPDATE users SET xp = %s, balance = %s WHERE ID = %s; """, (xp, balance, str(player.id)))
            conn.commit()
            conn.close()
            return xp_increase, balance_increase

        # remove 'typeracer' status from channel
        def remove_status():
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute(""" UPDATE channels
                        SET status = array_remove(status, %s)
                        WHERE channel_id = %s; """, ('typeracer', str(ctx.channel.id)))
            conn.commit()
            conn.close()

        # Check that the game isn't already running in the channel
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT status FROM channels WHERE channel_id = %s;""", (str(ctx.channel.id), ))
        status_lst = c.fetchone()[0]
        if status_lst is not None:
            if "typeracer" in status_lst:
                await ctx.send("This channel is already in a game of typeracer!")
                conn.commit()
                conn.close()
                return
        c.execute(""" UPDATE channels
                    SET status = array_append(status, %s)
                    WHERE channel_id = %s; """, ('typeracer', str(ctx.channel.id)))
        conn.commit()
        conn.close()

        if num_words > 25 or num_words < 1:
            await ctx.send("Number of words must be between 1 and 25!")
            remove_status()
            return

        def get_new_word():
            new_word_found = False
            while new_word_found is False:
                new_word = r.get_random_word(limit=num_words, hasDictionaryDef="true")
                for char in new_word:
                    if not 32 <= ord(char) <= 122:
                        pass
                    else:
                        new_word_found = True
            return new_word.lower()

        await ctx.send("*The race has started!\nThe word to type is...*")
        # getting list of words
        r = RandomWords()
        words_lst = r.get_random_words(limit=num_words, hasDictionaryDef="true")

        # removing strange characters
        for i in range(len(words_lst)):
            for char in words_lst[i]:
                if not 32 <= ord(char) <= 122:
                    new_word = get_new_word()
                    words_lst[i] = new_word
            words_lst[i] = words_lst[i].lower()

        # shuffling words_lst
        random.shuffle(words_lst)

        scoreboard_dict = {}
        i = 0
        word_sent = False
        while i < len(words_lst):
            if not word_sent:
                word_sent = True
                word = words_lst[i]
                word_display = word[0] + "\u200b" + word[1:]
                embed = discord.Embed(title="The word is:", description="`" + word_display + "`", color=0xF5DE50)
                embed.set_author(
                            name="Type the word!",
                            icon_url="http://www.law.uj.edu.pl/kpk/strona/wp-content/uploads/2016/03/52646-200.png")
                embed.set_footer(text=f"{i+1}/{len(words_lst)}")
                msg = await ctx.send(embed=embed)

            def check(m):
                return not m.author.bot and (m.content == word or m.content == word_display or (m.content == 'w.stop' and (m.author == ctx.author or m.author.permissions_in(ctx.channel).administrator))) and m.channel == ctx.channel

            try:
                answer = await self.bot.wait_for('message', check=check, timeout=25)
            except asyncio.TimeoutError:
                embed = discord.Embed(
                                    title="The word was:",
                                    description=word_display,
                                    color=0xED1C24
                                    )
                embed.set_author(
                        name="The type race has timed out!",
                        icon_url="http://cdn.onlinewebfonts.com/svg/img_96745.png")
                embed.set_footer(text=f"{i+1}/{len(words_lst)}")
                await msg.edit(embed=embed)
                break
            else:
                if answer.content == word:
                    embed = discord.Embed(
                                    title="The word was:",
                                    description=word_display,
                                    color=0x4CC417
                                    )
                    embed.set_author(
                                name=f"{answer.author.name} got it right!",
                                icon_url=answer.author.avatar_url)
                    embed.set_footer(text=f"{i+1}/{len(words_lst)}")
                    await msg.edit(embed=embed)
                    # update scoreboard
                    if answer.author in scoreboard_dict:
                        scoreboard_dict[answer.author] += 1
                    else:
                        scoreboard_dict[answer.author] = 1
                    i += 1
                    word_sent = False
                elif answer.content == word_display:
                    await ctx.send(answer.author.mention + " Don't even try to ctrl+C ctrl+V!")
                elif answer.content == 'w.stop':
                    embed = discord.Embed(
                                    title="The word was:",
                                    description=word_display,
                                    color=0xED1C24
                                    )
                    embed.set_author(
                        name="The type race has been stopped",
                        icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Black_close_x.svg/2000px-Black_close_x.svg.png")
                    embed.set_footer(text=f"{i+1}/{len(words_lst)}")
                    await msg.edit(embed=embed)
                    break

        if len(scoreboard_dict) > 0:
            # gives sorted list in order of decreasing score
            sorted_lst = sorted(scoreboard_dict.items(), key=lambda x: x[1])
            sorted_lst.reverse()
            await ctx.send(embed=get_scoreboard_embed(sorted_lst))

        remove_status()

    @commands.command(usage="[number of words]")
    async def shittytyperacer(self, ctx, num_words: int=5):
        '''
        A game to test your typing speed?
        w.typeracer [number of words]

        Number of words defaults to 5 if not specified.
        Type "w.stop" to stop the game. Only the game starter and server admins can stop the game.
        '''
        def get_scoreboard_embed(sorted_lst):
            embed = discord.Embed(color=0x48d1cc)
            temp = None
            offset = 0
            for i in range(len(sorted_lst)):
                player_score = sorted_lst[i]
                player = player_score[0]
                score = player_score[1]
                # checking to make sure people don't have same scores
                if score == temp:
                    offset += 1
                else:
                    offset = 0
                temp = score
                xp_increase, balance_increase = update_db_and_return_increase(player, score)
                embed.add_field(name=f"{i+1-offset}. {player.name}", value=f"**{score} words** *(+{xp_increase} XP, +{balance_increase} Coins)*", inline=False)
                embed.set_author(name="Final Scoreboard", icon_url=self.bot.user.avatar_url)
            return embed

        def update_db_and_return_increase(player, score):
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute(""" SELECT xp, balance FROM users
                        WHERE ID = %s; """, (str(player.id), ))
            fetch = c.fetchone()
            xp = int(fetch[0])
            balance = int(fetch[1])
            xp_increase = 0
            balance_increase = 0
            for i in range(score):
                xp_increase += random.randint(12, 20)
                balance_increase += random.randint(50, 80)
            xp += xp_increase
            balance += balance_increase
            c.execute(""" UPDATE users SET xp = %s, balance = %s WHERE ID = %s; """, (xp, balance, str(player.id)))
            conn.commit()
            conn.close()
            return xp_increase, balance_increase

        # remove 'typeracer' status from channel
        def remove_status():
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute(""" UPDATE channels
                        SET status = array_remove(status, %s)
                        WHERE channel_id = %s; """, ('typeracer', str(ctx.channel.id)))
            conn.commit()
            conn.close()

        # Check that the game isn't already running in the channel
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT status FROM channels WHERE channel_id = %s;""", (str(ctx.channel.id), ))
        status_lst = c.fetchone()[0]
        if status_lst is not None:
            if "typeracer" in status_lst:
                await ctx.send("This channel is already in a game of typeracer!")
                conn.commit()
                conn.close()
                return
        c.execute(""" UPDATE channels
                    SET status = array_append(status, %s)
                    WHERE channel_id = %s; """, ('typeracer', str(ctx.channel.id)))
        conn.commit()
        conn.close()

        if num_words > 25 or num_words < 1:
            await ctx.send("Number of words must be between 1 and 25!")
            remove_status()
            return

        await ctx.send("*The race has started!\nThe word to type is...*")
        # getting list of words
        gib = Gibberish()
        words_lst = gib.generate_words(num_words)

        scoreboard_dict = {}
        i = 0
        word_sent = False
        while i < len(words_lst):
            if not word_sent:
                word_sent = True
                word = words_lst[i]
                word_display = word[0] + "\u200B" + word[1:]
                embed = discord.Embed(title="The word is:", description="`" + word_display + "`", color=0xF5DE50)
                embed.set_author(
                            name="Type the word!",
                            icon_url="http://www.law.uj.edu.pl/kpk/strona/wp-content/uploads/2016/03/52646-200.png")
                embed.set_footer(text=f"{i+1}/{len(words_lst)}")
                msg = await ctx.send(embed=embed)

            def check(m):
                return not m.author.bot and (m.content == word or m.content == word_display or (m.content == 'w.stop' and (m.author == ctx.author or m.author.permissions_in(ctx.channel).administrator))) and m.channel == ctx.channel

            try:
                answer = await self.bot.wait_for('message', check=check, timeout=25)
            except asyncio.TimeoutError:
                embed = discord.Embed(
                                    title="The word was:",
                                    description=word_display,
                                    color=0xED1C24
                                    )
                embed.set_author(
                        name="The type race has timed out!",
                        icon_url="http://cdn.onlinewebfonts.com/svg/img_96745.png")
                embed.set_footer(text=f"{i+1}/{len(words_lst)}")
                await msg.edit(embed=embed)
                break
            else:
                if answer.content == word:
                    embed = discord.Embed(
                                    title="The word was:",
                                    description=word_display,
                                    color=0x4CC417
                                    )
                    embed.set_author(
                                name=f"{answer.author.name} got it right!",
                                icon_url=answer.author.avatar_url)
                    embed.set_footer(text=f"{i+1}/{len(words_lst)}")
                    await msg.edit(embed=embed)
                    # update scoreboard
                    if answer.author in scoreboard_dict:
                        scoreboard_dict[answer.author] += 1
                    else:
                        scoreboard_dict[answer.author] = 1
                    i += 1
                    word_sent = False
                elif answer.content == word_display:
                    await ctx.send(answer.author.mention + " Don't even try to ctrl+C ctrl+V!")
                elif answer.content == 'w.stop':
                    embed = discord.Embed(
                                    title="The word was:",
                                    description=word_display,
                                    color=0xED1C24
                                    )
                    embed.set_author(
                        name="The type race has been stopped",
                        icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Black_close_x.svg/2000px-Black_close_x.svg.png")
                    embed.set_footer(text=f"{i+1}/{len(words_lst)}")
                    await msg.edit(embed=embed)
                    break

        if len(scoreboard_dict) > 0:
            # gives sorted list in order of decreasing score
            sorted_lst = sorted(scoreboard_dict.items(), key=lambda x: x[1])
            sorted_lst.reverse()
            await ctx.send(embed=get_scoreboard_embed(sorted_lst))

        remove_status()

    @shittytyperacer.error
    @montyhall.error
    # @typeracer.error
    async def game_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            if ctx.command.name == 'montyhall':
                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                c = conn.cursor()
                c.execute(""" UPDATE users
                            SET status = array_remove(status, %s)
                            WHERE ID = %s; """, ('montyhall', str(ctx.author.id)))
                conn.commit()
                conn.close()
            elif ctx.command.name == 'typeracer' or ctx.command.name == 'shittytyperacer':
                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                c = conn.cursor()
                c.execute(""" UPDATE channels
                            SET status = array_remove(status, %s)
                            WHERE channel_id = %s; """, ('typeracer', str(ctx.channel.id)))
                conn.commit()
                conn.close()
        else:
            await ctx.send("Unknown error. Please tell Willa.")
            print(error)


def setup(bot):
    bot.add_cog(Game(bot))
