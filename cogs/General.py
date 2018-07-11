import discord
from discord.ext import commands


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


    @commands.command(aliases=["math"])
    async def calc(self, ctx, *, equation: str=None):
        '''
        Calculator for simple arithmetic operations (+, -, x, /, ^)
        w.calc <algebraic expression>
        A quick simple calculator for when you're feeling lazy.
        '''
        equation = equation.replace("^", "**")
        equation = equation.replace("x", "*")
        try:
            res = eval(equation)
        except SyntaxError:
            await ctx.send("Invalid input.")
        else:
            await ctx.send(res)


def setup(bot):
    bot.add_cog(General(bot))