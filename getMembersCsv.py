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

print("ça fonctionner !")

print("On récupère client.get_all_members()")
data = client.get_all_members()

print(f"Le type de data est {type(data)}")

client.run(TOKEN)
