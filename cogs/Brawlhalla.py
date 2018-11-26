import discord
from discord.ext import commands
import psycopg2
import os
import asyncio
import requests
import imgix
import math
from .Brawler import Brawler

DATABASE_URL = os.environ['DATABASE_URL']


def level_currxp_nextxp(xp):
    import math
    xp = int(xp)
    level = math.floor(0.1*((xp+100)**0.5))
    floor_level_xp = ((level*10)**2)-100
    curr_xp = xp - floor_level_xp
    next_level_xp_total = (((level+1)*10)**2)-100
    next_level_xp = next_level_xp_total - floor_level_xp
    return level, curr_xp, next_level_xp


class Brawlhalla:
    '''
    Commands for Brawlhalla.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="[legend] / [skin] / [color]")
    async def info(self, ctx, *, msg: str=None):
        '''
        Your selected legend. Gives info of a Brawlhalla legend/skin/color if specified.
        w.info

        Leave [skin]/[color] empty to get the default skin/color.
        For example:
        - "w.info ada" gives default skin default color ada
        - "w.info ada//black" gives default skin black ada
        - "w.info ada/atlantean" gives default color atlantean ada
        '''
        # if no arguments given, fetch the user's selected legend
        if msg is None:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute("""SELECT selected_legend_key FROM users
                            WHERE ID = %s """, (str(ctx.author.id),))
            selected_legend_key = c.fetchone()[0]
            # return if user hasn't selected a legend
            if selected_legend_key is None:
                await ctx.send("You have not selected a legend yet! Use \"w.inven legends\" to see your legends and \"w.select <legend>/<skin>/<color>\" to select a legend!")
                conn.close()
                return
            # checking legends lst for selected legend
            c.execute(""" SELECT legends_lst FROM users
                            WHERE ID = %s """, (str(ctx.author.id),))
            legends_lst = c.fetchone()[0]
            # searching legend_lst for legend_key
            for legend in legends_lst:
                if legend[0] == selected_legend_key:
                    selected_legend = legend
            key = selected_legend[0]
            legend_name = selected_legend[1].capitalize()
            # checking spaces between legend names
            if legend_name.lower() in ['lordvraxx', 'queennai', 'sirroland']:
                if legend_name.lower() == 'lordvraxx':
                    legend_name = 'Lord Vraxx'
                elif legend_name.lower() == 'queennai':
                    legend_name = 'Queen Nai'
                elif legend_name.lower() == 'sirroland':
                    legend_name = 'Sir Roland'
            skin = selected_legend[2].capitalize()
            color = selected_legend[3].capitalize()
            stance_num = int(selected_legend[4])
            xp = int(selected_legend[5])
            level, curr_xp, next_xp = level_currxp_nextxp(xp)
            stance_lst = ['Default', 'Strength', 'Dexterity', 'Defense', 'Speed']
            c.execute("""SELECT stance_stats, weapons FROM legends
                            WHERE key = %s; """, (key,))
            row = c.fetchone()
            stats_lst = row[0][stance_num]
            weapons = row[1]
            embed = discord.Embed(title=f"Level {level} {skin} {legend_name}", description=f"{curr_xp}/{next_xp}XP", color=ctx.author.color)
            embed.add_field(name=f"{stance_lst[stance_num]} Stance", value=f"**Str:** {stats_lst[0]}\n**Dex:** {stats_lst[1]}\n**Def:** {stats_lst[2]}\n**Spd:** {stats_lst[3]}", inline=True)
            embed.add_field(name="Weapons", value=f"{weapons[0]}\n{weapons[1]}", inline=True)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_image(url=f"https://s3.amazonaws.com/willabot-assets/{key}")
            embed.set_footer(text="Use \"w.stance <stance>\" to change the stance.")
            # showing selected legend number out of list of legends
            # c.execute("""SELECT legends_lst FROM users
            #                 WHERE ID = %s; """, (str(ctx.author.id),))
            # legends_lst = c.fetchone()[0]
            # for ind in range(len(legends_lst)):
            #     if legends_lst[ind][0] == key:
            #         legend_number = ind+1
            # embed.set_footer(text=f"Selected Legend: {legend_number}/{len(legends_lst)}")
            await ctx.send(embed=embed)
            conn.close()
            return

        # clean user input
        def clean_input(msg):
            if msg is not None:
                msg_lst = msg.split('/')
                msg_lst_clean = []
                for value in msg_lst:
                    value = value.replace(' ', '')
                    value = value.replace('\'', '')
                    value = value.replace('-', '')
                    value = value.replace('_', '')
                    value = value.replace('.', '')
                    value = value.replace(',', '')
                    value = value.lower()
                    msg_lst_clean.append(value)

                legend_name = msg_lst_clean[0]
                try:
                    skin = msg_lst_clean[1]
                    if skin == '':
                        skin = 'base'
                except IndexError:
                    skin = 'base'
                try:
                    color = msg_lst_clean[2]
                    if color == '':
                        color = 'classic'
                except IndexError:
                    color = 'classic'
                return (legend_name, skin, color)
            else:
                return None

        # get embed of legend/skin/color
        def get_embed(row):
            full_key = row[0]
            name = row[1].capitalize()
            # checking spaces between legend names
            if name.lower() in ['lordvraxx', 'queennai', 'sirroland']:
                if name.lower() == 'lordvraxx':
                    name = 'Lord Vraxx'
                elif name.lower() == 'queennai':
                    name = 'Queen Nai'
                elif name.lower() == 'sirroland':
                    name = 'Sir Roland'
            skin = row[2].capitalize()
            color = row[3].capitalize()
            embed = discord.Embed(title=f"{skin} {name} *({color})*", color=0x36393E)
            embed.set_image(url="https://s3.amazonaws.com/willabot-assets/" + full_key)
            # setting up stats and weapons
            default_stats = row[4][0]
            weapons = row[5]
            embed.add_field(name="Stats", value=f"**Str:** {default_stats[0]}\n**Dex:** {default_stats[1]}\n**Def:** {default_stats[2]}\n**Spd:** {default_stats[3]}", inline=True)
            embed.add_field(name="Weapons", value=f"{weapons[0]}\n{weapons[1]}", inline=True)
            return embed

        legend_name, skin, color = clean_input(msg)
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute("""SELECT key, name, skin, color, stance_stats, weapons FROM legends
                        WHERE name LIKE '%%'||%s||'%%'
                            AND skin LIKE '%%'||%s||'%%'
                            AND color LIKE '%%'||%s||'%%'; """, (legend_name, skin, color))
        row = c.fetchone()
        found = False
        if row is not None:
            embed = get_embed(row)
            await ctx.send(embed=embed)
            found = True
        # search again if classic color does not exist for skin
        elif color == 'classic':
            c.execute("""SELECT key, name, skin, color, stance_stats, weapons FROM legends
                WHERE name LIKE '%%'||%s||'%%'
                    AND skin LIKE '%%'||%s||'%%'; """, (legend_name, skin))
            row = c.fetchone()
            # only search for color and send embed if skin can be found
            if row is not None:
                embed = get_embed(row)
                await ctx.send(embed=embed)
                found = True
        # if not found, send help message
        if found is False:
            await ctx.send("Legend/skin/color not found! Use \"w.store stock [legend] [skin]\" to see a list of available legends/skins/colors!")
        conn.close()

    @commands.group(invoke_without_command=True)
    async def inven(self, ctx):
        '''
        Your Brawlhalla inventory.
        w.inven
        '''
        inven_group_command = self.bot.get_command('inven')
        subcommands_lst = []
        for subcommand in inven_group_command.commands:
            subcommands_lst.append(f"`{subcommand.name}`")
        help_msg = ', '.join(subcommands_lst)
        await ctx.send(f"Subcommands: {help_msg}")

    @inven.command()
    async def legends(self, ctx):
        '''
        Lists legends that you own.
        w.inven legends
        '''
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute("""SELECT legends_lst FROM users
                        WHERE ID = %s """, (str(ctx.author.id),))
        legends_lst = c.fetchone()[0]
        conn.close()
        if legends_lst is None:
            await ctx.send("You do not own any legends! Try \"w.store\".")
            return

        # fetching all distinct legends
        searched_legend_lst = []
        lst_legend_row = []
        for row in legends_lst:
            legend_name = row[1]
            skin = row[2]
            color = row[3]
            if skin == 'base' and color == 'classic':
                # checking spaces between legend names
                if legend_name.lower() in ['lordvraxx', 'queennai', 'sirroland']:
                    if legend_name.lower() == 'lordvraxx':
                        legend_name = 'Lord Vraxx'
                    elif legend_name.lower() == 'queennai':
                        legend_name = 'Queen Nai'
                    elif legend_name.lower() == 'sirroland':
                        legend_name = 'Sir Roland'
                searched_legend_lst.append(legend_name)
                legend_xp = row[5]
                level = level_currxp_nextxp(legend_xp)[0]
                lst_legend_row.append(f"**{legend_name.capitalize()}** | Level {level}")
        description = '\n'.join(lst_legend_row)
        embed = discord.Embed(title="Your legends:", description=description, color=0x36393E)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @inven.command()
    async def skins(self, ctx, legend: str=None):
        '''
        Lists the skins that you own for the legend.
        w.inven skins <legend>
        '''
        if legend is None:
            await ctx.send("You must specify the legend!\nw.inven skins <legend>")
            return

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute("""SELECT legends_lst FROM users
                        WHERE ID = %s """, (str(ctx.author.id),))
        legends_lst = c.fetchone()[0]
        conn.close()

        if legends_lst is None:
            await ctx.send("You do not own any legends! Try \"w.store\".")
            return

        # cleaning input
        legend = legend.replace(' ', '')
        legend = legend.replace('\'', '')
        legend = legend.replace('-', '')
        legend = legend.replace('_', '')
        legend = legend.replace('.', '')
        legend = legend.replace(',', '')
        legend = legend.lower()

        # find legend in legends_lst
        found = False
        for row in legends_lst:
            legend_name = row[1]
            if legend in legend_name:
                legend = legend_name
                found = True

        if found is False:
            await ctx.send(f"Legend \"{legend}\" not found.")
            return

        # fetching all distinct skins for legend
        searched_skin_lst = []
        for row in legends_lst:
            legend_name = row[1]
            skin = row[2]
            if skin.capitalize() not in searched_skin_lst and legend_name == legend:
                searched_skin_lst.append(skin.capitalize())

        # checking spaces between legend names for formatting
        if legend_name.lower() in ['lordvraxx', 'queennai', 'sirroland']:
            if legend_name.lower() == 'lordvraxx':
                legend_name = 'Lord Vraxx'
            elif legend_name.lower() == 'queennai':
                legend_name = 'Queen Nai'
            elif legend_name.lower() == 'sirroland':
                legend_name = 'Sir Roland'

        # if has no skins
        if len(searched_skin_lst) == 0:
            await ctx.send(f"You do not have any skins for {legend.capitalize()}!")
            return

        description = '\n'.join(searched_skin_lst)
        embed = discord.Embed(title=f"Your skins for {legend.capitalize()}:", description=description, color=0x36393E)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @inven.command(usage="<legend> / <skin>")
    async def colors(self, ctx, legend_skin: str=None):
        '''
        Lists the colors that you own for the skin.
        w.inven colors <legend> / <skin>
        '''
        # clean user input
        def clean_input(msg):
            if msg is not None:
                msg_lst = msg.split('/')
                msg_lst_clean = []
                for value in msg_lst:
                    value = value.replace(' ', '')
                    value = value.replace('\'', '')
                    value = value.replace('-', '')
                    value = value.replace('_', '')
                    value = value.replace('.', '')
                    value = value.replace(',', '')
                    value = value.lower()
                    msg_lst_clean.append(value)

                legend_name = msg_lst_clean[0]
                try:
                    skin = msg_lst_clean[1]
                    if skin == '':
                        skin = None
                except IndexError:
                    skin = None
                return (legend_name, skin)
            else:
                return (None, None)

        # cleaning input
        legend, skin = clean_input(legend_skin)

        if skin is None or legend is None:
            await ctx.send("You must specify the legend/skin!\nw.inven colors <legend> / <skin>")
            return

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute("""SELECT legends_lst FROM users
                        WHERE ID = %s """, (str(ctx.author.id),))
        legends_lst = c.fetchone()[0]
        conn.close()

        if legends_lst is None:
            await ctx.send("You do not own any legends! Try \"w.store\".")
            return

        # find legend/skin in legends_lst
        found = False
        for row in legends_lst:
            legend_name = row[1]
            skin_name = row[2]
            if legend in legend_name and skin in skin_name:
                legend = legend_name
                skin = skin_name
                found = True

        if found is False:
            await ctx.send(f"Legend/skin \"{legend}/{skin}\" not found.")
            return

        # fetching all distinct colors for skin
        searched_color_lst = []
        for row in legends_lst:
            legend_name = row[1]
            skin_name = row[2]
            color = row[3]
            if color.capitalize() not in searched_color_lst and legend_name == legend and skin_name == skin:
                searched_color_lst.append(color.capitalize())

        # checking spaces between legend names for formatting
        if legend_name.lower() in ['lordvraxx', 'queennai', 'sirroland']:
            if legend_name.lower() == 'lordvraxx':
                legend_name = 'Lord Vraxx'
            elif legend_name.lower() == 'queennai':
                legend_name = 'Queen Nai'
            elif legend_name.lower() == 'sirroland':
                legend_name = 'Sir Roland'

        # if has no skins
        if len(searched_color_lst) == 0:
            await ctx.send(f"You do not have any colors for {skin.capitalize()} {legend.capitalize()}!")
            return

        description = '\n'.join(searched_color_lst)
        embed = discord.Embed(title=f"Your colors for {skin.capitalize()} {legend.capitalize()}:", description=description, color=0x36393E)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(usage="<legend> / [skin] / [color]")
    async def select(self, ctx, *, msg):
        '''
        Select a main legend.
        w.select <legend> / [skin] / [color]
        '''
        # clean user input
        def clean_input(msg):
            if msg is not None:
                msg_lst = msg.split('/')
                msg_lst_clean = []
                for value in msg_lst:
                    value = value.replace(' ', '')
                    value = value.replace('\'', '')
                    value = value.replace('-', '')
                    value = value.replace('_', '')
                    value = value.replace('.', '')
                    value = value.replace(',', '')
                    value = value.lower()
                    msg_lst_clean.append(value)

                legend_name = msg_lst_clean[0]
                try:
                    skin = msg_lst_clean[1]
                except IndexError:
                    skin = ''
                try:
                    color = msg_lst_clean[2]
                except IndexError:
                    color = ''
                return (legend_name, skin, color)
            else:
                return None

        legend_name, skin, color = clean_input(msg)
        if skin == '' and color == '':
            skin = 'base'
            color = 'classic'

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute("""SELECT legends_lst FROM users
                        WHERE ID = %s """, (str(ctx.author.id),))
        legends_lst = c.fetchone()[0]
        if legends_lst is None:
            await ctx.send("You do not own any legends! Try \"w.store\".")
            conn.close()
            return

        # iterate through legends to find the right legend/skin/color
        select_legend_key = None
        legend_owned = False
        for legend in legends_lst:
            if legend_name in legend[1] and skin in legend[2] and color in legend[3]:
                select_legend_name = legend[1]
                select_legend_skin = legend[2]
                select_legend_color = legend[3]
                select_legend_xp = legend[5]
                select_legend_key = legend[0]
            if legend_name in legend[1] and 'base' in legend[2] and 'classic' in legend[3]:
                legend_owned = True

        # legend/skin/color can only be selected if legend is owned
        if legend_owned is False and select_legend_key is not None:
            await ctx.send("You must first own the legend before you can select the skin/color!")
            conn.close()
            return
        elif select_legend_key is None:
            await ctx.send("The legend/skin/color could not be found! Try \"w.inven legends\" or w.skin <legend>\" to see your legends/skins/colors.")
            conn.close()
            return

        # update selected_legend_key in database
        c.execute("""UPDATE users SET selected_legend_key = %s
                        WHERE ID = %s; """, (select_legend_key, str(ctx.author.id)))
        conn.commit()

        # constructing response message
        level = level_currxp_nextxp(select_legend_xp)[0]
        skin = select_legend_skin[0].upper() + select_legend_skin[1:]
        legend_name = select_legend_name[0].upper() + select_legend_name[1:]
        color = select_legend_color[0].upper() + select_legend_color[1:]
        await ctx.send(f"You selected your Level {level} {skin} {legend_name} *({color})*.")
        conn.close()

    @commands.command()
    async def stance(self, ctx, stance):
        '''
        Change your legend stance.
        w.stance <stance>

        Available stances: Default, Strength, Dexterity, Defense, Speed.
        '''
        # finding the stance index for stance_lst
        stances = ['Default', 'Strength', 'Dexterity', 'Defense', 'Speed']
        found = False
        i = 0
        while found is False and i <= 4:
            if stance.lower() in stances[i].lower():
                stance_ind = i
                found = True
            else:
                i += 1

        if found is False:
            await ctx.send("Stance not found. Your options are: Default, Strength, Dexterity, Defense, Speed.")
            return

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute("""SELECT selected_legend_key, legends_lst FROM users
                        WHERE ID = %s """, (str(ctx.author.id),))
        row = c.fetchone()
        selected_legend_key = row[0]
        legends_lst = row[1]
        if selected_legend_key is None or legends_lst is None:
            await ctx.send("You have not selected a legend or do not own a legend!")
            conn.close()
            return
        # searching legend_lst for legend_key
        found = False
        i = 0
        while found is False and i < len(legends_lst):
            if legends_lst[i][0] == selected_legend_key:
                legend_ind = i
                legend = legends_lst[legend_ind]
                found = True
            else:
                i += 1

        legend_name = legend[1]
        skin = legend[2]
        # changing stance_num
        c.execute("""UPDATE users SET legends_lst[%s][%s] = %s
                        WHERE ID = %s; """, (legend_ind+1, 5, stance_ind, str(ctx.author.id)))
        conn.commit()
        await ctx.send(f"You've selected **{stances[stance_ind]}** Stance for {skin.capitalize()} {legend_name.capitalize()}.")
        conn.close()

    @commands.group(invoke_without_command=True)
    async def store(self, ctx):
        '''
        The Brawlhalla store.
        w.store
        '''
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute("""SELECT balance FROM users
                        WHERE ID = %s """, (str(ctx.author.id),))
        balance = c.fetchone()[0]
        conn.close()
        embed = discord.Embed(description="Welcome to the store!\nUse \"w.store stock [legend] / [skin]\" to view all purchasable legends/skins/colors!\nYou must buy the legend before you can buy other skin/color combinations.", color=0xD4AF37)
        embed.set_author(name=f"Your balance: {balance} Coins", icon_url=self.bot.user.avatar_url)
        embed.add_field(name="Legend | 1,000 Coins", value="w.buy <legend>", inline=False)
        embed.add_field(name="Odin's Chest | 3,000 Coins", value="w.buy chest", inline=False)
        embed.add_field(name="Skin/Color | 8,000 Coins", value="w.buy <legend> / <skin> / <color>", inline=False)
        embed.set_footer(text="Every skin/color combination is exclusive! Buying a color for one skin will not unlock the color for other skins!")
        await ctx.send(embed=embed)

    @store.command(usage="[legend] / [skin]")
    async def stock(self, ctx, *, msg: str=None):
        '''
        Lists all available legends in the store. Specify [legend] to view all available skins for that legend. Specify [skin] to view all available colors for that skin.
        w.store stock [legend] / [skin]

        Isaiah, Jiro, Lin fei, and Zariel are currently unavailable.
        Not all skins and colors may be available.
        '''
        # clean user input
        def clean_input(msg):
            if msg is not None:
                msg_lst = msg.split('/')
                msg_lst_clean = []
                for value in msg_lst:
                    value = value.replace(' ', '')
                    value = value.replace('\'', '')
                    value = value.replace('-', '')
                    value = value.replace('_', '')
                    value = value.replace('.', '')
                    value = value.replace(',', '')
                    value = value.lower()
                    msg_lst_clean.append(value)

                legend_name = msg_lst_clean[0]
                try:
                    skin = msg_lst_clean[1]
                    if skin == '':
                        skin = None
                except IndexError:
                    skin = None
                return (legend_name, skin)
            else:
                return (None, None)

        legend_input, skin_input = clean_input(msg)

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        if msg is None:
            c.execute("""SELECT DISTINCT name FROM legends; """)
            rows = c.fetchall()
            legends_lst = []
            for row in rows:
                legend = row[0][0].upper() + row[0][1:]
                legends_lst.append(f"`{legend}`")
            embed = discord.Embed(description=', '.join(legends_lst), color=0x36393E)
            embed.set_author(name="Available legends", icon_url=self.bot.user.avatar_url)
            embed.set_footer(text="Isaiah, Jiro, Lin fei, and Zariel are currently unavailable.")
            await ctx.send(embed=embed)
        elif skin_input is None:
            # find legend matching input
            c.execute(""" SELECT DISTINCT name FROM legends
                            WHERE name LIKE '%%'||%s||'%%'; """, (legend_input,))
            row = c.fetchone()
            if row is None:
                await ctx.send("Could not find legend. Try \"w.store stock\" to see the list of legends available.")
                return
            legend_name = row[0]
            # get list of skins
            c.execute(""" SELECT DISTINCT skin FROM legends
                            WHERE name = %s; """, (legend_name,))
            rows = c.fetchall()
            skins_lst = []
            for row in rows:
                skin = row[0][0].upper() + row[0][1:]
                skins_lst.append(f"`{skin}`")
            embed = discord.Embed(description=', '.join(skins_lst), color=0x36393E)
            embed.set_author(name=f"Available skins for {legend_name}", icon_url=self.bot.user.avatar_url)
            embed.set_footer(text="Some skins may be unavailable.")
            await ctx.send(embed=embed)
        else:
            # find legend matching input
            c.execute(""" SELECT DISTINCT name FROM legends
                            WHERE name LIKE '%%'||%s||'%%'; """, (legend_input,))
            row = c.fetchone()
            if row is None:
                await ctx.send("Could not find legend. Try \"w.store stock\" to see the list of legends available.")
                return
            legend_name = row[0]
            # find skin matching input
            c.execute(""" SELECT DISTINCT skin FROM legends
                            WHERE name = %s
                            AND skin LIKE '%%'||%s||'%%'; """, (legend_name, skin_input))
            row = c.fetchone()
            if row is None:
                if row is None:
                    await ctx.send("Could not find skin. Try \"w.store stock [legend]\" to see the list of skins available for that legend.")
                return
            skin_name = row[0]
            # get list of colors
            c.execute(""" SELECT color FROM legends
                            WHERE name = %s
                            AND skin = %s; """, (legend_name, skin_name))
            rows = c.fetchall()
            colors_lst = []
            for row in rows:
                color = row[0][0].upper() + row[0][1:]
                colors_lst.append(f"`{color}`")
            embed = discord.Embed(description=', '.join(colors_lst), color=0x36393E)
            embed.set_author(name=f"Available colors for {skin_name} {legend_name}", icon_url=self.bot.user.avatar_url)
            embed.set_footer(text="Some colors may be unavailable.")
            await ctx.send(embed=embed)
        conn.close()

    @commands.command(usage="<item to buy>")
    async def buy(self, ctx, *, msg):
        '''
        Buy an item from the Brawlhalla store.
        w.buy <item to buy>
        '''
        if msg is None:
            await ctx.send("You must specify what to buy from the store. Try \"w.store\".")
            return

        # Check that the user isn't already purchasing an item
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT status FROM users WHERE ID=%s;""", (str(ctx.author.id), ))
        status_lst = c.fetchone()[0]
        if status_lst is not None:
            if "buy" in status_lst:
                await ctx.send("You're already in the purchase process! You must \"w.cancel\" your purchase to initiate a new purchase. This is to prevent accidental duplicate purchases. If you initiated a purchase process in another server/channel, make sure that purchase process is canceled or timed out. If this error continues to persist, please report it to Willa using \"w.report\".")
                conn.commit()
                conn.close()
                return
        c.execute(""" UPDATE users
                    SET status = array_append(status, %s)
                    WHERE ID = %s; """, ('buy', str(ctx.author.id)))
        conn.commit()
        conn.close()

        # clean user input
        def clean_input(msg):
            if msg is not None:
                msg_lst = msg.split('/')
                msg_lst_clean = []
                for value in msg_lst:
                    value = value.replace(' ', '')
                    value = value.replace('\'', '')
                    value = value.replace('-', '')
                    value = value.replace('_', '')
                    value = value.replace('.', '')
                    value = value.replace(',', '')
                    value = value.lower()
                    msg_lst_clean.append(value)

                legend_name = msg_lst_clean[0]
                try:
                    skin = msg_lst_clean[1]
                    if skin == '':
                        skin = 'base'
                except IndexError:
                    skin = 'base'
                try:
                    color = msg_lst_clean[2]
                    if color == '':
                        color = 'classic'
                except IndexError:
                    color = 'classic'
                return (legend_name, skin, color)
            else:
                return None

        def check_confirm(m):
                return m.author == ctx.author and m.content.lower() in ['w.confirm', 'w.cancel'] and m.channel == ctx.channel

        # removing 'buy' from status_lst
        def remove_status():
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute(""" UPDATE users
                        SET status = array_remove(status, %s)
                        WHERE ID = %s; """, ('buy', str(ctx.author.id)))
            conn.commit()
            conn.close()

        # get embed of legend/skin/color
        def get_embed(row, color_code, price):
            full_key = row[0]
            name = row[1].capitalize()
            # checking spaces between legend names
            if name.lower() in ['lordvraxx', 'queennai', 'sirroland']:
                if name.lower() == 'lordvraxx':
                    name = 'Lord Vraxx'
                elif name.lower() == 'queennai':
                    name = 'Queen Nai'
                elif name.lower() == 'sirroland':
                    name = 'Sir Roland'
            skin = row[2].capitalize()
            color = row[3].capitalize()
            embed = discord.Embed(title=f"{skin} {name} *({color})*", description=f"Are you sure you want to buy this legend/skin/color?\n{price} Coins will be deducted from your profile.\nType \"w.confirm\" to confirm purchase and \"w.cancel\" to cancel.", color=color_code)
            embed.set_image(url="https://s3.amazonaws.com/willabot-assets/" + full_key)
            embed.set_author(name="Confirm Purchase", icon_url=self.bot.user.avatar_url)
            embed.set_footer(text="Every skin/color combination is exclusive! Buying a color for one skin will not unlock the color for other skins!")
            return embed

        # checking that the user has enough balance
        def check_balance(user_id, required_balance):
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute(""" SELECT balance FROM users
                            WHERE ID = %s; """, (str(user_id),))
            balance = int(c.fetchone()[0])
            conn.close()
            if balance < required_balance:
                return False
            else:
                return True

        # returns True if user owns default legend
        # opens a new connection
        def check_default_legend(user_id, legend_name):
            key = f'images/legends/{legend_name}_base_classic.png'
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute(""" SELECT legends_lst FROM users
                        WHERE ID = %s; """, (str(user_id), ))
            legends_lst = c.fetchone()[0]
            conn.close()
            if legends_lst is not None:
                for legend in legends_lst:
                    if key in legend:
                        return True
            return False

        # update balance in database
        # does not open new connection and takes passed connection
        def update_database_coins(user_id, delta_coins, conn):
            c = conn.cursor()
            c.execute(""" SELECT balance FROM users
                        WHERE ID = %s; """, (str(user_id), ))
            user_balance = int(c.fetchone()[0])
            user_balance += delta_coins
            c.execute(""" UPDATE users
                            SET balance = %s
                            WHERE ID = %s; """, (str(user_balance), str(user_id)))

        # buying legend/skin/color
        async def buying_legend(msg):
            # divide input by keywords and determine item purchase
            legend_name, skin, color = clean_input(msg)

            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute("""SELECT key, name, skin, color, stance_stats, weapons FROM legends
                            WHERE name LIKE '%%'||%s||'%%'
                                AND skin LIKE '%%'||%s||'%%'
                                AND color LIKE '%%'||%s||'%%'; """, (legend_name, skin, color))
            row = c.fetchone()

            # get price for embed
            if skin == 'base' and color == 'classic':
                price = 1000
            else:
                price = 8000

            found = False
            if row is not None:
                embed = get_embed(row, 0xD4AF37, price)
                found = True
            # search again if classic color does not exist for skin
            elif color == 'classic':
                c.execute("""SELECT key, name, skin, color, stance_stats, weapons FROM legends
                    WHERE name LIKE '%%'||%s||'%%'
                        AND skin LIKE '%%'||%s||'%%'; """, (legend_name, skin))
                row = c.fetchone()
                # only search for color and send embed if skin can be found
                if row is not None:
                    embed = get_embed(row, 0xD4AF37, price)
                    found = True

            # if not found, send help message
            if found is False:
                await ctx.send("Legend/skin/color not found! Use \"w.store stock [legend] / [skin]\" to see a list of available legends/skins/colors!")
                conn.close()
                remove_status()
                return

            # saving elements from row above for later use
            full_key = row[0]
            name = row[1]
            skin = row[2]
            color = row[3]
            answered = False
            confirmed = False
            if found is True:
                purchase_embed = await ctx.send(embed=embed)
                while answered is False:
                    try:
                        purchase_confirm = await self.bot.wait_for('message', check=check_confirm, timeout=60)
                    except asyncio.TimeoutError:
                        timeout_embed = get_embed(row, 0xED1C24, price)
                        timeout_embed = timeout_embed.set_footer(text="The purchase has timed out!")
                        await purchase_embed.edit(embed=timeout_embed)
                        conn.close()
                        remove_status()
                        return
                    else:
                        if purchase_confirm.content == 'w.confirm':
                            answered = True
                            confirmed = True
                        elif purchase_confirm.content == 'w.cancel':
                            await ctx.send("Purchase canceled.")
                            answered = True
                            conn.close()
                            embed = get_embed(row, 0xED1C24, price)
                            await purchase_embed.edit(embed=embed)
                            remove_status()
                            return

            if confirmed is True:
                # checking that the user does not alreay have the item
                c.execute(""" SELECT legends_lst FROM users
                                WHERE ID = %s; """, (str(ctx.author.id),))
                legends_lst = c.fetchone()[0]
                if legends_lst is not None:
                    for legend in legends_lst:
                        # full_key assigned above
                        if full_key in legend:
                            await ctx.send("You cannot buy what you already own!")
                            conn.close()
                            embed = get_embed(row, 0xED1C24, price)
                            await purchase_embed.edit(embed=embed)
                            remove_status()
                            return
                else:
                    legends_lst = []

            # checking what the user is buying
            if skin == 'base' and color == 'classic':
                if check_balance(ctx.author.id, 1000):
                    purchased_legend = [full_key, name, skin, color, '0', '0']
                    legends_lst.append(purchased_legend)
                    c.execute("""UPDATE users SET legends_lst = %s
                                    WHERE ID = %s;""", (legends_lst, str(ctx.author.id)))
                    update_database_coins(ctx.author.id, -1000, conn)
                    await ctx.send(f"You have purchased {skin} {name} *({color})*!")
                    color_code = 0x4CC417
                else:
                    await ctx.send("You don't have enough Coins!")
                    color_code = 0xED1C24
            else:
                if check_balance(ctx.author.id, 8000):
                    if check_default_legend(ctx.author.id, name):
                        purchased_legend = [full_key, name, skin, color, '0', '0']
                        legends_lst.append(purchased_legend)
                        c.execute("""UPDATE users SET legends_lst = %s
                                        WHERE ID = %s;""", (legends_lst, str(ctx.author.id)))
                        update_database_coins(ctx.author.id, -8000, conn)
                        await ctx.send(f"You have purchased {skin} {name} *({color})*!")
                        color_code = 0x4CC417
                    else:
                        await ctx.send("You must have the default legend before buying skins/colors!")
                        color_code = 0xED1C24
                else:
                    await ctx.send("You don't have enough Coins!")
                    color_code = 0xED1C24

            embed = get_embed(row, color_code, price)
            await purchase_embed.edit(embed=embed)
            conn.commit()
            conn.close()

        # get embed of chest
        def get_embed_chest(color_code, price):
            embed = discord.Embed(title=f"Odin's Chest", description=f"Are you sure you want to buy the Odin's Chest?\n{price} Coins will be deducted from your profile.\nType \"w.confirm\" to confirm purchase and \"w.cancel\" to cancel.", color=color_code)
            embed.set_image(url="https://s3.amazonaws.com/willabot-assets/images/store/Closed_Chest.png")
            embed.set_author(name="Confirm Purchase", icon_url="https://s3.amazonaws.com/willabot-assets/images/store/Closed_Chest.png")
            embed.set_footer(text="Odin's Chest will give a random legend/skin/color from all available options in the store.")
            return embed

        def get_opening_chest_embed(row, color_code):
            embed = discord.Embed(description="The Odin's Chest is being opened!", color=color_code)
            embed.set_image(url="https://s3.amazonaws.com/willabot-assets/images/store/Chest_Animation.gif")
            embed.set_author(name="Odin's Chest", icon_url="https://s3.amazonaws.com/willabot-assets/images/store/Chest_Animation.gif")
            embed.set_footer(text="Odin's Chest will give a random legend/skin/color from all available options in the store.")
            return embed

        def get_opened_chest_embed(row, color_code):
            full_key = row[0]
            name = row[1].capitalize()
            # checking spaces between legend names
            if name.lower() in ['lordvraxx', 'queennai', 'sirroland']:
                if name.lower() == 'lordvraxx':
                    name = 'Lord Vraxx'
                elif name.lower() == 'queennai':
                    name = 'Queen Nai'
                elif name.lower() == 'sirroland':
                    name = 'Sir Roland'
            skin = row[2].capitalize()
            color = row[3].capitalize()
            embed = discord.Embed(title=f"{skin} {name} *({color})*", description=f"You opened the Odin's Chest and got {skin} {name} *({color})*!", color=color_code)
            embed.set_image(url="https://s3.amazonaws.com/willabot-assets/" + full_key)
            embed.set_thumbnail(url="https://s3.amazonaws.com/willabot-assets/images/store/Chest_Animation.gif")
            embed.set_author(name="Odin's Chest", icon_url="https://s3.amazonaws.com/willabot-assets/images/store/Open_Chest.png")
            embed.set_footer(text="Every skin/color combination is exclusive! Buying a color for one skin will not unlock the color for other skins!")
            return embed

        # buying chest
        async def buying_chest():
            embed = get_embed_chest(0xD4AF37, 3000)
            purchase_embed = await ctx.send(embed=embed)
            answered = False
            while answered is False:
                try:
                    purchase_confirm = await self.bot.wait_for('message', check=check_confirm, timeout=60)
                except asyncio.TimeoutError:
                    timeout_embed = get_embed(0xED1C24, 3000)
                    timeout_embed = timeout_embed.set_footer(text="The purchase has timed out!")
                    await purchase_embed.edit(embed=timeout_embed)
                    remove_status()
                    return
                else:
                    if purchase_confirm.content == 'w.confirm':
                        answered = True
                    elif purchase_confirm.content == 'w.cancel':
                        await ctx.send("Purchase canceled.")
                        answered = True
                        embed = get_embed(0xED1C24, 3000)
                        await purchase_embed.edit(embed=embed)
                        remove_status()
                        return

            if not check_balance(ctx.author.id, 3000):
                await ctx.send("You don't have enough Coins!")
                return
            else:
                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                c = conn.cursor()

                # get legends_lst from user to check for chest rerolls
                c.execute(""" SELECT legends_lst FROM users
                                WHERE ID = %s; """, (str(ctx.author.id),))
                legends_lst = c.fetchone()[0]
                if legends_lst is None:
                    legends_lst = []

                # reroll random legend until unowned random legend found
                random_found = False
                while random_found is False:
                    c.execute("""SELECT key, name, skin, color, stance_stats, weapons FROM legends
                                WHERE skin != 'base' AND color != 'classic'
                                ORDER BY random()
                                LIMIT 1; """)
                    random_legend = c.fetchone()
                    random_legend_key = random_legend[0]

                    # looping to find if legend is already owned
                    already_owned = False
                    for owned_legend in legends_lst:
                        if owned_legend[0] == random_legend_key:
                            already_owned = True
                    # if legend/skin/color already owned, repeat the while loop
                    if already_owned is False:
                        random_found = True

                # actual transaction
                full_key = random_legend[0]
                name = random_legend[1]
                skin = random_legend[2]
                color = random_legend[3]
                purchased_legend = [full_key, name, skin, color, '0', '0']
                legends_lst.append(purchased_legend)
                c.execute("""UPDATE users SET legends_lst = %s
                                WHERE ID = %s;""", (legends_lst, str(ctx.author.id)))
                update_database_coins(ctx.author.id, -3000, conn)
                conn.commit()
                conn.close()

                # send opening chest embed
                embed = get_opening_chest_embed(random_legend, 0x3A2166)
                await purchase_embed.edit(embed=embed)

                def check(m):
                    return False

                # timer to reveal legend
                try:
                    timer = await self.bot.wait_for('message', check=check, timeout=1.8)
                except asyncio.TimeoutError:
                    # edit to open chest embed
                    embed = get_opened_chest_embed(random_legend, 0x502D8C)
                    await purchase_embed.edit(embed=embed)

        if msg == 'chest':
            await buying_chest()
        else:
            await buying_legend(msg)
        remove_status()

    @buy.error
    async def buy_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute(""" UPDATE users
                        SET status = array_remove(status, %s)
                        WHERE ID = %s; """, ('buy', str(ctx.author.id)))
            conn.commit()
            conn.close()
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You must specify the item to buy!")
        else:
            await ctx.send("Unknown error. Please tell Willa.")
            print(error)

    @commands.command(usage="<@user>")
    async def brawl(self, ctx, user: str=None):
        '''
        Challenge someone to a brawl!
        w.brawl <@user>
        '''
        if user is None:
            await ctx.send("You must mention a user to brawl!")
            return

        player = ctx.author
        opponent = ctx.message.mentions[0]
        if opponent.bot:
            await ctx.send("You can't challenge a bot!")
            return
        if player == opponent:
            await ctx.send("You can't challenge yourself!")
            return

        # check that they're not already in a game of brawl
        def check_status():
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute(""" SELECT status FROM users WHERE ID=%s;""", (str(player.id), ))
            player_status_lst = c.fetchone()[0]
            c.execute(""" SELECT status FROM users WHERE ID=%s;""", (str(opponent.id), ))
            opponent_status_lst = c.fetchone()[0]
            if player_status_lst is not None and opponent_status_lst is not None:
                if "brawl" in player_status_lst:
                    conn.commit()
                    conn.close()
                    return f"{player.mention} is already in a brawl!"
                elif "brawl" in opponent_status_lst:
                    conn.commit()
                    conn.close()
                    return f"{opponent.mention} is already in a brawl!"
            # if not, add 'brawl' to status_lst
            c.execute(""" UPDATE users
                        SET status = array_append(status, %s)
                        WHERE ID = %s; """, ('brawl', str(player.id)))
            c.execute(""" UPDATE users
                        SET status = array_append(status, %s)
                        WHERE ID = %s; """, ('brawl', str(opponent.id)))
            conn.commit()
            conn.close()
            return True

        # remove brawl status from status_lst
        def remove_status(player, opponent):
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute(""" UPDATE users
                        SET status = array_remove(status, %s)
                        WHERE ID = %s; """, ('brawl', str(player.id)))
            c.execute(""" UPDATE users
                        SET status = array_remove(status, %s)
                        WHERE ID = %s; """, ('brawl', str(opponent.id)))
            conn.commit()
            conn.close()

        def get_legend_url(legend_key, flip=False):
            builder = imgix.UrlBuilder("willabot-assets.imgix.net")
            slash_ind = legend_key.rfind('/')
            underscore_ind = legend_key.find('_')
            legend_name = legend_key[slash_ind+1:underscore_ind]
            legends_to_reverse = ['scarlet', 'lucien']
            if legend_name.lower() in legends_to_reverse:
                flip = not flip
            if flip:
                url = builder.create_url(legend_key, {
                    'w': 500,
                    'h': 500,
                    'flip': 'h'
                    })
            else:
                url = builder.create_url(legend_key, {
                    'w': 500,
                    'h': 500
                    })
            return url

        def get_legend_height_width(legend_key):
            builder = imgix.UrlBuilder("willabot-assets.imgix.net")
            url = builder.create_url(legend_key, {
                    'fm': 'json'
                })
            json = requests.get(url).json()
            height = json['PixelHeight']
            width = json['PixelWidth']
            return height, width

        # get brawl battle img url through imgix
        def get_brawl_img_url(legend_key1, legend_key2):
            player1_legend_url = get_legend_url(legend_key1)
            height1, width1 = get_legend_height_width(legend_key1)
            player2_legend_url = get_legend_url(legend_key2, True)
            height2, width2 = get_legend_height_width(legend_key2)

            background_height = height1+height2
            background_width = 2*(width1+width2)

            builder = imgix.UrlBuilder("willabot-assets.imgix.net")
            url = builder.create_url("/images/backgrounds/Mammoth_BG.png", {
                    'fit': 'scale',
                    'w': background_width,
                    'h': background_height,
                    'mark': player1_legend_url,
                    'markfit': 'clip',
                    'markw': width1,
                    'markh': height1,
                    'markx': 0.12*background_width,
                    'marky': 0.8*background_height-height1,
                    'blend': player2_legend_url,
                    'bm': 'normal',
                    'balph': 100,
                    'bf': 'clip',
                    'bw': width2,
                    'bh': height2,
                    'bx': 0.88*background_width-width2,
                    'by': 0.8*background_height-height2
                    })
            return url

        def get_player_legend_lst(player):
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute("""SELECT selected_legend_key FROM users
                            WHERE ID = %s """, (str(player.id),))
            selected_legend_key = c.fetchone()[0]
            if selected_legend_key is None:
                conn.close()
                return None
            # checking legends lst for selected legend
            c.execute(""" SELECT legends_lst FROM users
                            WHERE ID = %s """, (str(player.id),))
            legends_lst = c.fetchone()[0]
            conn.close()
            # searching legend_lst for legend_key
            for legend in legends_lst:
                if legend[0] == selected_legend_key:
                    return legend

        def get_legend_stats_weapons(legend_key, stance):
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute("""SELECT stance_stats, weapons FROM legends
                            WHERE key = %s """, (legend_key,))
            row = c.fetchone()
            stance_stats = row[0]
            weapons = row[1]
            stats = stance_stats[int(stance)]
            return stats, weapons

        def get_DM_prompt_embed(moves, opponent):
            title = "The brawl has started! Select your move!"
            moves_string = ""
            for move in moves:
                moves_string += f"- {move.capitalize()}\n"
            embed = discord.Embed(title=title, description=f"Opponent: **{opponent}**", color=0x48d1cc)
            embed.add_field(name="Moves", value=moves_string)
            embed.set_footer(text="Type the move to use.")
            return embed

        # get stats, weapons, and img_url for embed
        def get_brawl_embed():
            stance_lst = ['Default', 'Strength', 'Dexterity', 'Defense', 'Speed']
            brawl_img_url = get_brawl_img_url(player_legend[0], opponent_legend[0])
            stock_emote = ":heart:"
            embed = discord.Embed(title=f"{player.name} VS {opponent.name}",
                                  description=f"{player.name}'s {player_legend[1].capitalize()}: {stock_emote*p_brawler.stocks}\n{opponent.name}'s {opponent_legend[1].capitalize()}: {stock_emote*o_brawler.stocks}",
                                  color=0x48d1cc)
            embed.add_field(name=f"{stance_lst[int(player_legend[4])]} Stance",
                            value=f"**Str:** {player_stats[0]}\n**Dex:** {player_stats[1]}\n**Def:** {player_stats[2]}\n**Spd:** {player_stats[3]}",
                            inline=True)
            embed.add_field(name=f"{stance_lst[int(opponent_legend[4])]} Stance",
                            value=f"**Str:** {opponent_stats[0]}\n**Dex:** {opponent_stats[1]}\n**Def:** {opponent_stats[2]}\n**Spd:** {opponent_stats[3]}",
                            inline=True)
            embed.set_image(url=brawl_img_url)
            return embed

        def get_game_over_embed(winner, winner_key, loser, loser_key):
            winner_url = get_legend_url(winner_key)
            loser_url = get_legend_url(loser_key)
            embed = discord.Embed(title=f"{winner.name} won!", description=f"{loser.name} lost.", color=0x48d1cc)
            embed.set_image(url=winner_url)
            embed.set_thumbnail(url=loser_url)
            embed.set_author(name="Game Over!", icon_url=self.bot.user.avatar_url)
            return embed

        check_status = check_status()
        if check_status is not True:
            await ctx.send(check_status)
            return

        challenge_msg = await ctx.send(f"{opponent.mention}! {player.mention} challenged you to a brawl!\nType \"w.accept <@user>\" to accept!")

        # checking if opponent accepts challenge
        def check_accept(m):
            return m.author == opponent and m.content.startswith('w.accept') and m.channel == ctx.channel
        accepted = False
        while accepted is False:
            try:
                accept = await self.bot.wait_for('message', check=check_accept, timeout=60)
            except asyncio.TimeoutError:
                await challenge_msg.edit(content=challenge_msg.content + "\n*The challenge has timed out!*")
                remove_status(player, opponent)
                return
            else:
                if accept.content == 'w.accept':
                    await ctx.send("You must specify the @user that challenged you!")
                elif accept.content == f'w.accept {player.mention}':
                    accepted = True

        # if one player hasn't selected a legend
        player_legend = get_player_legend_lst(player)
        opponent_legend = get_player_legend_lst(opponent)
        if player_legend is None and opponent_legend is None:
            await ctx.send("Both players have not selected a legend yet!")
        elif player_legend is None:
            await ctx.send(f"{player.mention} has not selected a legend yet!")
        elif opponent_legend is None:
            await ctx.send(f"{opponent.mention} has not selected a legend yet!")

        challenge_accepted = await ctx.send(f"{player.mention} {opponent.mention} Challenge accepted! Check your DMs!")

        # possible moves & sending both players embed through DM
        moves = ["attack", "dodge", "jump"]

        await ctx.send("Loading custom brawl game...")

        # calling function to get stats & weapons
        player_stats, player_weapons = get_legend_stats_weapons(player_legend[0], player_legend[4])
        opponent_stats, opponent_weapons = get_legend_stats_weapons(opponent_legend[0], opponent_legend[4])

        # initialize two Brawler classes
        p_brawler = Brawler(player_legend[1], player_stats,
                            player_weapons, player_legend[2],
                            player_legend[3], player_legend[0])
        o_brawler = Brawler(opponent_legend[1], opponent_stats,
                            opponent_weapons, opponent_legend[2],
                            opponent_legend[3], opponent_legend[0])

        # checking player's response
        def check_player(m):
            return m.author == player and m.content.lower() in moves

        def check_opponent(m):
            return m.author == opponent and m.content.lower() in moves

        await ctx.send(embed=get_brawl_embed())
        while p_brawler.stocks > 0 and o_brawler.stocks > 0:
            player_prompt = await player.send(embed=get_DM_prompt_embed(moves, opponent))
            opponent_prompt = await opponent.send(embed=get_DM_prompt_embed(moves, player))
            # checking players' response
            player_answered = False
            opponent_answered = False
            while player_answered is False or opponent_answered is False:
                try:
                    done, pending = await asyncio.wait([self.bot.wait_for('message', check=check_player, timeout=60), self.bot.wait_for('message', check=check_opponent, timeout=60)], return_when=asyncio.FIRST_COMPLETED)
                    msg = done.pop().result()
                except asyncio.TimeoutError:
                    player_prompt.embeds[0].set_footer(text="The game has timed out!")
                    opponent_prompt.embeds[0].set_footer(text="The game has timed out!")
                    await player_prompt.edit(embed=player_prompt.embeds[0])
                    await opponent_prompt.edit(embed=opponent_prompt.embeds[0])
                    await challenge_accepted.edit(content=f"{challenge_accepted.content}\n*The game has timed out!*")
                    remove_status(player, opponent)
                    return
                else:
                    if msg.author == player:
                        player_move = msg.content.lower()
                        if player_move == 'dodge' and p_brawler.dodge_cooldown != 0:
                            await ctx.send(f"{player.mention}, your dodge is on cooldown!")
                        elif player_move == 'jump' and p_brawler.jump_count == 3:
                            await ctx.send(f"{player.mention}, you're out of jumps!")
                        else:
                            player_answered = True
                    elif msg.author == opponent:
                        opponent_move = msg.content.lower()
                        if opponent_move == 'dodge' and o_brawler.dodge_cooldown != 0:
                            await ctx.send(f"{opponent.mention}, your dodge is on cooldown!")
                        elif opponent_move == 'jump' and o_brawler.jump_count == 3:
                            await ctx.send(f"{opponent.mention}, you're out of jumps!")
                        else:
                            opponent_answered = True

            await ctx.send(embed=get_brawl_embed())

            # update cooldowns
            p_brawler.update_cooldown()
            o_brawler.update_cooldown()

            # switch case?
            if player_move == 'attack' and opponent_move == 'attack':
                p_dmg = p_brawler.clash(o_brawler)
                o_dmg = o_brawler.clash(p_brawler)
                await ctx.send(f"CLASH!\n"
                               f"{player.name}'s {p_brawler.skin} "
                               f"{p_brawler.name} took **{o_dmg}** damage!\n"
                               f"{opponent.name}'s {o_brawler.skin} "
                               f"{o_brawler.name} took **{p_dmg}** damage!")

            elif player_move == 'attack' and opponent_move == 'dodge':
                o_dodge_type = o_brawler.add_dodge_cooldown()
                await ctx.send(f"{opponent.name} dodged ({o_dodge_type}) "
                               f"{player.name}'s light attack!")

            elif player_move == 'attack' and opponent_move == 'jump':
                o_jumps = o_brawler.add_jump_count()
                if o_brawler.jump(p_brawler):
                    await ctx.send(f"{opponent.name} jumped (remaining jumps: {o_jumps}) over "
                                   f"{player.name}'s light attack!")
                else:
                    p_dmg = p_brawler.attack(o_brawler)
                    await ctx.send(f"{player.name}'s light attack caught "
                                   f"{opponent.name}'s jump (remaining jumps: {o_jumps}) "
                                   f"for **{p_dmg}** damage!")

            elif player_move == 'dodge' and opponent_move == 'attack':
                p_dodge_type = p_brawler.add_dodge_cooldown()
                await ctx.send(f"{player.name} dodged ({p_dodge_type}) "
                               f"{opponent.name}'s light attack!")

            elif player_move == 'dodge' and opponent_move == 'dodge':
                p_dodge_type = p_brawler.add_dodge_cooldown()
                o_dodge_type = o_brawler.add_dodge_cooldown()
                await ctx.send(f"{player.name} dodged ({p_dodge_type}).\n"
                               f"{opponent.name} dodged ({o_dodge_type}).")

            elif player_move == 'dodge' and opponent_move == 'jump':
                p_dodge_type = p_brawler.add_dodge_cooldown()
                o_jumps = o_brawler.add_jump_count()
                await ctx.send(f"{player.name} dodged ({p_dodge_type}).\n"
                               f"{opponent.name} jumped (remaining jumps: {o_jumps}).")

            elif player_move == 'jump' and opponent_move == 'attack':
                p_jumps = p_brawler.add_jump_count()
                if p_brawler.jump(o_brawler):
                    await ctx.send(f"{player.name} jumped (remaining jumps: {p_jumps}) over "
                                   f"{opponent.name}'s light attack!")
                else:
                    o_dmg = o_brawler.attack(p_brawler)
                    await ctx.send(f"{opponent.name}'s light attack caught "
                                   f"{player.name}'s jump (remaining jumps: {p_jumps}) "
                                   f"for **{o_dmg}** damage!")

            elif player_move == 'jump' and opponent_move == 'dodge':
                p_jumps = p_brawler.add_jump_count()
                o_dodge_type = o_brawler.add_dodge_cooldown()
                await ctx.send(f"{player.name} jumped (remaining jumps: {p_jumps}).\n"
                               f"{opponent.name} dodged ({o_dodge_type}).")

            elif player_move == 'jump' and opponent_move == 'jump':
                p_jumps = p_brawler.add_jump_count()
                o_jumps = o_brawler.add_jump_count()
                await ctx.send(f"{player.name} jumped (remaining jumps: {p_jumps}).\n"
                               f"{opponent.name} jumped (remaining jumps: {o_jumps}).")

            # update stocks if hp <= 0
            if p_brawler.update_stocks():
                await ctx.send(f"{player.name}'s {p_brawler.skin} "
                               f"{p_brawler.name} lost a stock!")
            if o_brawler.update_stocks():
                await ctx.send(f"{opponent.name}'s {o_brawler.skin} "
                               f"{o_brawler.name} lost a stock!")

        if p_brawler.stocks > 0 and o_brawler.stocks == 0:
            embed = get_game_over_embed(player, p_brawler.key, opponent, o_brawler.key)
            await ctx.send(embed=embed)
        elif p_brawler.stocks == 0 and o_brawler.stocks > 0:
            embed = get_game_over_embed(opponent, o_brawler.key, player, p_brawler.key)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=get_brawl_embed())
            await ctx.send("DRAW!")

        remove_status(player, opponent)

    # @b.command()
    # async def test(self, ctx):
    #     '''
    #     test
    #     '''
    #     conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    #     c = conn.cursor()
    #     await ctx.send("Fetching all data")
    #     c.execute("""SELECT name, key FROM legends; """)
    #     lst_rows = c.fetchall()
    #     await ctx.send("Fetched all data")
    #     counter = 0
    #     await ctx.send("Starting loop")
    #     for row in lst_rows:
    #         name = row[0]
    #         key = row[1]
    #         print(name)
    #         print(key)
    #         counter += 1
    #         if counter % 500 == 0:
    #             await ctx.send("500 rows scanned")
    #     print(counter)
    #     conn.commit()
    #     conn.close()
    #     await ctx.send("done")

    # @b.command(hidden=False)
    # async def test(self, ctx):
    #     '''
    #     test
    #     Iterate through files in s3 bucket and execute operations.
    #     '''
    #     import boto3
    #     if await self.bot.is_owner(ctx.message.author):
    #         conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    #         c = conn.cursor()
    #         legends_lst = ['ada', 'artemis', 'asuri', 'azoth', 'barraza', 'bodvar', 'brynn', 'caspian', 'cassidy', 'cross', 'diana', 'ember', 'gnash', 'hattori', 'jhala', 'kaya', 'koji', 'kor', 'lordvraxx', 'lucien', 'mirage', 'mordex', 'nix', 'orion', 'queennai', 'ragnir', 'scarlet', 'sentinel', 'sidra', 'sirroland', 'teros', 'thatch', 'ulgrim', 'val', 'wushang', 'xull', 'yumiko']
    #         s3 = boto3.client('s3')
    #         # lst_of_dicts_to_delete = []
    #         # lst_of_keys_replace = []
    #         counter = 0
    #         for legend in legends_lst:
    #             obj_dict = s3.list_objects_v2(Bucket='willabot-assets', Prefix=f'images/legends/{legend}')
    #             for obj in obj_dict['Contents']:
    #                 # inserting legends into database
    #                 print(obj['Key'])
    #                 key = obj['Key']
    #                 string = key.replace('.png', '')
    #                 lst = string.split("_")
                    # make sure to get rid of the directory route
    #                 legend = lst[0]
    #                 skin = lst[1]
    #                 color = lst[2]
    #                 c.execute(""" INSERT INTO legends (key, name, skin, color)
    #                                 VALUES (%s, %s, %s, %s);""", (key, legend, skin, color))

    #                 # finding files to delete
    #                 # if '_community.png' in obj['Key'] or '_holiday.png' in obj['Key']:
    #                 #     print(obj['Key'])
    #                 #     dict_of_key_to_delete = {}
    #                 #     dict_of_key_to_delete['Key'] = obj['Key']
    #                 #     lst_of_dicts_to_delete.append(dict_of_key_to_delete)
    #                 # if '_communitycolor(cc).png' in obj['Key'] or '_winterholiday.png' in obj['Key']:
    #                 #     print(obj['Key'])
    #                 #     lst_of_keys_replace.append(obj['Key'])
    #             list_length = str(len(obj_dict['Contents']))
    #             await ctx.send(f"Finished iterating through {list_length} files for {legend}")
    #         await ctx.send("Done iterating through all files.")
    #         # await ctx.send(f"Found {len(lst_of_dicts_to_delete)} files to delete.")
    #         # await ctx.send(f"{len(lst_of_keys_replace)} files replaced.")
    #         # response = s3.delete_objects(Bucket='willabot-assets', Delete={'Objects':lst_of_dicts_to_delete})
    #         # await ctx.send(f"Deleted {len(response['Deleted'])} files.")
    #         conn.commit()
    #         conn.close()
    #     else:
    #         await ctx.send("This command is not available for noobs!")


def setup(bot):
    bot.add_cog(Brawlhalla(bot))