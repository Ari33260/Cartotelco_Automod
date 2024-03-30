import discord
import re
import os
from dotenv import load_dotenv
from datetime import datetime

# VARIABLES GLOBALES (PARAMETRES)
ID_CANAL_AUTOSIGNALEMENT = 1223257795571351572
SALON_SUIVI_MESSAGES = 1223280408939073536

print("Initialisation en cours ...")
load_dotenv()
TOKEN = os.getenv('TOKEN')
print(".env chargé : OK !")

print(f"Salon défini pour le suivi des messages : OK ! (ID : {SALON_SUIVI_MESSAGES}.") if SALON_SUIVI_MESSAGES is not None else print(f"Salon défini pour le suivi des messages : NOK !\nVeuillez définir un ID de salon dans le fichier main.py à la variable globale : SALON_SUIVI_MESSAGES")
print("\nChargement des dictionnaires...")
# Liste des mots interdits pour la catégorie insulte 
with open("AutoSignalement/dictionnaire_insultes.txt", "r") as fichier:
    contenu_fichier_insultes = fichier.read()
    liste_insultes = contenu_fichier_insultes.split('\n')
    #supprime les éléments vides
    liste_insultes = list(filter(len, liste_insultes))
print("Catégortie Insultes : OK !\nElements chargés : ",len(liste_insultes))

# Liste des mots interdits pour la catégorie politique 
with open("AutoSignalement/dictionnaire_politique.txt", "r") as fichier:
    contenu_fichier_politique = fichier.read()
    liste_politique = contenu_fichier_politique.split('\n')
    #supprime les éléments vides
    liste_politique = list(filter(len, liste_politique))
print("Catégortie politique : OK !\nElements chargés : ",len(liste_politique))

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

motif_regex_insultes = re.compile(r'\b(?:' + '|'.join(map(re.escape, liste_insultes)) + r')\b')
print("\nCompilation des motifs regex pour la catégorie insultes : OK !")

motif_regex_politique = re.compile(r'\b(?:' + '|'.join(map(re.escape, liste_politique)) + r')\b')
print("Compilation des motifs regex pour la catégorie politique : OK !")

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        
    async def on_message_edit(self, before, after):
        print(f"-------------------\nUn message a été modifié !\nDe : {before.author}\nID user : {before.author.id}\nID Salon : {before.channel.id}\nSalon : {before.channel} \nID : {before.id}\nLien du message : {before.jump_url}\nAvant : {before.content}\nAprès : {after.content}")
        canal_alerte = client.get_channel(SALON_SUIVI_MESSAGES)
        if canal_alerte and before.content is not after.content:
            idModification = await self.IdGenerator()
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
    async def on_message(self, message):
        print(f'-------------------\nDe : {message.author}\nID user : {message.author.id}\nID Salon : {message.channel.id}\nSalon : {message.channel} \nPosition : {message.position}\nid : {message.id}\nLien du message : {message.jump_url}\nContenu : {message.content}')

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
            correspondances = motif_regex_insultes.findall(content_message)
            # if motif_regex_insultes.search(content_message):
            if correspondances:
                for mot in correspondances:
                    liste_mots.append(mot)
                mots = ','.join(liste_mots)
                await self.AutoSignalementAlerte(content_message,message.author,message.jump_url,message.channel.id,message.author.id,mots,"Insultes")

        #Détecteur de signalement politique
        if str(message.channel.id) in liste_salons_politique:
            pass
        else:
            # Vérifier si le message correspond au motif regex de la catégorie politique
            liste_mots = []
            correspondances = motif_regex_politique.findall(content_message_no_lower)
            
            if correspondances:
                for mot in correspondances:
                    liste_mots.append(mot)
                mots = ','.join(liste_mots)
                await self.AutoSignalementAlerte(content_message_no_lower,message.author,message.jump_url,message.channel.id,message.author.id,mots,"Politique") 

    async def AutoSignalementAlerte(self, message, auteur, link_message, channelid, userid, motsIdentifies, categorie):
        canal_alerte = client.get_channel(ID_CANAL_AUTOSIGNALEMENT)
        if canal_alerte:
            idSignalement = await self.IdGenerator()
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
    async def IdGenerator(self):
        maintenant = datetime.now()
        AnneeCourte =  str(int(maintenant.strftime("%Y"))-2000)
        MoisJourHeureMinuteSeconde = maintenant.strftime("%m%d%H%m%S")
        identifiant = f"{AnneeCourte}{MoisJourHeureMinuteSeconde}"
        return identifiant
            
            
intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)
