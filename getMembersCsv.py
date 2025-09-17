import discord
import os
from dotenv import load_dotenv
from datetime import datetime


print("Initialisation en cours ...")
load_dotenv()
TOKEN = os.getenv('TOKEN')
print(".env chargé : OK !")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')
    
    for guild in client.guilds:
        for member in guild.members:
            print(f"{member}")
        
client.run(TOKEN)

