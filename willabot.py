# https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
from datetime import datetime
import discord
from discord.ext import commands
prefix = 'w.'
bot = commands.Bot(command_prefix=prefix)
from settings import token


commands_lst = ['ping', 'hello', 'help', 'echo', 'invite']
help_msg = "***WillaBot Commands***\nThe prefix for the WillaBot is `w.`\n\n**w.help**\n~~You're looking right at it c:~~\n"

bot.launch_time = datetime.utcnow()



#     #elif client.user.mentioned_in(message) and not message.author.bot:
#     #   await message.channel.send("Please don't ping me {0.author.mention}, I'm a busy bot. Try 'w.help' instead.".format(message))

#     elif message.content.lower() in ['what are you', 'what r u', 'wat are u', 'wat r you', 'what r you', 'what are u', 'wat are you', 'wat r u'] and not message.author.bot:
#         await message.channel.send("AN IDIOT SANDWICH :bread::sob::bread:")


@bot.command()
async def hello(ctx):
    '''
    Greet WillaBot!
    '''
    await ctx.send('Hello ' + ctx.message.author.mention + '!')


@bot.command()
async def ping(ctx):
    '''
    Latency of WillaBot
    '''
    latency = int(bot.latency*1000)
    msg_lst = ['Pong! ', str(latency), 'ms']
    msg = ''.join(msg_lst)
    await ctx.send(msg)


@bot.command()
async def uptime(ctx):
    '''
    Uptime of WillaBot
    '''
    delta_uptime = datetime.utcnow() - bot.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    await ctx.send(f"{days}d, {hours}h, {minutes}m, {seconds}s")


@bot.command()
async def echo(ctx, *, content:str):
    '''
    Makes WillaBot repeat message.
    '''
    await ctx.send(content)


@bot.command()
async def invite(ctx):
    '''
    Invite link for WillaBot. Help WillaBot explore different servers!
    '''
    await ctx.send('**Invite link for WillaBot:**\nhttps://discordapp.com/api/oauth2/authorize?client_id=463398601553346581&permissions=0&scope=bot')


@bot.event
async def on_ready():
    print(discord.__version__)
    print('Logged in as')
    #print(client.user.name)
    #print(client.user.id)
    print('------')
    game = discord.Game("w.help")
    await bot.change_presence(status=discord.Status.online, activity=game)


bot.run(token)
