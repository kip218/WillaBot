import discord
from discord.ext import commands
import psycopg2
import os
import boto3

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

    @b.command(usage="b info <legend>, [skin], [color]")
    async def info(self, ctx, legend, skin: str=None, color: str=None):
        '''
        Gives info of a Brawlhalla legend, skin, color.
        w.b info
        '''
        def format(string):
            string_lst = string.split("-")
            for substring_index in range(len(string_lst)):
                substring = string_lst[substring_index]
                substring = substring[0].upper() + substring[1:].lower()
                string_lst[substring_index] = substring
            res = "_".join(string_lst)
            return res

        legend = legend.upper().replace('-', '_')
        if skin is None or skin == "base":
            skin = 'base'
        else:
            skin = format(skin)
        if color is None or color == "Classic_Colors":
            color = 'Classic_Colors'
        else:
            color = format(color)
        img_url_lst = [legend, skin, color]
        img_url = '_'.join(img_url_lst)
        print(img_url)
        embed = discord.Embed()
        embed.set_image(url="https://s3.amazonaws.com/willabot-assets/images/legends/" + img_url + ".png")
        await ctx.send(embed=embed)

    @b.command()
    async def test(self, ctx):
        '''
        test
        '''
        if await self.bot.is_owner(ctx.message.author):
            legends_lst = ['ada', 'artemis', 'asuri', 'azoth', 'barraza', 'brynn', 'caspian', 'cassidy', 'cross', 'diana', 'ember', 'gnash', 'hattori', 'jhala', 'kaya', 'koji', 'kor', 'lord_vraxx', 'lucien', 'mirage', 'mordex', 'nix', 'orion', 'queen_nai', 'ragnir', 'scarlet', 'sentinel', 'sidra', 'sir_roland', 'teros', 'thatch', 'ulgrim', 'val', 'wu_shang', 'xull', 'yumiko']
            s3 = boto3.client('s3')
            for legend in legends_lst:
                # remove this after s3 update
                legend = legend.upper()
                obj_dict = s3.list_objects_v2(Bucket='willabot-assets', Prefix=f'images/legends/{legend}')
                for obj in obj_dict['Contents']:
                    print(obj['Key'])
                list_length = str(len(obj_dict['Contents']))
                await ctx.send(f"Finished iterating through {list_length} files for {legend}")
            await ctx.send("DONE")
        else:
            await ctx.send("This command is not available for noobs!")


def setup(bot):
    bot.add_cog(Brawlhalla(bot))