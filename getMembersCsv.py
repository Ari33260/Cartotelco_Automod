import discord
import os
import csv
from dotenv import load_dotenv
from datetime import datetime


print("Initialisation en cours ...")
load_dotenv()
TOKEN = os.getenv('TOKEN')
print(".env chargé : OK !")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)

CHANNEL_IDS = [
    1012741568031100931, # general
    1012782593307070554, # bistro
    1012751244554678382, # discu telco
    1012750995371065354, # speedtest
    1176096736410869840, # photos infra 
    
]

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')
    
    for guild in client.guilds:
        print(f"Traitement de la guilde : {guild.name} ({guild.id})")

        # Dictionnaire pour stocker les infos
        data = {}

        for member in guild.members:
            key = f"{member.id}_{member.name}"
            data[key] = {
                "id": member.id,
                "name": member.name,
                "nick": member.nick,
                "joined_at": member.joined_at.isoformat() if member.joined_at else None,
                "system": member.system,
                "message_count": 0,
                "last_message": None,
            }

        # Scan uniquement des salons spécifiés
        for channel_id in CHANNEL_IDS:
            channel = guild.get_channel(channel_id)
            if channel is None:
                print(f"⚠️ Salon {channel_id} introuvable dans {guild.name}")
                continue

            print(f"🔎 Scan du salon : {channel.name}")
            try:
                async for message in channel.history(limit=1000):  # limite ajustable
                    if message.author.bot:
                        continue
                    key = f"{message.author.id}_{message.author.name}"
                    if key in data:
                        data[key]["message_count"] += 1
                        if (data[key]["last_message"] is None or
                            message.created_at > data[key]["last_message"]):
                            data[key]["last_message"] = message.created_at
            except discord.Forbidden:
                print(f"⛔ Pas d’accès à {channel.name}")
            except discord.HTTPException as e:
                print(f"⚠️ Erreur HTTP sur {channel.name}: {e}")

        # Écriture CSV
        filename = f"{guild.name}_members.csv"
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["key", "id", "pseudo original", "pseudo serveur", "arrivé le", "client officiel", "nombre de message", "dernier message le"]
            )
            writer.writeheader()
            for key, info in data.items():
                writer.writerow({
                    "key": key,
                    "id": info["id"],
                    "name": info["name"],
                    "nick": info["nick"],
                    "joined_at": info["joined_at"],
                    "system": info["system"],
                    "message_count": info["message_count"],
                    "last_message": info["last_message"].isoformat() if info["last_message"] else None,
                })

        print(f"📂 Données enregistrées dans {filename}")

    await client.close()


        
client.run(TOKEN)

