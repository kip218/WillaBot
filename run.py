import os
import psycopg2
from datetime import datetime
import discord
from discord.ext import commands
from settings import token
import sys
import traceback

DATABASE_URL = os.environ['DATABASE_URL']

# Loading cogs (Help must always be last)
initial_extensions = ['cogs.Chat',
                      'cogs.Bot',
                      'cogs.Owner',
                      'cogs.General',
                      'cogs.Challonge',
                      'cogs.Game',
                      'cogs.Todo',
                      'cogs.Brawlhalla',
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
        if message.content.lower() in ('what are you', 'what r u', 'wat are u', 'wat r you', 'what r you', 'what are u', 'wat are you', 'wat r u'):
            await message.channel.send("AN IDIOT SANDWICH :bread::sob::bread:")

        if "shrug" in message.content.lower():
            await message.channel.send("¯\\_(ツ)_/¯")

        # add user to database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" INSERT INTO users (ID, username, xp, balance)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (ID)
                    DO NOTHING;""", (message.author.id, message.author.name, 0, 0))
        conn.commit()
        conn.close()

    await bot.process_commands(message)


@bot.event
async def on_connect():
    connect_time = str(datetime.utcnow().replace(microsecond=0))
    print("-------------------")
    print(connect_time)
    print("Connected")
    print("-------------------")

    create_tournaments_table = """ CREATE TABLE IF NOT EXISTS tournaments (
                                        ID text PRIMARY KEY,
                                        url text NOT NULL,
                                        name text NOT NULL,
                                        creator_id text NOT NULL,
                                        admin_list text[]
                                        ); """

    create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                        ID text PRIMARY KEY,
                                        username text NOT NULL,
                                        xp text NOT NULL,
                                        balance text NOT NULL,
                                        tournament_url_list text[],
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

    # conn = psycopg2.connect(database='willabot_db')
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor()
    c.execute(create_tournaments_table)
    c.execute(create_users_table)
    c.execute(create_legends_table)
    c.execute("ALTER TABLE users DROP COLUMN status;")
    c.execute("ALTER TABLE users ADD COLUMN status text[];")
    # c.execute("""UPDATE legends
    #                 SET stance_stats = '{{6,7,3,6}, {7,7,2,6}, {6,8,3,5}, {6,6,4,6}, {5,7,3,7}}'
    #                 WHERE name = 'ada' ;""")
    # c.execute("""UPDATE legends
    #                 SET weapons = '{Blasters, Spear}'
    #                 WHERE name = 'ada' ;""")

    # c.execute("""UPDATE legends
    #                 SET stance_stats = '{{5,5,4,8}, {6,5,3,8}, {4,6,4,8}, {5,5,5,7}, {5,4,5,9}}'
    #                 WHERE name = 'artemis' ;""")
    # c.execute("""UPDATE legends
    #                 SET weapons = '{Rocket Lance, Scythe}'
    #                 WHERE name = 'artemis' ;""")

    # c.execute("""UPDATE legends
    #                 SET stance_stats = '{{4,7,5,6}, {5,6,5,6}, {4,8,5,5}, {3,7,6,6}, {4,7,4,7}}'
    #                 WHERE name = 'asuri' ;""")
    # c.execute("""UPDATE legends
    #                 SET weapons = '{Katars, Sword}'
    #                 WHERE name = 'asuri' ;""")

    # c.execute("""UPDATE legends
    #                 SET stance_stats = '{{7,5,6,4}, {8,5,5,4}, {7,6,6,3}, {7,4,7,4}, {6,5,6,5}}'
    #                 WHERE name = 'azoth' ;""")
    # c.execute("""UPDATE legends
    #                 SET weapons = '{Bow, Axe}'
    #                 WHERE name = 'azoth' ;""")

    # c.execute("""UPDATE legends
    #                 SET stance_stats = '{{6,4,8,4}, {7,3,8,4}, {6,5,8,3}, {5,4,9,4}, {6,4,7,5}}'
    #                 WHERE name = 'barraza' ;""")
    # c.execute("""UPDATE legends
    #                 SET weapons = '{Axe, Blasters}'
    #                 WHERE name = 'barraza' ;""")

    # c.execute("""UPDATE legends
    #                 SET stance_stats = '{{6,6,5,5}, {7,5,5,5}, {6,7,4,5}, {6,6,6,4}, {5,6,5,6}}'
    #                 WHERE name = 'bodvar' ;""")
    # c.execute("""UPDATE legends
    #                 SET weapons = '{Hammer, Sword}'
    #                 WHERE name = 'bodvar' ;""")

    # c.execute("""UPDATE legends
    #                 SET stance_stats = '{{5,5,5,7}, {6,4,5,7}, {5,6,5,6}, {4,5,6,7}, {5,5,4,8}}'
    #                 WHERE name = 'brynn' ;""")
    # c.execute("""UPDATE legends
    #                 SET weapons = '{Axe, Spear}'
    #                 WHERE name = 'brynn' ;""")

    # c.execute("""UPDATE legends
    #                 SET stance_stats = '{{7,5,4,6}, {8,5,4,5}, {7,6,3,6}, {6,5,6,5}, {7,4,4,7}}'
    #                 WHERE name = 'caspian' ;""")
    # c.execute("""UPDATE legends
    #                 SET weapons = '{Gauntlets, Katars}'
    #                 WHERE name = 'caspian' ;""")

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
    game = discord.Game("w.help")
    await bot.change_presence(status=discord.Status.online, activity=game)


bot.run(token)
