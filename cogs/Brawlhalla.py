import discord
from discord.ext import commands
import psycopg2
import os

DATABASE_URL = os.environ['DATABASE_URL']


class Brawlhalla:
    '''
    Commands for Brawlhalla.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def b(self, ctx):
        '''
        Brawlhalla commands.
        w.b
        '''

    @b.command(usage="[legend] / [skin] / [color]")
    async def info(self, ctx, *, msg: str=None):
        '''
        Your selected legend. Gives info of a Brawlhalla legend/skin/color if specified.
        w.b info

        Leave [skin]/[color] empty to get the default skin/color.
        For example:
        - "w.b info ada" gives default skin default color ada
        - "w.b info ada//black" gives default skin black ada
        - "w.b info ada/atlantean" gives default color atlantean ada
        '''
        if msg is None:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            c = conn.cursor()
            c.execute("""SELECT selected_legend FROM users
                            WHERE ID = %s """, (str(ctx.author.id),))
            selected_legend = c.fetchone()[0]
            # return if user hasn't selected a legend
            if selected_legend is None:
                await ctx.send("You have not selected a legend yet! Use \"w.b legends\" to see your legends.")
                conn.close()
                return
            key = selected_legend[0]
            legend_name = selected_legend[1][0].upper() + selected_legend[1][1:]
            skin = selected_legend[2][0].upper() + selected_legend[2][1:]
            color = selected_legend[3][0].upper() + selected_legend[3][1:]
            stance_num = int(selected_legend[4])
            level = selected_legend[5]
            stance_lst = ['Default', 'Strength', 'Dexterity', 'Defense', 'Speed']
            c.execute("""SELECT stance_stats, weapons FROM legends
                            WHERE key = %s; """, (key,))
            row = c.fetchone()
            stats_lst = row[0][stance_num]
            weapons = row[1]
            embed = discord.Embed(color=0x36393E)
            embed.add_field(name=f"{stance_lst[stance_num]} Stance", value=f"**Str:** {stats_lst[0]}\n**Dex:** {stats_lst[1]}\n**Def:** {stats_lst[2]}\n**Spd:** {stats_lst[3]}", inline=True)
            embed.add_field(name="Weapons", value=f"{weapons[0]}\n{weapons[1]}", inline=True)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_author(name=f"{ctx.author.name}'s Level {level} {skin} {legend_name}", icon_url=ctx.author.avatar_url)
            # embed.set_image(url=f"https://s3.amazonaws.com/willabot-assets/{key}")
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

        row = c.fetchone()

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
            name = row[1][0].upper() + row[1][1:]
            skin = row[2][0].upper() + row[2][1:]
            color = row[3][0].upper() + row[3][1:]
            embed = discord.Embed(title=f"{skin} {name} *({color})*", color=0x36393E)
            embed.set_image(url="https://s3.amazonaws.com/willabot-assets/" + full_key)
            # setting up stats and weapons
            default_stats = row[4][0]
            weapons = row[5]
            embed.add_field(name="Stats", value=f"**Str:** {default_stats[0]}\n**Dex:** {default_stats[1]}\n**Def:** {default_stats[2]}\n**Spd:** {default_stats[3]}", inline=True)
            embed.add_field(name="Weapons", value=f"{weapons[0]}\n{weapons[1]}", inline=True)
            return embed

        clean_input = clean_input(msg)
        if clean_input is not None:
            legend_name, skin, color = clean_input(msg)
        else:
            return

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
            await ctx.send("Legend/skin/color not found! Use \"w.b list [legend] [skin]\" to see a list of available legends/skins/colors!")
        conn.close()

    @b.command(usage="[legend] / [skin]")
    async def list(self, ctx, *, msg: str=None):
        '''
        Lists all available legends in the database. Specify [legend] to view all available skins for that legend. Specify [skin] to view all available colors for that skin.
        w.b list [legend] / [skin]

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
                legends_lst.append(legend)
            embed = discord.Embed(title="List of legends", description=', '.join(legends_lst), color=0x36393E)
            embed.set_footer(text="Isaiah, Jiro, Lin fei, and Zariel are currently unavailable.")
            await ctx.send(embed=embed)
        elif skin_input is None:
            # find legend matching input
            c.execute(""" SELECT DISTINCT name FROM legends
                            WHERE name LIKE '%%'||%s||'%%'; """, (legend_input,))
            row = c.fetchone()
            if row is None:
                await ctx.send("Could not find legend. Try \"w.b list\" to see the list of legends available.")
                return
            legend_name = row[0]
            # get list of skins
            c.execute(""" SELECT DISTINCT skin FROM legends
                            WHERE name = %s; """, (legend_name,))
            rows = c.fetchall()
            skins_lst = []
            for row in rows:
                skin = row[0][0].upper() + row[0][1:]
                skins_lst.append(skin)
            embed = discord.Embed(title=f"List of {legend_name} skins", description=', '.join(skins_lst), color=0x36393E)
            embed.set_footer(text="Some skins may be unavailable.")
            await ctx.send(embed=embed)
        else:
            # find legend matching input
            c.execute(""" SELECT DISTINCT name FROM legends
                            WHERE name LIKE '%%'||%s||'%%'; """, (legend_input,))
            row = c.fetchone()
            if row is None:
                await ctx.send("Could not find legend. Try \"w.b list\" to see the list of legends available.")
                return
            legend_name = row[0]
            # find skin matching input
            c.execute(""" SELECT DISTINCT skin FROM legends
                            WHERE name = %s
                            AND skin LIKE '%%'||%s||'%%'; """, (legend_name, skin_input))
            row = c.fetchone()
            if row is None:
                if row is None:
                    await ctx.send("Could not find skin. Try \"w.b list [legend]\" to see the list of skins available for that legend.")
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
                colors_lst.append(color)
            embed = discord.Embed(title=f"List of available colors for {skin_name} {legend_name}", description=', '.join(colors_lst), color=0x36393E)
            embed.set_footer(text="Some colors may be unavailable.")
            await ctx.send(embed=embed)
        conn.close()

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