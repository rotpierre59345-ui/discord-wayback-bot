
import os
import discord
from discord.ext import commands
import yt_dlp
from waybackpy import WaybackMachineCDXServerAPI

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')
    await bot.tree.sync() # Synchronise les commandes slash

@bot.tree.command(name="download", description="Télécharge une vidéo YouTube archivée via la Wayback Machine")
async def download(interaction: discord.Interaction, url: str):
    await interaction.response.send_message(f"Recherche de la vidéo archivée pour {url}... Cela peut prendre un certain temps.")

    try:
        # Utiliser waybackpy pour trouver une archive
        wayback = WaybackMachineCDXServerAPI(url, user_agent="DiscordBot/1.0")
        archive_url = wayback.near(year=2020).archive_url # Essayer de trouver une archive à partir de 2020

        if not archive_url:
            await interaction.followup.send(f"Aucune archive trouvée pour {url} sur la Wayback Machine.")
            return

        await interaction.followup.send(f"Archive trouvée: {archive_url}. Tentative de téléchargement...")

        # Utiliser yt-dlp pour télécharger la vidéo depuis l'archive
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': 'video.mp4',
            'noplaylist': True,
            'max_filesize': 50 * 1024 * 1024, # Limite de 50MB pour Discord
            'merge_output_format': 'mp4',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(archive_url, download=True)
            filename = ydl.prepare_filename(info_dict)

        if os.path.exists(filename):
            await interaction.followup.send(file=discord.File(filename))
            os.remove(filename) # Supprimer le fichier après l'envoi
        else:
            await interaction.followup.send("Erreur: Le fichier vidéo n'a pas été trouvé après le téléchargement.")

    except Exception as e:
        await interaction.followup.send(f"Une erreur est survenue: {e}")

# Exécuter le bot
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN:
    bot.run(DISCORD_TOKEN)
else:
    print("Erreur: Le token Discord n'est pas défini. Veuillez définir la variable d'environnement DISCORD_TOKEN.")
