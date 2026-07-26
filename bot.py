
import os
import discord
from discord.ext import commands
import yt_dlp
import requests
from waybackpy import WaybackMachineCDXServerAPI
import time

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées: {len(synced)}")
    except Exception as e:
        print(f"Erreur de synchronisation: {e}")

def get_wayback_url(youtube_url):
    """Cherche une archive de la vidéo sur la Wayback Machine."""
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    cdx = WaybackMachineCDXServerAPI(youtube_url, user_agent=user_agent)
    try:
        # On cherche la capture la plus ancienne ou la plus stable
        archive = cdx.oldest()
        if archive:
            return archive.archive_url
    except:
        pass
    return None

@bot.tree.command(name="download", description="Télécharge une vidéo YouTube supprimée via la Wayback Machine")
async def download(interaction: discord.Interaction, url: str):
    await interaction.response.defer(thinking=True) # Indique que le bot travaille

    archive_url = get_wayback_url(url)
    
    if not archive_url:
        await interaction.followup.send(f"❌ Aucune archive trouvée pour cette URL sur la Wayback Machine.")
        return

    await interaction.followup.send(f"🔍 Archive trouvée : <{archive_url}>\n⏳ Tentative de téléchargement du fichier vidéo...")

    # Paramètres yt-dlp optimisés pour Wayback Machine
    # On force le format mp4 et on limite la taille pour Discord
    video_id = str(int(time.time()))
    output_filename = f"video_{video_id}.mp4"
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_filename,
        'noplaylist': True,
        'max_filesize': 24 * 1024 * 1024, # 24MB pour rester sous la limite de 25MB de Discord
        'quiet': False,
        'no_warnings': False,
        # Wayback Machine nécessite souvent des headers spécifiques
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # On tente d'extraire et télécharger
            info = ydl.extract_info(archive_url, download=True)
            # yt-dlp peut changer l'extension, on récupère le nom final
            actual_filename = ydl.prepare_filename(info)
            
            # Si l'extension a changé (ex: .mkv), on le note
            if not os.path.exists(actual_filename) and os.path.exists(output_filename):
                actual_filename = output_filename

        if os.path.exists(actual_filename):
            filesize = os.path.getsize(actual_filename)
            if filesize > 25 * 1024 * 1024:
                await interaction.followup.send(f"⚠️ La vidéo a été téléchargée mais elle pèse {filesize/(1024*1024):.1f}MB, ce qui dépasse la limite de Discord (25MB).")
            else:
                await interaction.followup.send(content="✅ Voici votre vidéo :", file=discord.File(actual_filename))
            
            # Nettoyage
            os.remove(actual_filename)
        else:
            await interaction.followup.send("❌ Échec du téléchargement : Le fichier n'a pas pu être généré.")

    except Exception as e:
        error_msg = str(e)
        if "File is too large" in error_msg:
            await interaction.followup.send("❌ La vidéo archivée est trop volumineuse pour être envoyée sur Discord (>25MB).")
        else:
            await interaction.followup.send(f"❌ Une erreur est survenue lors du téléchargement : {error_msg}")
        
        # Nettoyage au cas où
        if os.path.exists(output_filename):
            os.remove(output_filename)

# Exécuter le bot
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN:
    bot.run(DISCORD_TOKEN)
else:
    print("ERREUR : DISCORD_TOKEN manquant dans les variables d'environnement.")
