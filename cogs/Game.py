from discord.ext import commands
import random
import psycopg2
import os

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
        The famous Monty Hall problem
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
    async def pd(self, ctx, user):
        '''
        Prisoner's Dilemma
        w.pd <user>
        '''
        

def setup(bot):
    bot.add_cog(Game(bot))
