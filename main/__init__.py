import settings, discord
from discord.ext import commands

activity = discord.Activity(type=discord.ActivityType.watching, name=".gg/g2rGrm8Y8U | made by sheepie0")
bot = commands.Bot(command_prefix=settings.PREFIX, intents=settings.INTENTS, activity=activity)
