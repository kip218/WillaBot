import discord
from discord.ext import commands
from datetime import datetime
import asyncio


def format_help_page(bot, cog_name, curr_page, max_page):
    lst_commands = bot.get_cog_commands(cog_name)
    embed = discord.Embed(
        title=cog_name + " commands",
        description="Page " + str(curr_page) + " of " + str(max_page) + ". React with :point_left: or :point_right: below to view other pages.\n\"w.help [command]\" for info on a specific command.",
        color=0x48d1cc
        )
    embed.set_author(name="WillaBot", icon_url="https://cdn.discordapp.com/avatars/463398601553346581/16918503e6313c71fc023ac37233d992.webp?size=1024")
    embed.set_footer(text="Prefix is \"w.\"")
    for command in lst_commands:
        embed.add_field(name=command.signature, value=command.short_doc, inline=False)
        if isinstance(command, commands.core.Group):
            for subcommand in command.commands:
                embed.add_field(name=subcommand.signature, value=subcommand.short_doc, inline=False)
    return embed


class Help:
    '''
    Help commands.
    '''
    def __init__(self, bot):
        self.bot = bot
        self.lst_cogs = ['General', 'Game', 'Todo', 'Chat', 'Brawlhalla', 'Challonge', 'Bot']
        self.lst_cogs_embed = []
        for i in range(len(self.lst_cogs)):
            embed = format_help_page(bot, self.lst_cogs[i], i+1, len(self.lst_cogs))
            self.lst_cogs_embed.append(embed)

    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @commands.group(invoke_without_command=True)
    async def help(self, ctx, *, command: str=None):
        '''
        Sends the help menu.
        w.help [command]
        Command can be specified to get more information about the command.
        '''
        if command is None:
            curr_page = 1
            curr_ind = curr_page - 1
            embed = self.lst_cogs_embed[curr_ind]
            help_page = await ctx.send(embed=embed)
            await help_page.add_reaction(emoji='\U0001F448')
            await help_page.add_reaction(emoji='\U0001F449')

            def check(reaction, user):
                return ctx.message.author == user and user.bot is False and (reaction.emoji == '\U0001F448' or reaction.emoji == '\U0001F449') and help_page.id == reaction.message.id

            timeout = False
            while timeout is False:
                try:
                    done, pending = await asyncio.wait([self.bot.wait_for('reaction_add', check=check, timeout=180), self.bot.wait_for('reaction_remove', check=check, timeout=180)], return_when=asyncio.FIRST_COMPLETED)
                    reaction = done.pop().result()[0]
                except asyncio.TimeoutError:
                    timeout = True
                    help_page_embed = help_page.embeds[0]
                    help_page_embed.set_footer(text="The help page has timed out!")
                    await help_page.edit(embed=help_page_embed)
                    return
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
        else:
            cmd = self.bot.get_command(command)
            if cmd is None:
                await ctx.send(f"Command \"{command}\" not found.")
            else:
                await ctx.send(cmd.help)

    @help.error
    async def help_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            error_msg = str(error)
            T_ind = error_msg.find("T")
            error_msg = error_msg[T_ind:]
            user = ctx.message.author
            await ctx.send("Slow down " + user.mention + "! The command is on cooldown! " + error_msg + ".")
        else:
            await ctx.send("Unknown error. Please tell Willa.")
            print(error)

    @help.command()
    async def owner(self, ctx):
        if await self.bot.is_owner(ctx.message.author):
            embed = format_help_page(self.bot, 'Owner', 1, 1)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Something tells me you're not Willa :thinking:")


def setup(bot):
    bot.add_cog(Help(bot))