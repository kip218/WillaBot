# https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import discord
from discord.ext import commands

TOKEN = 'NDYzMzk4NjAxNTUzMzQ2NTgx.Dhv1Vw.QzH5NH35pc0R3OV8dpGIlKyoobU'
TOKEN2 = 'NDYzNDE3NDAzMDcwNDgwNDE0.Dhzvmg.xDLPYzGYnexTXX3zSM5DzffOmK8'

client = discord.Client()

commands_lst = ['hello', 'help', 'echo', 'invite', 'roles']
help_msg = "***WillaBot Commands***\nThe prefix for the WillaBot is `w.`\n\n**w.hello**\nGreet WillaBot\n\n**w.help**\n~~You're looking right at it c:~~\n\n**w.echo [message]**\nMakes WillaBot repeat message\n\n**w.invite**\nInvite link for WillaBot"


@client.event
async def on_message(message):
    if message.content.startswith('w.') and not message.author.bot:
        msg_full = message.content
        space_ind = msg_full.find(' ')
        if space_ind == -1:
            space_ind = len(msg_full)
        command = msg_full[2:space_ind]
        msg_rest = msg_full[space_ind:]

        
        if command in commands_lst:
            if command == 'hello' and msg_rest == '':
                await message.channel.send('Hello {0.author.mention}!'.format(message))

            elif command == 'help' and msg_rest == '':
                await message.channel.send(help_msg)

            elif command == 'echo':
                msg_echo = msg_full[space_ind+1:]
                if 0 < len(msg_echo) < 50:
                    await message.channel.send(msg_echo)

            elif command == 'invite' and msg_rest == '':
                await message.channel.send('**Invite link for WillaBot:**\nhttps://discordapp.com/api/oauth2/authorize?client_id=463398601553346581&permissions=0&scope=bot')

            elif command == 'roles':
                roles_lst = guild.roles
                await message.channel.send(roles_lst)

        else:
            await message.channel.send("Oops, wrong command! Try 'w.help' for a list of commands!")

    elif client.user.mentioned_in(message) and not message.author.bot:
        await message.channel.send("Please don't ping me {0.author.mention}, I'm a busy bot. Try 'w.help' instead.".format(message))

    elif message.content.lower() in ['what are you', 'what r u', 'wat are u', 'wat r you', 'what r you', 'what are u', 'wat are you', 'wat r u'] and not message.author.bot:
        await message.channel.send("AN IDIOT SANDWICH :bread::sob::bread:")



@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)