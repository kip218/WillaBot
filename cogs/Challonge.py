import discord
from discord.ext import commands
import challonge
from settings import challonge_token
import sqlite3
import datetime
from dateutil import tz
import random
import string

challonge.set_credentials("WillaBot", challonge_token)

conn = sqlite3.connect("database.db")
c = conn.cursor()

create_tournaments_table = """ CREATE TABLE IF NOT EXISTS tournaments (
                                    url text PRIMARY KEY,
                                    name text NOT NULL,
                                    ID text NOT NULL,
                                    creator text NOT NULL,
                                    admins text ,
                                    ); """

create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                    user_id text PRIMARY KEY,
                                    tournaments text,
                                    challonge_id text,
                                    ); """


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

    @chal.command()
    async def create(self, ctx):
        try:
            await ctx.message.author.send("```Please answer the following questions in the appropriate format. Your tournament will be created after this process is done. The bot will time out if each question isn't answered within 30 minutes. Because the challonge function is still in development, please let Willa know if you encounter any errors!```")
        except:
            await ctx.send("Something went wrong! Please tell Willa.")
            return

        def check(m):
            return not m.author.bot and m.channel == ctx.message.author.dm_channel

        question = await ctx.message.author.send("What is the name of the tournament?\n\n**Tournament name:** ")
        try:
            answer = await self.bot.wait_for('message', check=check, timeout=1800)
        except:
                await ctx.message.author.send("Sorry, something went wrong. Please tell Willa.")
        else:
            await question.edit(content="```Tournament name: " + answer.content + "```")
            name = answer.content

        question = await ctx.message.author.send("Tournament type?\n\n**Options:** \n- 'single elimination'\n- 'double elimination'")
        answered = False
        while answered is False:
            try:
                answer = await self.bot.wait_for('message', check=check, timeout=1800)
            except:
                return
            else:
                if answer.content.lower() == 'single elimination' or answer.content.lower() == 'double elimination':
                    await question.edit(content="```Tournament type: " + answer.content + "```")
                    tournament_type = answer.content
                    answered = True
                else:
                    await ctx.send("Invalid input. Please choose from the options given, and make sure you don't have a typo.")

        question = await ctx.message.author.send("**Tournament description:** ")
        try:
            answer = await self.bot.wait_for('message', check=check, timeout=1800)
        except:
            await ctx.message.author.send("Sorry, something went wrong. Please tell Willa.")
        else:
            await question.edit(content="```Tournament description: " + answer.content + "```")
            description = answer.content

        question = await ctx.message.author.send("When will the tournament start?\n\n**Format:** \"year-month-day hour:minute UTCtimezone\"\n**Example response:** \"2018-07-15 16:30 +8\"\n\nIf you're not sure which timezone you're in: https://www.timeanddate.com/time/map/")
        answered = False
        while answered is False:
            try:
                answer = await self.bot.wait_for('message', check=check, timeout=1800)
            except:
                await ctx.message.author.send("Sorry, something went wrong. Please tell Willa.")
            else:
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
                    await ctx.send("Invalid input. Please make sure you're following the format.")
                else:
                    time_now = datetime.datetime.utcnow()
                    start_time = datetime.datetime(year, month, day, hour, minute, tzinfo=tzlocal)
                    if start_time - time_now < 0:
                        await ctx.send("The starting time of the tournament must be in the future!")
                    else:
                        await question.edit(content="```Start time: " + answer.content + "```")
                        answered = True

        question = await ctx.message.author.send("Check-in duration? (in minutes)\nExample response: \"60\"\n\n**Check-in duration:** ")
        answered = False
        while answered is False:
            try:
                answer = await self.bot.wait_for('message', check=check, timeout=1800)
            except:
                await ctx.message.author.send("Sorry, something went wrong. Please tell Willa.")
            else:
                try:
                    check_in = int(answer.content)
                except:
                    await ctx.send("Invalid input. Please input an integer.")
                else:
                    await question.edit(content="```Check-in duration: " + answer.content + "```")
                    answered = True

        created = False
        while created is False:
            try:
                url = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(8))
                await ctx.send(url)
                created_tournament = challonge.tournaments.create(
                                            name=name,
                                            url=url,
                                            tournament_type=tournament_type,
                                            description=description,
                                            start_at=start_time,
                                            check_in_duration=check_in,
                                            open_signup=True
                                            )
            except:
                print("Failed to create tournament")
            else:
                await ctx.send("Your tournament has been created!\nTournament challonge link: https://challonge.com/" + url)
                created = True

    @chal.command()
    async def info(self, ctx, url):
        slash_ind = url.rfind("com/")
        url_tail = url[slash_ind+4:]
        try:
            tournament = challonge.tournaments.show(url_tail)
            participants = challonge.participants.index(url_tail)
        except:
            await ctx.send("Tournament couldn't be found. Either the url is wrong, or the tournament wasn't created under my challonge account.")
            return
        else:
            tournament_name = tournament['name']
            tournament_id = tournament['id']
            participants_count = tournament['participants_count']
            img_url = tournament['live_image_url']
            start_time = tournament['start_at']
            lst = []
            for participant in participants:
                nickname = participant['name']
                challonge_username = participant['challonge_username']
                pair = (nickname, challonge_username)
                lst.append(str(pair))
            embed = discord.Embed(
                title="challonge link",
                description="Tournament ID: " + str(tournament_id),
                url=url,
                color=0x48d1cc
                )
            embed.set_author(name=tournament_name)
            embed.set_thumbnail(url=img_url)
            embed.add_field(name="Start time", value=str(start_time), inline=False)
            embed.add_field(name="Number of participants", value=participants_count, inline=False)
            embed.add_field(name="List of participants (nickname, username)", value=', '.join(lst), inline=False)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Challonge(bot))
