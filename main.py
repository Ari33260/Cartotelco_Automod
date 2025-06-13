import discord
from discord.ext import commands
import re
import os
from dotenv import load_dotenv
from datetime import datetime
import subprocess
import random
import requests
import aiohttp
import urllib3
from bs4 import BeautifulSoup

# Eviter les warning
urllib3.disable_warnings()

# VARIABLES GLOBALES (PARAMETRES)
ID_CANAL_AUTOSIGNALEMENT = 1223257795571351572
ID_CANAL_LOG = 1012816121574998026
SALON_SUIVI_MESSAGES = 1223280408939073536
SALON_PARTAGE_ACTU = 1298716918567665765
RolesByPass = [1012814021344374948,1012813457734770799]
Listes_mots = {}

print("Initialisation en cours ...")
load_dotenv()
TOKEN = os.getenv('TOKEN')
print(".env chargé : OK !")

print(f"Salon défini pour le suivi des messages : OK ! (ID : {SALON_SUIVI_MESSAGES}.") if SALON_SUIVI_MESSAGES is not None else print(f"Salon défini pour le suivi des messages : NOK !\nVeuillez définir un ID de salon dans le fichier main.py à la variable globale : SALON_SUIVI_MESSAGES")
print("\nChargement des dictionnaires...")
# Liste des mots interdits pour la catégorie insulte 
with open("AutoSignalement/dictionnaire_insultes.txt", "r") as fichier:
    contenu_fichier_insultes = fichier.read()
    Listes_mots['insultes'] = contenu_fichier_insultes.split('\n')
    #supprime les éléments vides
    Listes_mots['insultes'] = list(filter(len, Listes_mots['insultes']))
print("Catégorie Insultes : OK !\nElements chargés : ",len(Listes_mots['insultes']))

# Liste des mots interdits pour la catégorie politique 
with open("AutoSignalement/dictionnaire_politique.txt", "r") as fichier:
    contenu_fichier_politique = fichier.read()
    Listes_mots['politique'] = contenu_fichier_politique.split('\n')
    #supprime les éléments vides
    Listes_mots['politique'] = list(filter(len, Listes_mots['politique']))
print("Catégorie politique : OK !\nElements chargés : ",len(Listes_mots['politique']))

print("\nChargement des salons à exclure...")
with open("AutoSignalement/except_salons_insultes.txt", "r") as fichier:
    contenu_salons_insultes = fichier.read()
    #nf = non formaté
    liste_salons_insultes_nf = contenu_salons_insultes.split('\n')
    #supprime les éléments vides
    liste_salons_insultes_nf = list(filter(len, liste_salons_insultes_nf))
    liste_salons_insultes = []
    for e in liste_salons_insultes_nf:
        salon_insultes_nf = e.split(":")
        salon_insultes = salon_insultes_nf[1] 
        liste_salons_insultes.append(salon_insultes)
        
print("Catégortie Insultes : OK !\nElements chargés : ",len(liste_salons_insultes))

with open("AutoSignalement/except_salons_politique.txt", "r") as fichier:
    contenu_salons_politique = fichier.read()
    liste_salons_politique_nf = contenu_salons_politique.split('\n')
    #supprime les éléments vides
    liste_salons_politique_nf = list(filter(len, liste_salons_politique_nf))
    liste_salons_politique = []
    for e in liste_salons_politique_nf:
        salon_politique_nf = e.split(":")
        salon_politique = salon_politique_nf[1] 
        liste_salons_politique.append(salon_politique)

        
print("Catégortie politique : OK !\nElements chargés : ",len(liste_salons_politique))

print(f"\nSalon de référence pour l'Autosignalement : OK ! (ID : {ID_CANAL_AUTOSIGNALEMENT})") if ID_CANAL_AUTOSIGNALEMENT is not None else print(f"Salon de référence pour l'Autosignalement : NOK !\nVeuillez définir un ID de salon dans le fichier main.py à la variable globale : ID_CANAL_AUTOSIGNALEMENT")

motif_regex = {}
motif_regex['insultes'] = re.compile(r'\b(?:' + '|'.join(map(re.escape, Listes_mots['insultes'])) + r')\b')
print("\nCompilation des motifs regex pour la catégorie insultes : OK !")

