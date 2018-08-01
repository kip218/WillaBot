import discord
from discord.ext import commands
import psycopg2
import os

DATABASE_URL = os.environ['DATABASE_URL']


class Brawlhalla:
    '''
    Commands for the to-do list.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def b(self, ctx):
        '''
        Brawlhalla commands
        w.b
        '''

    @b.command(usage="<legend> / [skin] / [color]")
    async def info(self, ctx, *, msg: str=None):
        '''
        Gives info of a Brawlhalla legend, skin, color.
        w.b info
        Leave [skin]/[color] empty to get the default skin/color.
        For example:
        - "w.b info ada" gives default skin default color ada
        - "w.b info ada//black" gives default skin black ada
        - "w.b info ada/atlantean" gives default color atlantean ada
        '''
        # clean user input
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

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute("""SELECT key FROM legends
                        WHERE name LIKE '%%'||%s||'%%'
                            AND skin LIKE '%%'||%s||'%%'
                            AND color LIKE '%%'||%s||'%%'; """, (legend_name, skin, color))
        row = c.fetchone()
        if row is not None:
            full_key = row[0]
            embed = discord.Embed()
            embed.set_image(url="https://s3.amazonaws.com/willabot-assets/" + full_key)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Legend/skin/color not found!")
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