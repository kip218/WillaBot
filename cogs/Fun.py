from discord.ext import commands
import os
import requests

DATABASE_URL = os.environ['DATABASE_URL']
mashape_key = os.environ['mashape_key']


class Fun:
    '''
    Commands for fun.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def joke(self, ctx):
        '''
        Tells a joke.
        w.joke
        '''
        headers = {'Accept': 'text/plain'}
        joke = requests.get('https://icanhazdadjoke.com/', headers=headers).text
        await ctx.send(joke)

    @commands.command()
    async def quote(self, ctx):
        '''
        Random quote.
        w.quote
        '''
        headers = {
                "X-Mashape-Key": mashape_key,
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
                }
        response = requests.get("https://andruxnet-random-famous-quotes.p.mashape.com/?count=1", headers=headers).json()[0]
        quote = response['quote']
        author = response['author']
        await ctx.send(f"*\"{quote}\"*\n- {author}")


def setup(bot):
    bot.add_cog(Fun(bot))