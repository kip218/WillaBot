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

    @b.command(usage="<legend>, [skin], [color]")
    async def info(self, ctx, *, msg):
        '''
        Gives info of a Brawlhalla legend, skin, color.
        w.b info
        '''
        msg_lst = msg.split(',')
        legend = msg_lst[0]
        try:
            skin = msg_lst[1]
        except IndexError:
            skin = 'base'
        try:
            color = msg_lst[2]
        except IndexError:
            color = 'classic'

        img_key_lst = [legend, skin, color]
        img_key_lst_clean = []
        for value in img_key_lst:
            value = value.replace(' ', '')
            value = value.replace('\'', '')
            value = value.replace('-', '')
            value = value.replace('_', '')
            img_key_lst_clean.append(value)
        img_key = '_'.join(img_key_lst_clean)

        embed = discord.Embed()
        embed.set_image(url="https://s3.amazonaws.com/willabot-assets/images/legends/" + img_key + ".png")
        await ctx.send(embed=embed)

    # @b.command(hidden=False)
    # async def test(self, ctx):
    #     '''
    #     test
    #     '''
    #     if await self.bot.is_owner(ctx.message.author):
    #         legends_lst = ['ada', 'artemis', 'asuri', 'azoth', 'barraza', 'brynn', 'caspian', 'cassidy', 'cross', 'diana', 'ember', 'gnash', 'hattori', 'jhala', 'kaya', 'koji', 'kor', 'lord_vraxx', 'lucien', 'mirage', 'mordex', 'nix', 'orion', 'queen_nai', 'ragnir', 'scarlet', 'sentinel', 'sidra', 'sir_roland', 'teros', 'thatch', 'ulgrim', 'val', 'wu_shang', 'xull', 'yumiko']
    #         s3 = boto3.client('s3')
    #         for legend in legends_lst:
    #             # remove this after s3 update
    #             legend = legend.upper()
    #             obj_dict = s3.list_objects_v2(Bucket='willabot-assets', Prefix=f'images/legends/{legend}')
    #             for obj in obj_dict['Contents']:
    #                 print(obj['Key'])
    #             list_length = str(len(obj_dict['Contents']))
    #             await ctx.send(f"Finished iterating through {list_length} files for {legend}")
    #         await ctx.send("DONE")
    #     else:
    #         await ctx.send("This command is not available for noobs!")


def setup(bot):
    bot.add_cog(Brawlhalla(bot))