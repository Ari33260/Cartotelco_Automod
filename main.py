import discord
from discord.ext import commands
import re
import os
from dotenv import load_dotenv
from datetime import datetime
import subprocess

# VARIABLES GLOBALES (PARAMETRES)
ID_CANAL_AUTOSIGNALEMENT = 1223257795571351572
SALON_SUIVI_MESSAGES = 1223280408939073536
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

bot = commands.Bot(command_prefix='!',intents=intents)

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
        await ctx.send(f"Le nombre d'argument est insuffisant !")
        await ctx.send(f"^!addbl [mots ou expressions à ajouter] [catégorie]")
        await ctx.send(f"Exemple :")
        await ctx.send(f"^!addbl Marine Le Pen,Zemmour,Macron Politique")

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')

@bot.event
async def on_message_edit(before, after):
    print(f"-------------------\nUn message a été modifié !\nDe : {before.author}\nID user : {before.author.id}\nID Salon : {before.channel.id}\nSalon : {before.channel} \nID : {before.id}\nLien du message : {before.jump_url}\nAvant : {before.content}\nAprès : {after.content}")
    canal_alerte = bot.get_channel(SALON_SUIVI_MESSAGES)
    if canal_alerte and before.content is not after.content:
        idModification = await IdGenerator()
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

async def AutoSignalementAlerte(message, auteur, link_message, channelid, userid, motsIdentifies, categorie):
    canal_alerte = bot.get_channel(ID_CANAL_AUTOSIGNALEMENT)
    if canal_alerte:
        idSignalement = await IdGenerator()
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
        
async def IdGenerator():
    maintenant = datetime.now()
    AnneeCourte =  str(int(maintenant.strftime("%Y"))-2000)
    MoisJourHeureMinuteSeconde = maintenant.strftime("%m%d%H%m%S")
    identifiant = f"{AnneeCourte}{MoisJourHeureMinuteSeconde}"
    return identifiant

async def MajListe(ctx, categorie):
    path = f"AutoSignalement/dictionnaire_{categorie}.txt.copy"
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
         
        
bot.run(TOKEN)
