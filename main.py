import os
import discord
from discord.ext import commands
from music import Music
from stayonline import stayonline

my_secret = os.environ['token']

cogs = [Music]

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.typing = True
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

for cog in cogs:
  cog.setup(client)
  
stayonline()

client.run(my_secret)