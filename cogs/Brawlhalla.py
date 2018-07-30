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

    @b.command()
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
        if skin is not None:
            skin = format(skin)
        else:
            skin = 'base'
        if color is not None:
            color = format(color)
        else:
            color = 'Classic_Colors'
        img_url_lst = [legend, skin, color]
        img_url = '_'.join(img_url_lst)
        print(img_url)
        embed = discord.Embed()
        embed.set_image(url="https://s3.amazonaws.com/willabot-assets/images/legends/" + img_url + ".png")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Brawlhalla(bot))