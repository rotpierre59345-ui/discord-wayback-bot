
import os
import discord
from discord.ext import commands
import yt_dlp
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
    await bot.tree.sync()

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

@bot.tree.command(name="download", description="Télécharge une vidéo YouTube archivée")
async def download(interaction: discord.Interaction, url: str):
    # 1. On affiche "Le bot réfléchit..." (comme dans l'exemple)
    await interaction.response.defer(thinking=True)

    # 2. Recherche de l'archive
    archive_url = get_wayback_url(url)
    
    if not archive_url:
        await interaction.followup.send(f"Aucune archive trouvée pour cette URL.", ephemeral=True)
        return

    # 3. Préparation du téléchargement
    video_id = str(int(time.time()))
    output_filename = f"video_{video_id}.mp4"
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_filename,
        'noplaylist': True,
        'max_filesize': 24 * 1024 * 1024,
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    }

    try:
        loop = asyncio.get_event_loop()
        
        def run_ydl():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(archive_url, download=True)

        info = await loop.run_in_executor(None, run_ydl)
        actual_filename = output_filename
        
        # Vérification du fichier
        if not os.path.exists(actual_filename):
            for f in os.listdir('.'):
                if f.startswith(f"video_{video_id}"):
                    actual_filename = f
                    break

        if os.path.exists(actual_filename):
            # 4. Envoi du fichier SEUL (comme dans l'exemple)
            # On utilise followup.send qui va remplacer le "réfléchit" ou s'ajouter proprement
            await interaction.followup.send(file=discord.File(actual_filename))
            
            # Nettoyage
            os.remove(actual_filename)
        else:
            await interaction.followup.send("Erreur lors du téléchargement de la vidéo.", ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"Une erreur est survenue.", ephemeral=True)
        if os.path.exists(output_filename):
            os.remove(output_filename)

# Exécuter le bot
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN:
    bot.run(DISCORD_TOKEN)
else:
    print("ERREUR : DISCORD_TOKEN manquant.")
