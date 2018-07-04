import discord
import discord.ext.commands as commands
import pyowm
from pyowm.exceptions.not_found_error import NotFoundError as pyowmNFE

import asyncio
import textwrap as tw

from .template import PluginClass


class Weather(PluginClass):
    CONFIG_REQUIRED = True
    STORAGE_REQUIRED = True

    def __init__(self, config, storage):
        self.config = config
        self.storage = storage
        self.owm = pyowm.OWM(config['API_KEY'])

    def __unload(self):
        pass #TODO: once framework has storage saving, implement storage output
             # otherwise storage allows for persistent use of plugin data across
             # relods of the plugin

    def help(self):
        result = f'''
                ```
                {type(self).__name__}
                this plugin retrieves weather in specific areas if no arguments
                are given then it will use the user's saved location.
                - .weather <city> <state/country>
                fetches weather in the specified area
                - .w
                fetches user's set location's weather
                - .wset <city> <state/country>
                allows the user to set their location
                ```
                '''

        return tw.dedent(result)

    @commands.command()
    async def weather(self, ctx, city: str, state: str):
        """gets the weather for a specific area"""
        await ctx.send(self.getWeather(city, state))

    @commands.command()
    async def w(self, ctx):
        """gets the default weather location for the user; if none is set it will reply as such"""
        try:
            userWeatherLoc = self.storage[ctx.message.author]
        except:
            await ctx.send('user has not registered a default location')
            return

        await ctx.send(self.getWeather(userWeatherLoc[0], userWeatherLoc[1]))

    @commands.command()
    async def wset(self, ctx, city: str, state: str):
        """lets a user set their weather default location"""

        userWeatherLoc = [city, state]
        temp = {ctx.message.author : userWeatherLoc}
        self.storage.update(temp)

        await ctx.send('your weather location has been registered')

    @commands.command()
    async def weather_help(self, ctx):
        await ctx.send(self.help())

    def getWeather(self, city, state):
        try:
            obs = self.owm.weather_at_place(f'{city},{state}')
        except pyowmNFE:
            # the format requires a country code (i.e. US)
            # assume US because i'm a filthy american
            obs = self.owm.weather_at_place(f'{city},{state},US')

        #the format requires a country code (i.e. US)
        weather = obs.get_weather()
        wind = weather.get_wind()['speed']
        humidity = weather.get_humidity()
        temperature = weather.get_temperature('fahrenheit')['temp']
        reply = str(wind)

        result = f'''
                  ```
                  It is currently {temperature}F degrees in {city}, {state}.
                  The wind speed of {wind} mph with a humidity of {humidity}%.
                  ```
                  '''

        return tw.dedent(result)