motif_regex['politique'] = re.compile(r'\b(?:' + '|'.join(map(re.escape, Listes_mots['politique'])) + r')\b')
print("Compilation des motifs regex pour la catégorie politique : OK !")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# arg1 = mot à supprimer du dictionnaire
# arg2 = catégorie
@bot.command()
async def addwl(ctx, arg1, arg2):
    commande =  f"sed -i '/^{arg1}$/d' AutoSignalement/dictionnaire_{arg2.lower()}.txt"
    print(f"Commande exécutée : {commande}")
    resultat = subprocess.run(commande, shell=True, capture_output=True, text=True)
    print(f"Retour console : {resultat.stdout}")
    await ctx.send(f"Mise à jour du dictionnaire...")
    await MajListe(ctx,arg2.lower())

# arg = mots (si plusieurs alors ils sont séparés par une virgule.)
# arg-1 = catégorie
@bot.command()
async def addbl(ctx, *args):
    print(args)
    if len(args) > 1:
        categorie = args[-1].lower()
        # Permet de récupérer l'ensemble des mots même des expressions.
        mots_nf = []
        for argument in range(len(args)-1):
            mots_nf.append(args[argument])
        mots_nf = ' '.join(mots_nf)
        # Transforme la variable mots_nf en liste car args est un tuple.
        file_path = f"AutoSignalement/dictionnaire_{categorie.lower()}.txt"
        mots_before = mots_nf.split(',')
        mots_after = []
        for mot in mots_before:
            print(mot)
            if mot in Listes_mots[categorie]:
                await ctx.send(f"Le mot {mot} existe déjà dans le dictionnaire local ! Il ne peut être ajouté.")
            else :
                mots_after.append(mot)
                            
        if os.path.isfile(file_path) == True:
            echo_data = '\n'.join(mots_after)
            await ctx.send(f"Nombre d'élements à mettre à jour : {len(mots_after)}")
            await ctx.send(f"Mise à jour du dictionnaire externe...")
            commande =  f"echo '{echo_data}' >> {file_path} | sort -o {file_path} {file_path}"
            print(commande)
            print(f"Commande exécutée : {commande}")
            resultat = subprocess.run(commande, shell=True, capture_output=True, text=True)
            print(f"Retour console : {resultat.stdout}")
            await ctx.send(f"Mise à jour du dictionnaire externe : OK !")
            await ctx.send(f"Mise à jour du dictionnaire local...")
            for mot in mots_after:
                Listes_mots[categorie].append(mot)
            motif_regex[categorie] = re.compile(r'\b(?:' + '|'.join(map(re.escape, Listes_mots[categorie])) + r')\b')
            await ctx.send(f"Compilation des motifs regex pour la catégorie {categorie} : OK !")
            await ctx.send(f"Nombre d'éléments chargés dans le dictionnaire local : {len(Listes_mots[categorie])}")
        else:
            await ctx.send(f"Ce dictionnaire ({categorie}) externe n'existe pas !")
    else:
        await ctx.send(f"Le nombre d'argument est insuffisant !\n^!addbl [mots ou expressions à ajouter] [catégorie]\nExemple :\n^!addbl Marine Le Pen,Zemmour,Macron Politique")
        
@bot.command()
async def test(ctx):
    mots = ["Mot1","Mot2"]
    await ctx.send("Clique sur le bouton en bas pour tester l'intéraction ! \n oaramètre __init__(timeout=None)", view=TestButton(mots))
    
@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')

@bot.event
async def on_message_edit(before, after):
    print(f"-------------------\nUn message a été modifié !\nDe : {before.author}\nID user : {before.author.id}\nID Salon : {before.channel.id}\nSalon : {before.channel} \nID : {before.id}\nLien du message : {before.jump_url}\nAvant : {before.content}\nAprès : {after.content}")
    canal_alerte = bot.get_channel(SALON_SUIVI_MESSAGES)
    if canal_alerte and before.content is not after.content:
        idModification = IdGenerator()
        embed = discord.Embed(
            description=f"<@{before.author.id}> a modifié son message ({before.jump_url}) dans le salon <#{before.channel.id}>",
            color=discord.Color.default()
        )
        embed.set_author(name=f"Modification n°{idModification}")
        embed.add_field(name="Avant", value=f"> {before.content}", inline=False)
        embed.add_field(name="Après", value=f"> {after.content}", inline=True)
            
        await canal_alerte.send(embed=embed)
    else:
        print("Le salon  de log défini est incorrect ! La modification n'a pas pu être logué !")
    
    if after.channel.id == SALON_PARTAGE_ACTU and 'http' in after.content and len(after.embeds) > 0 and len(before.embeds) == 0 :
        await after.create_thread(name=f"{after.embeds[0].title}")

