# https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import time
from datetime import datetime
import discord
from discord.ext import commands
prefix = 'w.'
bot = commands.Bot(command_prefix=prefix)
from settings import token


help_msg = "***WillaBot Commands***\nThe prefix for the WillaBot is `w.`\n\n**w.help**\n~~You're looking right at it c:~~\n"


bot.launch_time = datetime.utcnow()


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
    delta_uptime = datetime.utcnow() - bot.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    await ctx.send(f"{days}d, {hours}h, {minutes}m, {seconds}s")


@bot.command()
async def servers(ctx):
    '''
    The number of servers using WillaBot
    '''
    num = len(bot.guilds)
    await ctx.send("WillaBot is currently exploring " + str(num) + " different servers!")


@bot.command()
async def echo(ctx, *, content:str):
    '''
    Repeats [message]
    '''
    await ctx.send(content)


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

#checks display_name for str
# def check_display_name(str, display_name):
#     slider = -1
#     for i in len(str):
#         if str[i] in display_name:
#             ind = display_name.find(str[i])
#             if ind > slider:
#                 slider = ind

@bot.command()
async def pfp(ctx, user: str=None):
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
        lst_display_names = []
        lst_member_names = []
        for member in lst_members:
            lst_display_names.append(member.display_name.lower())
            lst_member_names.append(member.name.lower())
        ind = 0
        found = False
        while found == False and ind < len(lst_members):
            curr_display_name = lst_display_names[ind]
            curr_member_name = lst_member_names[ind]
            if user.lower() in curr_display_name:
                member = lst_members[ind]
                embed = get_pfp(member)
                await ctx.send(embed=embed)
                found = True
            elif user.lower() in curr_member_name:
                member = lst_members[ind]
                embed = get_pfp(member)
                await ctx.send(embed=embed)
                found = True
            else:
                ind += 1
        if found == False:
            await ctx.send("Could not find user named \"" + user + "\"")

@bot.event
async def on_message(message):
    if message.content.lower() in ['what are you', 'what r u', 'wat are u', 'wat r you', 'what r you', 'what are u', 'wat are you', 'wat r u'] and not message.author.bot:
        await message.channel.send("AN IDIOT SANDWICH :bread::sob::bread:")
    elif bot.user.mentioned_in(message) and not message.author.bot:
        await message.channel.send("Please don't ping me, " + message.author.mention + "I'm a busy bot. Try 'w.help' instead.")
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
