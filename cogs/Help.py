import discord
from discord.ext import commands
from datetime import datetime


def format_help_page(bot, cog_name, curr_page, max_page):
    lst_commands = bot.get_cog_commands(cog_name)
    embed = discord.Embed(
        title=cog_name + " commands",
        description="Page " + str(curr_page) + " of " + str(max_page) + ". React with :point_left: or :point_right: below to view other pages.",
        color=0x48d1cc
        )
    embed.set_author(name="WillaBot", icon_url="https://cdn.discordapp.com/avatars/463398601553346581/16918503e6313c71fc023ac37233d992.webp?size=1024")
    embed.set_footer(text="Prefix is 'w.'")
    for command in lst_commands:
        embed.add_field(name=command.name, value=command.short_doc)
    return embed


class Help:
    '''
    Help commands.
    '''

    def __init__(self, bot):
        self.bot = bot
        self.lst_cogs = ['General', 'Chat', 'Bot', 'Owner']
        self.lst_cogs_embed = []
        for i in range(len(self.lst_cogs)):
            embed = format_help_page(bot, self.lst_cogs[i], i+1, len(self.lst_cogs))
            self.lst_cogs_embed.append(embed)

    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.command()
    async def help(self, ctx):
        '''
        Sends the help menu.
        w.help [command]
        Command can be specified to get more information about the command.
        '''
        curr_page = 1
        curr_ind = curr_page - 1
        embed = self.lst_cogs_embed[curr_ind]
        help_page = await ctx.send(embed=embed)
        await help_page.add_reaction(emoji='\U0001F448')
        await help_page.add_reaction(emoji='\U0001F449')
        start_time = datetime.utcnow()

        def check(reaction, user):
            return ctx.message.author == user and user.bot is False and (reaction.emoji == '\U0001F448' or reaction.emoji == '\U0001F449') and help_page.id == reaction.message.id

        timeout = False
        while timeout is False:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check)
                time_now = datetime.utcnow()
                delta = datetime.utcnow() - start_time
                if delta.total_seconds() > 120:
                    timeout = True
                    return
            except SyntaxError:
                await ctx.send("Sorry, something went wrong. Please tell Willa.")
            else:
                if reaction.emoji == '\U0001F448':
                    if curr_page == 1:
                        curr_page = len(self.lst_cogs_embed)
                    else:
                        curr_page -= 1
                elif reaction.emoji == '\U0001F449':
                    if curr_page == len(self.lst_cogs_embed):
                        curr_page = 1
                    else:
                        curr_page += 1
                new_page_num = curr_page
                new_ind = new_page_num - 1
                new_embed = self.lst_cogs_embed[new_ind]
                await help_page.edit(embed=new_embed)
                await help_page.remove_reaction(emoji='\U0001F448', member=user)
                await help_page.remove_reaction(emoji='\U0001F449', member=user)

    @help.error
    async def help_on_cooldown(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            error_msg = str(error)
            T_ind = error_msg.find("T")
            error_msg = error_msg[T_ind:]
            user = ctx.message.author
            await ctx.send("Slow down " + user.mention + "! The command is on cooldown! " + error_msg + ".")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("I don't have permission to edit messages!")
        else:
            await ctx.send("Unknown error. Please tell Willa.")


def setup(bot):
    bot.add_cog(Help(bot))