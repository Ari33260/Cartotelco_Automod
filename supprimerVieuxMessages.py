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

@bot.command()
@commands.has_permissions(administrator=True)
async def purger_cible(ctx):
    target_user_id = int(USER_ID)
    total_supprimes = 0

    await ctx.send(f"Démarrage du nettoyage pour l'utilisateur `{USER_ID}`...")

    for salon_str_id in LISTES_SALONS:
        channel_id = int(salon_str_id)
        channel = bot.get_channel(channel_id)

        # Si le salon n'est pas dans le cache, on tente un appel API
        if channel is None:
            try:
                channel = await bot.fetch_channel(channel_id)
            except (discord.NotFound, discord.Forbidden):
                print(f"[!] Salon inaccessible ou introuvable : {channel_id}")
                continue

        if not isinstance(channel, discord.TextChannel):
            continue

        print(f"Scan en cours dans : #{channel.name} ({channel.id})")
        count_salon = 0

        try:
            # limit=None scanne l'intégralité de l'historique du salon
            async for message in channel.history(limit=None):
                if message.author.id == target_user_id:
                    try:
                        await message.delete()
                        count_salon += 1
                        total_supprimes += 1
                        # Pause indispensable pour ne pas déclencher les rate limits
                        await asyncio.sleep(1.2)
                    except discord.Forbidden:
                        print(f"[!] Permissions insuffisantes pour supprimer dans #{channel.name}")
                        break
                    except discord.HTTPException as e:
                        # Gestion en cas de rate limit temporaire imposé par Discord
                        if e.status == 429:
                            retry_after = getattr(e, 'retry_after', 5)
                            print(f"[!] Rate limit atteint. Pause de {retry_after}s...")
                            await asyncio.sleep(retry_after)
        except discord.Forbidden:
            print(f"[!] Accès refusé à l'historique de #{channel.name}")
            continue

        print(f"Terminé pour #{channel.name} : {count_salon} message(s) supprimé(s).")

    await ctx.send(f"Nettoyage achevé. Total de messages supprimés : **{total_supprimes}**.")

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
    
