import os
import psycopg2
from datetime import datetime
import discord
from discord.ext import commands
from settings import token
import sys
import traceback
import random

DATABASE_URL = os.environ['DATABASE_URL']

# Loading cogs (Help must always be last)
initial_extensions = ['cogs.Chat',
                      'cogs.Bot',
                      'cogs.Owner',
                      'cogs.General',
                      'cogs.Game',
                      'cogs.Todo',
                      'cogs.Brawlhalla',
                      'cogs.Fun',
                      'cogs.Help']

bot = commands.Bot(command_prefix='w.')
bot.remove_command("help")


if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()


@bot.event
async def on_command(ctx):
    # add user to database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor()
    c.execute(""" INSERT INTO users (ID, username, xp, balance)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (ID)
                DO NOTHING;""", (ctx.author.id, ctx.author.name, 0, 0))
    conn.commit()
    conn.close()


@bot.event
async def on_message(message):
    # logging
    # time = str(message.created_at.replace(microsecond=0))
    user = str(message.author)
    msg = message.clean_content
    if isinstance(message.channel, discord.TextChannel):
        channel = message.channel.name
        server = message.guild.name
    elif isinstance(message.channel, discord.DMChannel):
        channel = str(message.channel.recipient)
        server = "DMChannel"
    print(server + "| " + channel + "| " + user + ": " + msg)

    if not message.author.bot:
        # add user to database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" INSERT INTO users (ID, username, xp, balance)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (ID)
                    DO NOTHING;""", (message.author.id, message.author.name, 0, 0))
        c.execute(""" UPDATE users SET username = %s
                    WHERE ID = %s
                    AND username != %s    ; """, (message.author.name, str(message.author.id), message.author.name))
        c.execute(""" SELECT xp FROM users
                    WHERE ID = %s; """, (str(message.author.id),))
        xp = c.fetchone()
        if xp is not None:
            author_xp = int(xp[0])
            author_xp += random.randint(4, 8)
        c.execute(""" UPDATE users SET xp = %s WHERE ID = %s; """, (str(author_xp), str(message.author.id)))

        if isinstance(message.channel, discord.TextChannel):
            # add channel to database
            c.execute(""" INSERT INTO channels (channel_id, channel_name, guild_id, guild_name)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (channel_id)
                        DO NOTHING;""", (message.channel.id, message.channel.name, message.guild.id, message.guild.name))
        conn.commit()
        conn.close()

    await bot.process_commands(message)


@bot.event
async def on_guild_join(guild):
    # notify me when bot joins server
    embed = discord.Embed(
            title="WillaBot joined a new server!",
            description=f"Server name: {guild.name}\nServer ID: {guild.id}\nMember count: {guild.member_count}\nServer owner: {guild.owner}",
            color=0x4CC417
            )
    embed.set_thumbnail(
            url=guild.icon_url
            )
    owner = bot.get_user(161774631303249921)
    await owner.send(embed=embed)
    print(f"WillaBot joined a new server!\nServer name: {guild.name}\nServer ID: {guild.id}\nMember count: {guild.member_count}\nServer owner: {guild.owner}")


@bot.event
async def on_guild_remove(guild):
    # notify me when bot leaves server)
    embed = discord.Embed(
            title="WillaBot left a server!",
            description=f"\nServer name: {guild.name}\nServer ID: {guild.id}\nMember count: {guild.member_count}\nServer owner: {guild.owner}\n",
            color=0xED1C24
            )
    embed.set_thumbnail(
            url=guild.icon_url
            )
    owner = bot.get_user(161774631303249921)
    await owner.send(embed=embed)
    print(f"\nWillaBot left a server!\nServer name: {guild.name}\nServer ID: {guild.id}\nMember count: {guild.member_count}\nServer owner: {guild.owner}\n")


@bot.event
async def on_connect():
    connect_time = str(datetime.utcnow().replace(microsecond=0))
    print("-------------------")
    print(connect_time)
    print("Connected")
    print("-------------------")

    create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                        ID text PRIMARY KEY,
                                        username text NOT NULL,
                                        xp text NOT NULL,
                                        balance text NOT NULL,
                                        selected_legend_key text,
                                        legends_lst text[][],
                                        todo_list text[],
                                        daily_time timestamp,
                                        status text[]
                                        ); """

    create_legends_table = """ CREATE TABLE IF NOT EXISTS legends (
                                        key text PRIMARY KEY,
                                        name text NOT NULL,
                                        skin text NOT NULL,
                                        color text NOT NULL,
                                        stance_stats text[][] NOT NULL,
                                        weapons text[] NOT NULL
                                        ); """

    create_server_channel_table = """ CREATE TABLE IF NOT EXISTS channels (
                                        channel_id text PRIMARY KEY,
                                        channel_name text NOT NULL,
                                        guild_id text NOT NULL,
                                        guild_name text NOT NULL,
                                        status text[]); """

    # conn = psycopg2.connect(database='willabot_db')
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor()
    c.execute(create_users_table)
    c.execute(create_legends_table)
    c.execute(create_server_channel_table)
    c.execute("ALTER TABLE users DROP COLUMN status;")
    c.execute("ALTER TABLE users ADD COLUMN status text[];")
    c.execute("ALTER TABLE channels DROP COLUMN status;")
    c.execute("ALTER TABLE channels ADD COLUMN status text[];")
    conn.commit()
    conn.close()


@bot.event
async def on_ready():
    ready_time = str(datetime.utcnow().replace(microsecond=0))
    print("-------------------")
    print(ready_time)
    print("Version: " + discord.__version__)
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("-------------------")
    game = discord.Game("w.help (unmaintained)")
    await bot.change_presence(status=discord.Status.online, activity=game)


bot.run(token)
