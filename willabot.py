# https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import discord
from discord.ext import commands

TOKEN = 'NDYzMzk4NjAxNTUzMzQ2NTgx.Dhv1Vw.QzH5NH35pc0R3OV8dpGIlKyoobU'

client = discord.Client()

commands_lst = ['hello', 'help', 'echo', 'invite', 'roles']
help_msg = "***WillaBot Commands***\nThe prefix for the WillaBot is `w.`\n\n**w.hello**\nGreet WillaBot\n\n**w.help**\n~~You're looking at it right now c:~~\n\n**w.echo [message]**\nMakes WillaBot repeat message\n\n**w.invite**\nInvite link for WillaBot"


@client.event
async def on_message(message):
    if message.content.startswith('w.') and not message.author.bot:
        msg_full = message.content
        space_ind = msg_full.find(' ')
        if space_ind == -1:
            space_ind = len(msg_full)
        command = msg_full[2:space_ind]

        
        if command in commands_lst:
            if command == 'hello':
                await message.channel.send('Hello {0.author.mention}!'.format(message))

            elif command == 'help':
                await message.channel.send(help_msg)

            elif command == 'echo':
                msg_echo = msg_full[space_ind+1:]
                if 0 < len(msg_echo) < 50:
                    await message.channel.send(msg_echo)

            elif command == 'invite':
                await message.channel.send('**Invite link for WillaBot:**\nhttps://discordapp.com/api/oauth2/authorize?client_id=463398601553346581&permissions=0&scope=bot')

            elif command == 'roles':
                roles_lst = guild.roles
                await message.channel.send(roles_lst)

        else:
            await message.channel.send("Oops, wrong command! Try 'w.help' for a list of commands!")

    if client.user.mentioned_in(message) and not message.author.bot:
        await message.channel.send("Please don't ping me {0.author.mention}, I'm a busy bot. Try 'w.help' instead.".format(message))


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)