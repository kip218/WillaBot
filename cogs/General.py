import discord
from discord.ext import commands
import random


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
                if user.lower() in curr_member.display_name.lower():
                    embed = get_pfp(curr_member)
                    await ctx.send(embed=embed)
                    found = True
                elif user.lower() in curr_member.name.lower():
                    embed = get_pfp(curr_member)
                    await ctx.send(embed=embed)
                    found = True
                else:
                    ind += 1
            if found is False:
                await ctx.send("Could not find user named \"" + user + "\"")

    @commands.command()
    async def daily(self, ctx):
        '''
        Get your daily Willacoins!
        w.daily
        '''
        if await self.bot.is_owner(ctx.message.author):
            await ctx.send("You got 200 Willacoins!")
        else:
            await ctx.send("SIKE this is still work in progress you didn't get any Willacoins :joy:")

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
            answer = await self.bot.wait_for('message', check=check, timeout=600)
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
                    switch = await self.bot.wait_for('message', check=check, timeout=600)
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
                            await msg.edit(content="You found the car!\n\n" + emotes)
                        else:
                            await msg.edit(content="You did not find the car. Try again!\n\n" + emotes)


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