@bot.event
async def on_message_delete(message):
    canal_alerte = bot.get_channel(SALON_SUIVI_MESSAGES)
    if canal_alerte:
        idSuppression = IdGenerator()
        embed = discord.Embed(
            description=f"<@{message.author.id}> a supprimé son message ({message.jump_url}) dans le salon <#{message.channel.id}>",
            color=discord.Color.default()
        )
        embed.set_author(name=f"❌ Suppression n°{idSuppression}")
        embed.add_field(name="Message supprimé", value=f"> {message.content}")
        
        await canal_alerte.send(embed=embed)
        
    else:
        print("Le salon  de log défini est incorrect ! La modification n'a pas pu être logué !")

@bot.event
async def on_message(message):
    print(f'-------------------\nDe : {message.author}\nID user : {message.author.id}\nID Salon : {message.channel.id}\nSalon : {message.channel} \nPosition : {message.position}\nid : {message.id}\nLien du message : {message.jump_url}\nContenu : {message.content}')
    if message.content[0] == '!' and message.author.top_role.id in RolesByPass:
        await bot.process_commands(message)
    else:
        #Lit le message en transformant tout en minuscule
        content_message = message.content.lower()
        # Ne transforme pas le message
        content_message_no_lower = message.content
        
        #Détecteur de signalement Insultes
        if str(message.channel.id) in liste_salons_insultes:
            pass
        else:
            # Vérifier si le message correspond au motif regex de la catégorie insultes
            liste_mots = []
            correspondances = motif_regex['insultes'].findall(content_message)
            # if motif_regex['insultes'].search(content_message):
            if correspondances:
                for mot in correspondances:
                    liste_mots.append(mot)
                mots = ','.join(liste_mots)
                await AutoSignalementAlerte(content_message,message.author,message.jump_url,message.channel.id,message.author.id,mots,"Insultes")

        #Détecteur de signalement politique
        if str(message.channel.id) in liste_salons_politique:
            pass
        else:
            # Vérifier si le message correspond au motif regex de la catégorie politique
            liste_mots = []
            correspondances = motif_regex['politique'].findall(content_message_no_lower)
            
            if correspondances:
                for mot in correspondances:
                    liste_mots.append(mot)
                mots = ','.join(liste_mots)
                await AutoSignalementAlerte(content_message_no_lower,message.author,message.jump_url,message.channel.id,message.author.id,mots,"Politique")

        # PARTIE PARTAGE ACTU
        if message.channel.id == SALON_PARTAGE_ACTU:
            url = extractUrl(message.content)
            if url:
                title = await getUrlTitle(url)
                await message.create_thread(name=title)
            else:
                try:
                    await message.author.send(
                        "🚫 Ton message a été supprimé car il ne contenait pas d'URL, ce qui est requis dans ce salon."
                    )
                    await sendLog(typeError="Informatif", markCritical=1, body=f"L'utilisateur {message.author} a été averti car il a envoyé un message sans URL dans #PartageActus.", admMention=False)
                except discord.Forbidden:
                    # Impossible de DM l'utilisateur
                    pass
                
                await message.delete()


async def AutoSignalementAlerte(message, auteur, link_message, channelid, userid, motsIdentifies, categorie):
    canal_alerte = bot.get_channel(ID_CANAL_AUTOSIGNALEMENT)
    if canal_alerte:
        idSignalement = IdGenerator()
        # alerte = f"**Alerte !** L'utilisateur {auteur} a utilisé un mot interdit dans le message suivant : `{message}`"
        embed = discord.Embed(
            description=f"<@{userid}> a envoyé un message ({link_message}) qui est **interdit** dans le salon <#{channelid}>",
            color=discord.Color.default()
        )
        embed.set_author(name=f"[AUTO] Signalement n°{idSignalement}")
        embed.add_field(name="Contenu du message", value=f"> {message}", inline=False)
        embed.add_field(name="Mots identifiés", value=f"> {motsIdentifies}", inline=True)
        embed.add_field(name="Catégorie", value=f"> {categorie}", inline=True)
        
        await canal_alerte.send(embed=embed)
    else:
        print("Aucun salon de log a été défini ! Le signalement n'a pas pu être logué !")
