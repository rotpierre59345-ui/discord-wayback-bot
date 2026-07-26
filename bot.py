
import os
import discord
from discord.ext import commands
import yt_dlp
import requests
from waybackpy import WaybackMachineCDXServerAPI
import time
import asyncio

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
        archive = cdx.oldest()
        if archive:
            return archive.archive_url
    except:
        pass
    return None

@bot.tree.command(name="download", description="Télécharge une vidéo YouTube supprimée via la Wayback Machine")
async def download(interaction: discord.Interaction, url: str):
    await interaction.response.defer(thinking=True)
    
    status_message = await interaction.followup.send("🔍 Recherche d'une archive sur la Wayback Machine...")

    archive_url = get_wayback_url(url)
    
    if not archive_url:
        await interaction.edit_original_response(content=f"❌ Aucune archive trouvée pour cette URL.")
        return

    await interaction.edit_original_response(content=f"✅ Archive trouvée : <{archive_url}>\n⏳ Initialisation du téléchargement (cela peut être lent)...")

    video_id = str(int(time.time()))
    output_filename = f"video_{video_id}.mp4"
    
    # Fonction de callback pour suivre la progression
    def progress_hook(d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%')
            s = d.get('_speed_str', 'N/A')
            # On ne met pas à jour trop souvent pour éviter de se faire rate-limit par Discord
            # Cette fonction est appelée dans un thread séparé par yt-dlp
            pass

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_filename,
        'noplaylist': True,
        'max_filesize': 24 * 1024 * 1024,
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [progress_hook],
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    }

    try:
        # On lance le téléchargement dans un thread séparé pour ne pas bloquer l'event loop
        loop = asyncio.get_event_loop()
        
        await interaction.edit_original_response(content=f"✅ Archive trouvée !\n📥 Téléchargement en cours depuis les serveurs d'Archive.org... (Veuillez patienter)")
        
        def run_ydl():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(archive_url, download=True)

        info = await loop.run_in_executor(None, run_ydl)
        actual_filename = ydl_opts['outtmpl']
        
        if not os.path.exists(actual_filename):
            # Essayer de trouver le fichier si yt-dlp a changé l'extension
            for f in os.listdir('.'):
                if f.startswith(f"video_{video_id}"):
                    actual_filename = f
                    break

        if os.path.exists(actual_filename):
            await interaction.edit_original_response(content="📤 Téléchargement terminé ! Envoi du fichier vers Discord...")
            
            filesize = os.path.getsize(actual_filename)
            if filesize > 25 * 1024 * 1024:
                await interaction.edit_original_response(content=f"⚠️ La vidéo fait {filesize/(1024*1024):.1f}MB (Limite Discord : 25MB). Impossible de l'envoyer.")
            else:
                await interaction.followup.send(content="✅ Voici votre vidéo !", file=discord.File(actual_filename))
                await interaction.delete_original_response() # Supprime le message de statut
            
            os.remove(actual_filename)
        else:
            await interaction.edit_original_response(content="❌ Échec : Le fichier vidéo n'a pas pu être récupéré.")

    except Exception as e:
        error_str = str(e)
        if "File is too large" in error_str:
            await interaction.edit_original_response(content="❌ La vidéo est trop volumineuse pour Discord (>25MB).")
        else:
            await interaction.edit_original_response(content=f"❌ Erreur lors du téléchargement : {error_str[:100]}...")
        
        if os.path.exists(output_filename):
            os.remove(output_filename)

# Exécuter le bot
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN:
    bot.run(DISCORD_TOKEN)
else:
    print("ERREUR : DISCORD_TOKEN manquant.")
