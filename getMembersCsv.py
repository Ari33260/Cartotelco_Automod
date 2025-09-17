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

for member in client.get_all_members():
    print(f"Le type est : {type(member)}")
    print(f"Data : {member}")

client.run(TOKEN)
