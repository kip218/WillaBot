import discord
from discord.ext import commands
import challonge
from settings import challonge_token
import datetime
from dateutil import tz
import random
import string
import psycopg2
import os

DATABASE_URL = os.environ['DATABASE_URL']

challonge.set_credentials("WillaBot", challonge_token)


class Challonge:
    '''
    Challonge commands for managing tournaments.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def chal(self, ctx):
        '''
        Group of challonge commands
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommands: list, create, remove, info")

    @chal.command()
    async def create(self, ctx):
        '''
        Create a new challonge tournament
        w.chal create
        '''
        await ctx.message.author.send("Check your DM!")
        await ctx.message.author.send("```Please answer the following questions in the appropriate format. Your tournament will be created after this process is done. The bot will time out if each question isn't answered within 10 minutes. Because the challonge function is still in development, please let Willa know if you encounter any errors!```")

        # checking command invoker
        def check(m):
            return not m.author.bot and m.channel == ctx.message.author.dm_channel

        # Game name
        question = await ctx.message.author.send("What game is the tournament for?\n\n**Game name:** ")
        try:
            answer = await self.bot.wait_for('message', check=check, timeout=600)
        except:
            await question.edit(content="```The bot has timed out!```")
            return
        else:
            await question.edit(content="```Game name: " + answer.content + "```")
            game_name = answer.content

        # Tournament name
        question = await ctx.message.author.send("What is the name of the tournament?\n\n**Tournament name:** ")
        try:
            answer = await self.bot.wait_for('message', check=check, timeout=600)
        except:
            await question.edit(content="```The bot has timed out!```")
            return
        else:
            await question.edit(content="```Tournament name: " + answer.content + "```")
            name = answer.content

        # Tournament type
        question = await ctx.message.author.send("Tournament type?\n\n**Options:** \n- 'single elimination'\n- 'double elimination'")
        answered = False
        while answered is False:
            try:
                answer = await self.bot.wait_for('message', check=check, timeout=600)
            except:
                await question.edit(content="```The bot has timed out!```")
                return
            else:
                if answer.content.lower() == 'single elimination' or answer.content.lower() == 'double elimination':
                    await question.edit(content="```Tournament type: " + answer.content + "```")
                    tournament_type = answer.content
                    answered = True
                else:
                    await ctx.message.author.send("Invalid input. Please choose from the options given, and make sure you don't have a typo.")

        # Tournament description
        question = await ctx.message.author.send("**Tournament description:** ")
        try:
            answer = await self.bot.wait_for('message', check=check, timeout=600)
        except:
            await question.edit(content="```The bot has timed out!```")
            return
        else:
            await question.edit(content="```Tournament description: " + answer.content + "```")
            description = answer.content

        # Start time
        question = await ctx.message.author.send("When will the tournament start? Input \"None\" if there is no planned start time.\n\n**Format:** \"year-month-day hour:minute UTCtimezone\"\n**Example response:** \"2020-07-15 16:30 +8\"\n\nIf you're not sure which timezone you're in: https://www.timeanddate.com/time/map/")
        answered = False
        while answered is False:
            try:
                answer = await self.bot.wait_for('message', check=check, timeout=600)
            except:
                await question.edit(content="```The bot has timed out!```")
            else:
                if answer.content.lower() != "none":
                    try:
                        answer_lst = answer.content.split(" ")
                        date_lst = answer_lst[0].split("-")
                        time_lst = answer_lst[1].split(":")
                        timezone_offset = int(answer_lst[2])
                        year = int(date_lst[0])
                        month = int(date_lst[1])
                        day = int(date_lst[2])
                        hour = int(time_lst[0])
                        minute = int(time_lst[1])
                        tzlocal = tz.tzoffset('UTC', timezone_offset*3600)
                    except:
                        await ctx.message.author.send("Invalid input. Please make sure you're following the format.")
                    else:
                        try:
                            time_now = datetime.datetime.now(tz=tzlocal)
                            start_time = datetime.datetime(year, month, day, hour, minute, tzinfo=tzlocal)
                        except:
                            await ctx.message.author.send("Invalid input. Please check that the date is valid.")
                        else:
                            if (start_time - time_now).total_seconds() < 0:
                                await ctx.message.author.send("The starting time of the tournament must be in the future!")
                            else:
                                await question.edit(content="```Start time: " + answer.content + "```")
                                answered = True
                                start_time_none = False
                else:
                    start_time = None
                    check_in = None
                    answered = True
                    start_time_none = True

        # Check-in duration
        if start_time_none is False:
            question = await ctx.message.author.send("Check-in duration? (in minutes & in multiples of 5)\nExample response: \"60\"\n\n**Check-in duration:** ")
            answered = False
            while answered is False:
                try:
                    answer = await self.bot.wait_for('message', check=check, timeout=1800)
                except:
                    await question.edit(content="```The bot has timed out!```")
                else:
                    try:
                        check_in = int(answer.content)
                    except:
                        await ctx.message.author.send("Invalid input. Please input an integer.")
                    else:
                        if check_in % 5 == 0:
                            await question.edit(content="```Check-in duration: " + answer.content + "```")
                            answered = True
                        else:
                            await ctx.message.author.send("Invalid input. Input must be in multiples of 5.")

        # Creating tournament through challonge API
        created = False
        counter = 0
        while created is False and counter < 20:
            try:
                url = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
                challonge.tournaments.create(
                                    name=name,
                                    url=url,
                                    tournament_type=tournament_type,
                                    description=description,
                                    start_at=start_time,
                                    check_in_duration=check_in,
                                    open_signup=True,
                                    game_name=game_name
                                    )
            except:
                print("Failed to create tournament")
                counter += 1
            else:
                await ctx.message.author.send("Your tournament has been created!\nTournament challonge link: https://challonge.com/" + url)
                created = True

                # Updating database
                # conn = psycopg2.connect(database='willabot_db')
                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                c = conn.cursor()
                tournament = challonge.tournaments.show(url)
                tournament_id = tournament['id']
                c.execute(""" INSERT INTO tournaments (ID, url, name, creator_id) 
                            VALUES (%s, %s, %s, %s); """, (tournament_id, "https://challonge.com/" + url, name, ctx.message.author.id))
                c.execute(""" UPDATE users
                            SET tournament_url_list = array_append(tournament_url_list, %s) 
                            WHERE ID = %s; """, ("https://challonge.com/" + url, str(ctx.message.author.id)))
                print("Inserted new tournament into database: " + str(tournament_id))
                conn.commit()
                conn.close()

    @chal.command()
    async def info(self, ctx, url):
        '''
        Gives information about the tournament
        w.chal info <challonge url>
        '''
        slash_ind = url.rfind("com/")
        url_tail = url[slash_ind+4:]
        try:
            tournament = challonge.tournaments.show(url_tail)
            participants = challonge.participants.index(url_tail)
        except:
            await ctx.send("Tournament couldn't be found. Either the url is wrong, or the tournament wasn't created under my challonge account.")
            return
        else:
            game_name = tournament['game_name']
            tournament_name = tournament['name']
            participants_count = tournament['participants_count']
            img_url = tournament['live_image_url']
            start_time = tournament['start_at']
            embed = discord.Embed(
                title="challonge link",
                description="Game: " + game_name,
                url=url,
                color=0x48d1cc
                )
            embed.set_author(name=tournament_name)
            embed.set_thumbnail(url=img_url)
            embed.add_field(name="Start time", value=str(start_time), inline=False)
            embed.add_field(name="Number of participants", value=str(participants_count), inline=False)
            if participants_count > 0:
                lst = []
                for participant in participants:
                    nickname = participant['name']
                    challonge_username = participant['challonge_username']
                    pair = (nickname, challonge_username)
                    lst.append(str(pair))
                participants_string = ', '.join(lst)
                embed.add_field(name="List of participants (nickname, username)", value=participants_string, inline=False)
            await ctx.send(embed=embed)

    @chal.command()
    async def list(self, ctx):
        '''
        Your list of tournaments
        w.chal list
        '''
        # conn = psycopg2.connect(database='willabot_db')
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute("SELECT * FROM tournaments WHERE creator_id=%s ORDER BY id ASC;", (str(ctx.message.author.id),))
        tournament_lst = c.fetchall()
        if len(tournament_lst) == 0:
            await ctx.send("You haven't created any tournaments! You can create a tournament with \"w.chal create\".")
        else:
            tuple_lst = []
            description = ''
            for tournament in tournament_lst:
                tuple_lst.append((tournament[2], tournament[1]))
            for i in range(len(tuple_lst)):
                tournament_name = "**" + str(i+1) + ")** " + str(tuple_lst[i][0])
                tournament_url = tuple_lst[i][1]
                description += tournament_name + "\n" + tournament_url + "\n\n"
            embed = discord.Embed(title=str(ctx.message.author.name) + "'s tournaments", description=description, color=0x48d1cc)
            await ctx.send(embed=embed)
        conn.close()

    @chal.command()
    async def remove(self, ctx, num):
        '''
        Removes a challonge tournament
        w.chal delete <tournament number>
        '''
        try:
            num = int(num)
        except:
            await ctx.send("You must input an integer.")
            return
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute("SELECT * FROM tournaments WHERE creator_id=%s ORDER BY id ASC;", (str(ctx.message.author.id), ))
        tournament_lst = c.fetchall()
        if len(tournament_lst) == 0:
            await ctx.send("You haven't created any tournaments! You can create a tournament with \"w.chal create\".")
        elif 1 <= num <= len(tournament_lst):
            tournament_id_to_delete = tournament_lst[num-1][0]
            tournament_url_to_delete = tournament_lst[num-1][1]
            tournament_name = tournament_lst[num-1][2]
            challonge.tournaments.destroy(tournament_id_to_delete)
            c.execute("DELETE FROM tournaments WHERE id=%s;", (tournament_id_to_delete, ))
            c.execute("""UPDATE users 
                        SET tournament_url_list = array_remove(tournament_url_list, %s)
                        WHERE ID = %s; """, (tournament_url_to_delete, str(ctx.message.author.id)))
            await ctx.send("Removed tournament: " + tournament_name)
        else:
            await ctx.send("You must input an integer between 1 and " + str(len(tournament_lst)))
        conn.commit()
        conn.close()


def setup(bot):
    bot.add_cog(Challonge(bot))
