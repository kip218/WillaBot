# https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import random
import sqlite3
import time
from datetime import datetime
import discord
from discord.ext import commands
from settings import token

bot = commands.Bot(command_prefix='w.')
launch_time = datetime.utcnow()


@bot.command()
async def hello(ctx):
    '''
    Greet WillaBot!
    '''
    await ctx.send('Hello ' + ctx.message.author.mention + '!')


@bot.command()
async def ping(ctx):
    '''
    WillaBot latency
    '''
    latency = int(bot.latency*1000)
    msg_lst = ['Pong! ', str(latency), 'ms']
    msg = ''.join(msg_lst)
    await ctx.send(msg)


@bot.command()
async def uptime(ctx):
    '''
    WillaBot uptime
    '''
    delta_uptime = datetime.utcnow() - launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    await ctx.send(f"{days}d {hours}h {minutes}m {seconds}s")


@bot.command()
async def servers(ctx):
    '''
    The number of servers and users using WillaBot
    '''
    num = len(bot.guilds)
    total_users = 0
    for guild in bot.guilds:
        total_users += len(guild.members)
    await ctx.send("WillaBot is currently exploring " + str(num) + " different servers with " + str(total_users) + " users!")


@bot.command()
async def serverinfo(ctx, search: str=None):
    '''
    Gives info of a server WillaBot is in. Gives current server info if [server number] not specified. 
    '''
    if search is None:
        title = ctx.guild.name
        member_count = str(len(ctx.guild.members))
        icon_url = ctx.guild.icon_url
    else:
        try:
            search = int(search)
        except:
            server_lst = bot.guilds
            ind = 0
            found = False
            while found == False and ind < len(server_lst):
                curr_server = server_lst[ind]
                if search.lower().replace(" ", "") in curr_server.name.lower().replace(" ", ""):
                    title = curr_server.name
                    member_count = str(len(ctx.guild.members))
                    icon_url = curr_server.icon_url
                    found = True
                else:
                    ind += 1
            if found == False:
                await ctx.send("Could not find server named \"" + search + "\"")
                return
        else:
            if 1 <= search <= len(bot.guilds):
                server = bot.guilds[search-1]
                title = server.name
                member_count = str(len(server.members))
                icon_url = server.icon_url
            else:
                await ctx.send("Not a valid number. Please use an integer between 0 and " + str(len(bot.guilds)))
    embed = discord.Embed(
        title=title,
        description="Member count: " + member_count,
        color=0x48d1cc
        )
    embed.set_thumbnail(
        url=icon_url
        )
    await ctx.send(embed=embed)


@bot.group()
async def echo(ctx):
    '''
    Repeats [message]
    '''
    if ctx.invoked_subcommand is None:
        content = ctx.message.content
        space_ind = content.find(' ')
        if space_ind > 4:
            content = content[space_ind+1:]
            await ctx.send(content)


@echo.command()
async def erase(ctx, *, content: str=None):
    '''
    Repeats [message] and erases the original message
    '''
    if len(ctx.message.mentions) == 0 and content is not None:
        try:
            await ctx.message.delete()
        except:
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


@bot.command()
async def invite(ctx):
    '''
    Invite link for WillaBot. Help WillaBot explore different servers!
    '''
    embed = discord.Embed(
        title="Help WillaBot explore a new discord server!",
        url="https://discordapp.com/api/oauth2/authorize?client_id=463398601553346581&permissions=0&scope=bot",
        description="*\"Nothing is pleasanter to me than exploring different discord servers.\"\n- WillaBot*",
        color=0x48d1cc
        )
    embed.set_thumbnail(
        url="https://www.eastbaytimes.com/wp-content/uploads/2016/07/20080622_025925_walle.jpg?w=360"
        )
    await ctx.send(embed=embed)


# gets embed msg of member's avatar
def get_pfp(member):
    pic_url = member.avatar_url
    title = 'Profile picture of ' + str(member)
    color = member.color
    embed = discord.Embed(title=title, color=color)
    embed.set_image(url=pic_url)
    return embed


@bot.command()
async def pfp(ctx, *, user: str=None):
    '''
    Sends [user]'s profile picture
    '''
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
        #loop to search name
        ind = 0
        found = False
        while found == False and ind < len(lst_members):
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
        if found == False:
            await ctx.send("Could not find user named \"" + user + "\"")


@bot.command()
async def calc(ctx, *, equation: str=None):
    '''
    Calculates simple arithmetic operations used in python (+, -, x, /, ^)
    '''
    equation = equation.replace("^", "**")
    equation = equation.replace("x", "*")
    try:
        res = eval(equation)
    except:
        await ctx.send("Invalid input.")
    else:
        await ctx.send(res)


@bot.event
async def on_message(message):
    #logging
    print(message.author.name + ": " + str(message.content)
    if message.content.lower() in ['what are you', 'what r u', 'wat are u', 'wat r you', 'what r you', 'what are u', 'wat are you', 'wat r u'] and not message.author.bot:
        await message.channel.send("AN IDIOT SANDWICH :bread::sob::bread:")
    if "shrug" in message.content.lower():
        await message.channel.send("¯\\_(ツ)_/¯")
    if "sosig" in message.content.lower():
        embed = discord.Embed(color= 0x48d1cc)
        embed.set_image(url="https://static.tumblr.com/90c42824de11581fb88945e0988e7510/gsvg9km/c9kov82iq/tumblr_static_tumblr_static__640.png")
        await message.channel.send(embed=embed)
    await bot.process_commands(message)


@bot.event
async def on_ready():
    print(discord.__version__)
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    game = discord.Game("w.help")
    await bot.change_presence(status=discord.Status.online, activity=game)


@bot.command()
async def shutdown(ctx):
    '''
    Shut down WillaBot
    '''
    author_id = ctx.message.author.id
    if author_id == 161774631303249921:
        await ctx.send("I need to go take a shit")
        await bot.close()
    else:
        num = random.randint(0, 1)
        if num == 0:
            await ctx.send("y tho")
        elif num == 1:
            await ctx.send("no u")


bot.run(token)
