import discord
from discord.ext import commands


class Chat:
    '''
    Chat related commands.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @commands.group(invoke_without_command=True)
    async def echo(self, ctx, *, message: str=None):
        '''
        Repeats message.
        w.echo <message>
        '''
        if message is None:
            ctx.command.reset_cooldown(ctx)
            return
        if ctx.invoked_subcommand is None:
            content = ctx.message.content
            space_ind = content.find(' ')
            if space_ind > 4:
                content = content[space_ind+1:]
                await ctx.send(content)

    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @echo.command(aliases=["del"], usage="/ del [message]")
    async def delete(self, ctx, *, message: str=None):
        '''
        Repeats message and deletes original message.
        w.echo delete <message>
        '''
        if message is None:
            ctx.command.reset_cooldown(ctx)
            return
        if len(ctx.message.mentions) == 0:
            try:
                await ctx.message.delete()
            except EnvironmentError:
                await ctx.send("I don't have permission to delete messages!")
            else:
                await ctx.send(message)
        else:
            if message is None:
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

    @commands.command()
    async def purge(self, ctx, number: int=1):
        '''
        Purges <number> of messages. Only members with admin perms can use this command.
        w.purge <number>

        <number> defaults to 1 and has to be between 1 and 100.
        '''
        permissions = ctx.author.permissions_in(ctx.channel)
        if permissions.administrator:
            if not 1 <= number <= 100:
                await ctx.send("<number> must be between 1 and 100!")
            else:
                messages = await ctx.channel.history(limit=number+1).flatten()
                for message in messages:
                    await message.delete()
        else:
            await ctx.send("You don't have admin permissions in this channel!")

    @echo.error
    @delete.error
    async def echo_on_cooldown(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            error_msg = str(error)
            T_ind = error_msg.find("T")
            error_msg = error_msg[T_ind:]
            user = ctx.message.author
            await ctx.send("Slow down " + user.mention + "! The command is on cooldown! " + error_msg + ".")
        else:
            await ctx.send("Unknown error. Please tell Willa.")


def setup(bot):
    bot.add_cog(Chat(bot))
