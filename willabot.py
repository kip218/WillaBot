# https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import discord
from discord.ext import commands
prefix = 'w.'
bot = commands.Bot(command_prefix=prefix)
from settings import token

print(discord.__version__)


commands_lst = ['ping', 'hello', 'help', 'echo', 'invite']
help_msg = "***WillaBot Commands***\nThe prefix for the WillaBot is `w.`\n\n**w.hello**\nGreet WillaBot\n\n**w.help**\n~~You're looking right at it c:~~\n\n**w.echo [message]**\nMakes WillaBot repeat message\n\n**w.invite**\nInvite link for WillaBot"

#turtle's bot token
#NDYyOTY3MTU2MzM5MTEzOTg0.Dh0LLQ.IB7iZwJmBVPLWBRdqV9yjGLinOA
# @bot.event
# async def on_message(message):
#     if message.content.startswith('w.') and not message.author.bot:
#         msg_full = message.content
#         space_ind = msg_full.find(' ')
#         if space_ind == -1:
#             space_ind = len(msg_full)
#         command = msg_full[2:space_ind]
#         msg_rest = msg_full[space_ind:]

        
#         if command in commands_lst:
#             if command == 'ping' and msg_rest == '':
#                 await message.channel.send('PONG'.format(message))

#             elif command == 'hello' and msg_rest == '':
#                 await message.channel.send('Hello {0.author.mention}!'.format(message))

#             elif command == 'help' and msg_rest == '':
#                 await message.channel.send(help_msg)

#             elif command == 'echo':
#                 msg_echo = msg_full[space_ind+1:]
#                 if 0 < len(msg_echo) < 100:
#                     await message.channel.send(msg_echo)

#             elif command == 'invite' and msg_rest == '':
#                 await message.channel.send('**Invite link for WillaBot:**\nhttps://discordapp.com/api/oauth2/authorize?client_id=463398601553346581&permissions=0&scope=bot')

#         else:
#             await message.channel.send("Oops, wrong command! Try 'w.help' for a list of commands!")

#     #elif client.user.mentioned_in(message) and not message.author.bot:
#     #   await message.channel.send("Please don't ping me {0.author.mention}, I'm a busy bot. Try 'w.help' instead.".format(message))

#     elif message.content.lower() in ['what are you', 'what r u', 'wat are u', 'wat r you', 'what r you', 'what are u', 'wat are you', 'wat r u'] and not message.author.bot:
#         await message.channel.send("AN IDIOT SANDWICH :bread::sob::bread:")

@bot.command()
async def ping(ctx):
    '''
    Get the latency of the bot.
    '''
    latency = int(bot.latency*1000)
    msg_lst = ['Pong! ', str(latency), 'ms']
    msg = ''.join(msg_lst)
    await ctx.send(msg)


@bot.command()
async def echo(ctx, *, content:str):
    await ctx.send(content)


@bot.event
async def on_ready():
    print('Logged in as')
    #print(client.user.name)
    #print(client.user.id)
    print('------')

bot.run(token)