async def getUrlTitle(url):
    url = url.strip()
    print(f"[DEBUG] L'URL est : {url}")

    # Add 'https://' if the URL doesn't have a scheme
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
    # response.raise_for_status()  # Raise an error if the request fails

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
    
        if title_tag:
            title = title_tag.get_text()
            print(f"[DEBUG] Le titre est : {title}")
            return title
        else:
            print(f"[DEBUG] : Erreur lors de l'extraction du titre \n")
            id = IdGenerator()
            await sendLog(typeError = "Erreur programme", markCritical=4, body=f"Le programme n' a pas réussi à extraire le titre de l'URL : {url}.\nCode retour HTTP : 200\nTitre du thread potentiel : Partage n°{id}", admMention=True)
            return f"Partage n°{id}"
    else: 
            print(f"[DEBUG] : Code retour différent de 200 \n")
            id = IdGenerator()
            await sendLog(typeError = "Erreur programme", markCritical=3, body=f"Le code de retour HTTP n'est pas celui attendu.\nCode retour HTTP : {response.status_code}\nTitre du thread potentiel : Partage n°{id}", admMention=False)
            return f"Partage n°{id}"
def extractUrl(message: str):
    url_regex = r'(https?://[^\s]+|www\.[^\s]+)'
    match = re.search(url_regex, message)
    if match:
        return match.group(0)
    
        
def IdGenerator():
    maintenant = datetime.now()
    AnneeCourte =  str(int(maintenant.strftime("%Y"))-2000)
    MoisJourHeureMinuteSeconde = maintenant.strftime("%m%d%H%m%S")
    identifiant = f"{AnneeCourte}{MoisJourHeureMinuteSeconde}"
    return identifiant

async def MajListe(ctx, categorie):
    path = f"AutoSignalement/dictionnaire_{categorie}.txt"
    await ctx.send(f"Le path du dictionnaire est : {path}")
    if os.path.isfile(path) == True:
        with open(path, "r") as fichier:
            contenu_fichier = fichier.read()
            liste = contenu_fichier.split('\n')
            Listes_mots[categorie] = liste
            print(Listes_mots[categorie])
            await ctx.send(f"Nombre d'éléments chargés : {len(Listes_mots[categorie])}")
            Listes_mots[categorie] = list(filter(len, Listes_mots[categorie]))
            motif_regex[categorie] = re.compile(r'\b(?:' + '|'.join(map(re.escape, Listes_mots[categorie])) + r')\b')
            await ctx.send(f"Compilation des motifs regex pour la catégorie {categorie} : OK !")
    else:
         await ctx.send(f"Le dictionnaire n'existe pas !")
        
async def sendLog(typeError: str, markCritical: int, body: str, admMention: bool):
    id = IdGenerator()
    canal_log = bot.get_channel(ID_CANAL_LOG)
    
    embed = discord.Embed(
        description=f"Type erreur : {typeError} \nCritique de l'erreur : {markCritical} / 5",
        color=discord.Color.default()
    )
    embed.set_author(name=f"Log n°{id}")
    embed.add_field(name="Contenu", value=f"> {body}", inline=False)
    if admMention:
        embed.add_field(name="Equipe concernée", value=f"> <@&1012814021344374948>", inline=True)
    await canal_log.send(embed=embed)
    
         
class TestButton(discord.ui.View):
    def __init__(self, mots):
        super().__init__(timeout=None)
        self.mots = mots
        #Solution temporaire
        identifiant = str(random.randint(0, 10000))
        for mot in mots:
            bouton = MonBouton(label=f"Supprimer {mot}", custom_id=f"{mot}+{identifiant}", style=discord.ButtonStyle.danger)
            self.add_item(bouton)
        
class MonBouton(discord.ui.Button):  
    async def callback(self, interaction):
        mot = self.custom_id.split('+')[0]
        await interaction.response.send_message(f"Tu as cliqué sur {mot}",ephemeral=True)
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
    
