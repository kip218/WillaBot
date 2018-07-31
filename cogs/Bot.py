import discord
from discord.ext import commands
from datetime import datetime

launch_time = datetime.utcnow()


class Bot:
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
        total_users = 0
        for guild in self.bot.guilds:
            total_users += len(guild.members)
        await ctx.send("WillaBot is currently exploring " + str(num) + " different servers with " + str(total_users) + " users!")

    @commands.command()
    async def server(self, ctx, *, server_name: str=None):
        '''
        Gives current server info if [server name] not specified. Name of the server can be specified to show info of that server. WillaBot needs to be a member of the server.
        w.serverinfo [server name]
        '''
        if server_name is None:
            title = ctx.guild.name
            member_count = str(len(ctx.guild.members))
            icon_url = ctx.guild.icon_url
        else:
            try:
                server_num = int(server_name)
            except ValueError:
                server_lst = self.bot.guilds
                ind = 0
                found = False
                while found == False and ind < len(server_lst):
                    curr_server = server_lst[ind]
                    if server_name.lower().replace(" ", "") in curr_server.name.lower().replace(" ", ""):
                        title = curr_server.name
                        member_count = str(len(curr_server.members))
                        icon_url = curr_server.icon_url
                        found = True
                    else:
                        ind += 1
                if found == False:
                    await ctx.send("Could not find server named \"" + server_num + "\"")
                    return
            else:
                if 1 <= server_num <= len(self.bot.guilds):
                    server = self.bot.guilds[server_num-1]
                    title = server.name
                    member_count = str(len(server.members))
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
        Invite Willabot to your server and help WillaBot explore different servers!
        w.invite
        '''
        embed = discord.Embed(
            title="Help WillaBot explore a new discord server!",
            url="https://discordapp.com/oauth2/authorize?client_id=463398601553346581&scope=bot&permissions=1077275729",
            description="*\"Nothing is pleasanter to me than exploring different discord servers.\"\n- WillaBot*",
            color=0x48d1cc
            )
        embed.set_thumbnail(
            url="https://www.eastbaytimes.com/wp-content/uploads/2016/07/20080622_025925_walle.jpg?w=360"
            )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Bot(bot))
