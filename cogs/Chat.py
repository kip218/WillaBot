import discord
from discord.ext import commands


class Chat:
    '''
    Chat related commands.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def echo(self, ctx):
        '''
        Repeats [message]
        '''
        if ctx.invoked_subcommand is None:
            content = ctx.message.content
            space_ind = content.find(' ')
            if space_ind > 4:
                content = content[space_ind+1:]
                await ctx.send(content)

    @echo.command(aliases=["erase", "del"])
    async def delete(self, ctx, *, content: str=None):
        '''
        Repeats [message] and deletes the original message
        '''
        if len(ctx.message.mentions) == 0 and content is not None:
            try:
                await ctx.message.delete()
            except EnvironmentError:
                await ctx.send("I don't have permission to delete messages!")
            else:
                await ctx.send(content)
        else:
            if content is None:
                return
            else:
                mentioned_msg = ctx.message.content
                space_ind = mentioned_msg.find(" ", 10)
                mentioned_msg = mentioned_msg[space_ind+1:]
                lst_members_mentions = [member.mention for member in ctx.message.mentions]
                description = ctx.message.author.mention + " pinged " + ', '.join(lst_members_mentions) + " and tried to run away"
                embed = discord.Embed(
                    description=description,
                    color=0xff0000
                    )
                embed.set_thumbnail(
                    url="http://www.pngall.com/wp-content/uploads/2017/05/Alert-Download-PNG.png"
                    )
                embed.add_field(
                    name="Message:",
                    value="*\"" + mentioned_msg + "\"*",
                    inline=True
                    )
                embed.set_author(
                    name=str(ctx.message.author),
                    icon_url=ctx.message.author.avatar_url
                    )
                embed.set_footer(
                    text="*Pinging people and running away is a dick move."
                    )
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Chat(bot))
