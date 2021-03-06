import discord
from discord.ext import commands
from discord.ext.commands.cog import Cog
from datetime import datetime
import random

launch_time = datetime.utcnow()


class Bot(Cog):
    '''
    Bot related commands.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def servers(self, ctx):
        '''
        Shows the number of servers and users using WillaBot.
        w.servers
        '''
        num = len(self.bot.guilds)
        id_name_dict = {}
        total_users = 0
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.id not in id_name_dict:
                    id_name_dict[member.id] = member.name
        total_users = len(id_name_dict)
        await ctx.send(f"WillaBot is currently exploring {num} different servers with {total_users} unique users!")

    @commands.command(usage="[server name]")
    async def server(self, ctx, *, server_name: str=None):
        '''
        Gives current server info if [server name] not specified. Name of the server can be specified to show info of that server. WillaBot needs to be a member of the server.
        w.serverinfo [server name]
        '''
        if server_name is None:
            title = ctx.guild.name
            member_count = str(ctx.guild.member_count)
            icon_url = ctx.guild.icon_url
        else:
            try:
                server_num = int(server_name)
            except ValueError:
                server_lst = self.bot.guilds
                ind = 0
                found = False
                while found is False and ind < len(server_lst):
                    curr_server = server_lst[ind]
                    if server_name.lower().replace(" ", "") in curr_server.name.lower().replace(" ", ""):
                        title = curr_server.name
                        member_count = str(curr_server.member_count)
                        icon_url = curr_server.icon_url
                        found = True
                    else:
                        ind += 1
                if found is False:
                    await ctx.send("Could not find server named \"" + server_name + "\"")
                    return
            else:
                if 1 <= server_num <= len(self.bot.guilds):
                    server = self.bot.guilds[server_num-1]
                    title = server.name
                    member_count = str(server.member_count)
                    icon_url = server.icon_url
                else:
                    await ctx.send("Not a valid number. Please use an integer between 0 and " + str(len(self.bot.guilds)))
        embed = discord.Embed(
            title=title,
            description="Member count: " + member_count,
            color=0x48d1cc
            )
        embed.set_thumbnail(
            url=icon_url
            )
        await ctx.send(embed=embed)

    @commands.command()
    async def hello(self, ctx):
        '''
        Greet WillaBot!
        w.hello
        '''
        await ctx.send('Hello ' + ctx.message.author.mention + '!')

    @commands.command()
    async def ping(self, ctx):
        '''
        Checks WillaBot latency from host server.
        w.ping
        '''
        latency = int(self.bot.latency*1000)
        msg_lst = ['Pong! ', str(latency), 'ms']
        msg = ''.join(msg_lst)
        await ctx.send(msg)

    @commands.command()
    async def uptime(self, ctx):
        '''
        Shows how long WillaBot has been online for.
        w.uptime
        '''
        delta_uptime = datetime.utcnow() - launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"{days}d {hours}h {minutes}m {seconds}s")

    @commands.command()
    async def invite(self, ctx):
        '''
        Invite Willabot to your server! Or get an invite to Willa's Server!
        w.invite
        '''
        title_lst = ("Invite WillaBot to your server!", "Help WillaBot explore a new server!")
        desc_lst = ("Please let me join your server :)", "*Nothing is pleasanter to me than exploring different discord servers.\n- WillaBot*")
        randind = random.randint(0, 1)
        embed = discord.Embed(
            title=title_lst[randind],
            url="https://discordapp.com/oauth2/authorize?client_id=463398601553346581&scope=bot&permissions=1077275729",
            description=desc_lst[randind],
            color=0x48d1cc
            )
        embed.set_thumbnail(
            url=self.bot.user.avatar_url
            )
        embed.set_footer(
            text="Click the link to invite WillaBot to your server!")
        await ctx.send(content="https://discord.gg/UAp5ZTZ", embed=embed)

    @commands.cooldown(rate=1, per=180, type=commands.BucketType.user)
    @commands.command()
    async def report(self, ctx, *, message):
        '''
        Report bugs or send suggestions to Willa!
        w.report <message>
        '''
        embed = discord.Embed(
            description=f"***{message}***",
            color=0xF5DE50
                )
        embed.set_author(
            name=f"{ctx.author}",
            icon_url=ctx.author.avatar_url
                )
        embed.set_footer(
            text=f"{ctx.guild} | {ctx.channel}"
                )
        owner = self.bot.get_user(161774631303249921)
        await owner.send(embed=embed)
        print(f"\n{ctx.guild} | {ctx.channel}\n{ctx.author} reports: {message}\n")
        await ctx.send(f"Your message *\"{message}\"* has been sent to Willa! Thank you for your feedback!")

    @report.error
    async def report_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            error_msg = str(error)
            T_ind = error_msg.find("T")
            error_msg = error_msg[T_ind:]
            user = ctx.message.author
            await ctx.send("Slow down " + user.mention + "! The command is on cooldown! " + error_msg + ".")
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("You cannot report an empty message!")
        else:
            await ctx.send("Unknown error. Please tell Willa.")
            print(error)


def setup(bot):
    bot.add_cog(Bot(bot))
