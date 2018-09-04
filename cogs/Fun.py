import discord
from discord.ext import commands
import os
import requests

DATABASE_URL = os.environ['DATABASE_URL']
mashape_key = os.environ['mashape_key']
weather_key = os.environ['weather_key']


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
        # quick fix for weird character error from website
        joke = joke.replace("â", "'")
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

    @commands.cooldown(rate=10, per=60, type=commands.BucketType.user)
    @commands.command()
    async def weather(self, ctx, *, city: str=None):
        '''
        Gets the weather forecast for a city.
        w.weather <city>

        If you wish to specify the country, add the 2-letter country code after the city.
        eg) "w.weather Seoul, KR"
        '''
        if city is None:
            await ctx.send("You must specify a city!")
            return

        try:
            response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={weather_key}&units=metric").json()
            main = response['weather'][0]['main']
            description = response['weather'][0]['description']
            weather_icon_code = response['weather'][0]['icon']
            weather_icon_url = f"http://openweathermap.org/img/w/{weather_icon_code}.png"
            temp = response['main']['temp']
            humidity = response['main']['humidity']
            temp_min = response['main']['temp_min']
            temp_max = response['main']['temp_max']
            country = response['sys']['country']
            city = response['name']
        except:
            await ctx.send("City not found.")
            return

        embed = discord.Embed(title=f"Weather Forecast for {city}, {country}", description=f"**{main}**\n{description}", color=0x48d1cc)
        embed.set_thumbnail(url=weather_icon_url)
        embed.add_field(name="Temperature (°C)", value=f"{temp} ({temp_min} - {temp_max})")
        embed.add_field(name="Humidity", value=humidity)
        await ctx.send(embed=embed)

    @weather.error
    async def weather_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            error_msg = str(error)
            T_ind = error_msg.find("T")
            error_msg = error_msg[T_ind:]
            user = ctx.message.author
            await ctx.send("Slow down " + user.mention + "! The command is on cooldown! " + error_msg + ".")
        else:
            await ctx.send("Unknown error. Please tell Willa.")
            print(error)


def setup(bot):
    bot.add_cog(Fun(bot))