# https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import sqlite3
import time
from datetime import datetime
import discord
from discord.ext import commands
prefix = 'w.'
bot = commands.Bot(command_prefix=prefix)
from settings import token


help_msg = "***WillaBot Commands***\nThe prefix for the WillaBot is `w.`\n\n**w.help**\n~~You're looking right at it c:~~\n"

launch_time = datetime.utcnow()
mute = True

# @bot.command()
# async def help(ctx):
#     await cts.send("Help menu in the works")


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
    await ctx.send(f"{days}d, {hours}h, {minutes}m, {seconds}s")


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
async def serverinfo(ctx, num: str=None):
    '''
    Gives info of a server WillaBot is in. Gives current server info if [server number] not specified. 
    '''
    if num is None:
        title = ctx.guild.name
        member_count = str(len(ctx.guild.members))
        icon_url = ctx.guild.icon_url
    else:
        try:
            num = int(num)
        except:
            await ctx.send("Not a valid number. Please use an integer between 0 and " + str(len(bot.guilds)))
            return
        else:
            if 1 <= num <= len(bot.guilds):
                server = bot.guilds[num-1]
                title = server.name
                member_count = str(len(server.members))
                icon_url = server.icon_url
            else:
                await ctx.send("Not a valid number. Please use an integer between 0 and " + str(len(bot.guilds)))
    embed = discord.Embed(title=title, description="Member count: " + member_count, color=0x48d1cc)
    embed.set_thumbnail(url=icon_url)
    await ctx.send(embed=embed)


@bot.group()
async def echo(ctx):
    '''
    Repeats [message]
    '''
    if ctx.invoked_subcommand is None:
        content = ctx.message.content
        space_ind = content.find(' ')
        content = content[space_ind+1:]
        await ctx.send(content)

@echo.command()
async def erase(ctx, *, content: str):
    '''
    Repeats [message] and erases the original message
    '''
    try:
        await ctx.message.delete()
        await ctx.send(content)
    except:
        await ctx.send("I don't have permission to delete messages!")


@bot.command()
async def invite(ctx):
    '''
    Invite link for WillaBot. Help WillaBot explore different servers!
    '''
    embed = discord.Embed(title="Help WillaBot explore a new discord server!", url="https://discordapp.com/api/oauth2/authorize?client_id=463398601553346581&permissions=0&scope=bot", description="*\"Nothing is pleasanter to me than exploring different discord servers.\"\n- WillaBot*", color=0x48d1cc)
    embed.set_thumbnail(url="https://www.eastbaytimes.com/wp-content/uploads/2016/07/20080622_025925_walle.jpg?w=360")
    await ctx.send(embed=embed)


#gets embed msg of member's avatar
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


# mute = False
# def stfu_helper(mute):
#     if mute == False:
#         mute = True
#     else:
#         mute = False

# @bot.command()
# async def stfu(ctx):
    '''
    Toggles all commands that don't use the prefix
    '''
#     stfu_helper(mute)
#     if mute == False:
#         await ctx.send("WillaBot is now free to talk!")
#     elif mute == True:
#         await ctx.send("WillaBot will now shut the fuck up.")


@bot.event
async def on_message_delete(message):
    if not message.author.bot and not mute:
        user = message.author
        msg = message.content
        await message.channel.send(str(user.mention) + " said \"" + msg + "\" and tried to delete it")


@bot.event
async def on_message(message):
    if message.content.lower() in ['what are you', 'what r u', 'wat are u', 'wat r you', 'what r you', 'what are u', 'wat are you', 'wat r u'] and not message.author.bot:
        await message.channel.send("AN IDIOT SANDWICH :bread::sob::bread:")
    elif bot.user.mentioned_in(message) and not message.author.bot and not mute:
        await message.channel.send("Please don't ping me " + message.author.mention + ", I'm a busy bot. Try 'w.help' instead.")
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


bot.run(token)
