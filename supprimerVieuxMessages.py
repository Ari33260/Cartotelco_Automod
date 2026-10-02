from dotenv import load_dotenv
import asyncio
from datetime import datetime, timezone, timedelta
import discord
from discord.ext import commands
from dotenv import load_dotenv

# VARIABLES GLOBALES (PARAMETRES)
LISTES_SALONS = ("1429394357466697899","1429394838683390033","1012750995371065354","1176096736410869840","1429399097210703984","1367608197040570518",
                 "1012741568031100931","1012782593307070554","1301996850647400448","1278432821140258827","1207394338124865587","1298716918567665765",
                 )
USER_ID = "376068947835092992"


print("Initialisation en cours ...")
load_dotenv()
TOKEN = os.getenv('TOKEN')
print(".env chargé : OK !")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def send_log(thread: discord.Thread, tag: str, msg: str):
    now = datetime.now().strftime("%H:%M:%S")
    formatted = f"`[{now}]` `[{tag.upper()}]` {msg}"
    print(f"[{now}] [{tag.upper()}] {msg}")
    
    try:
        # Tronquage de sécurité si un message brut dépasse la limite Discord
        if len(formatted) > 1950:
            formatted = formatted[:1940] + "...`"
        await thread.send(formatted)
    except Exception as e:
        print(f"Erreur d'envoi dans le thread : {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def purger_cible(ctx):
    target_user_id = int(USER_ID)
    total_supprimes = 0
    total_salons = len(LISTES_SALONS)

    # Création du thread rattaché au message de commande
    thread = await ctx.message.create_thread(
        name=f"log-purge-{USER_ID[-4:]}-{datetime.now().strftime('%H%M%S')}",
        auto_archive_duration=60
    )

    await send_log(thread, "INFO", f"Commande lancée par {ctx.author.name} (ID: {ctx.author.id})")
    await send_log(thread, "INFO", f"Cible : `{target_user_id}` | Salons à scanner : {total_salons}")

    for index, salon_str_id in enumerate(LISTES_SALONS, start=1):
        channel_id = int(salon_str_id)
        await send_log(thread, "SALON", f"[{index}/{total_salons}] Résolution ID : `{channel_id}`...")

        channel = bot.get_channel(channel_id)
        if channel is None:
            try:
                channel = await bot.fetch_channel(channel_id)
                await send_log(thread, "SALON", f"Récupéré via API : `#{channel.name}`")
            except discord.NotFound:
                await send_log(thread, "ERREUR", f"Salon `{channel_id}` introuvable. Ignoré.")
                continue
            except discord.Forbidden:
                await send_log(thread, "ERREUR", f"Accès interdit au salon `{channel_id}`.")
                continue
            except Exception as e:
                await send_log(thread, "ERREUR", f"Erreur salon `{channel_id}` : {e}")
                continue

        if not isinstance(channel, discord.TextChannel):
            await send_log(thread, "SKIP", f"`#{channel.name}` n'est pas un salon textuel standard.")
            continue

        await send_log(thread, "SCAN", f"Lecture de l'historique dans `#{channel.name}`...")
        count_salon = 0
        messages_scannes = 0

        try:
            async for message in channel.history(limit=None):
                messages_scannes += 1
                
                # Signalement tous les 200 messages scannés
                if messages_scannes % 200 == 0:
                    await send_log(thread, "PROGRES", f"`#{channel.name}` : {messages_scannes} messages analysés...")

                if message.author.id == target_user_id:
                    apercu = message.clean_content.replace("\n", " ")[:30]
                    date_msg = message.created_at.strftime("%d/%m/%Y %H:%M")
                    
                    try:
                        await message.delete()
                        count_salon += 1
                        total_supprimes += 1
                        await send_log(thread, "SUPPR", f"Msg `{message.id}` ({date_msg}) supprimé : *\"{apercu}...\"*")
                        await asyncio.sleep(1.2)
                    except discord.Forbidden:
                        await send_log(thread, "ERREUR", f"Manque permission 'Gérer les messages' dans `#{channel.name}`.")
                        break
                    except discord.NotFound:
                        await send_log(thread, "WARN", f"Message `{message.id}` déjà introuvable.")
                    except discord.HTTPException as e:
                        if e.status == 429:
                            retry_after = getattr(e, "retry_after", 5)
                            await send_log(thread, "RATE-LIMIT", f"Discord 429 reçu. Pause de {retry_after}s...")
                            await asyncio.sleep(retry_after)
                        else:
                            await send_log(thread, "ERREUR", f"Erreur HTTP {e.status} : {e.text}")

        except discord.Forbidden:
            await send_log(thread, "ERREUR", f"Accès refusé à l'historique de `#{channel.name}`.")
            continue

        await send_log(thread, "FIN-SALON", f"`#{channel.name}` terminé : {count_salon} supprimé(s) / {messages_scannes} scannés.")

    await send_log(thread, "TERMINE", f"**Nettoyage complet.** Total supprimé : **{total_supprimes}** messages.")
@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')

bot.run(TOKEN)


class MaClasse():
    def __init__(self, valeur1, valeur2):
        self.valeur1 = valeur1
        self.valeur2 = valeur2
        
    def MaFonctionMaClasse():
        #Je veux appeler ici la fonction "FonctionMain"
        FonctionMain(valeur1,valeur2)
        
def FonctionMain(valeur1,valeur2):
    #Instruction
    return 0
    
