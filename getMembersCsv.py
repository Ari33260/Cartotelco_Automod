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
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')
    
    for guild in client.guilds:
        print(f"Traitement de la guilde : {guild.name} ({guild.id})")

        # Dictionnaire pour stocker les infos des membres
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

        # Parcours de l’historique des salons texte
        for channel in guild.text_channels:
            try:
                async for message in channel.history(limit=1000):  # limite = nombre de messages à remonter
                    if message.author.bot:
                        continue
                    key = f"{message.author.id}_{message.author.name}"
                    if key in data:
                        data[key]["message_count"] += 1
                        if (data[key]["last_message"] is None or
                            message.created_at > data[key]["last_message"]):
                            data[key]["last_message"] = message.created_at
            except discord.Forbidden:
                print(f"⛔ Impossible d’accéder à {channel.name}")
            except discord.HTTPException as e:
                print(f"⚠️ Erreur HTTP sur {channel.name}: {e}")

        # Écriture dans un CSV
        filename = f"{guild.name}_members.csv"
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["key", "id", "name", "nick", "joined_at", "system", "message_count", "last_message"]
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

    await client.close()  # ferme le bot après export

        
client.run(TOKEN)

