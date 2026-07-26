# 🎥 Discord YouTube Wayback Downloader

Un bot Discord simple qui permet de récupérer et télécharger des vidéos YouTube supprimées en utilisant la **Wayback Machine** d'Archive.org.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/deploy?referrerCode=manus&repo=https://github.com/ytbarturery-cyber/discord-wayback-bot&envs=DISCORD_TOKEN)

## 🚀 Fonctionnalités

- **Commande Slash `/download`** : Entrez une URL YouTube et le bot cherchera une version archivée.
- **Téléchargement Automatique** : Si une archive est trouvée, le bot télécharge la vidéo et vous l'envoie directement sur Discord.
- **Gestion de la Wayback Machine** : Utilise l'API CDX pour trouver les captures les plus pertinentes.

## 🛠️ Installation & Déploiement

### 1. Prérequis
- Un compte [Discord Developer Portal](https://discord.com/developers/applications).
- Un bot créé avec les **Slash Commands** activées.
- Un compte [Railway](https://railway.app/).

### 2. Déploiement sur Railway
Cliquez sur le bouton ci-dessus ou suivez ces étapes :
1. Liez votre compte GitHub à Railway.
2. Créez un nouveau projet à partir de ce dépôt.
3. Ajoutez la variable d'environnement suivante :
   - `DISCORD_TOKEN` : Votre token secret de bot Discord.

## 📝 Utilisation

Une fois le bot en ligne et invité sur votre serveur :
1. Tapez `/download`.
2. Collez l'URL de la vidéo YouTube (même si elle est supprimée).
3. Attendez que le bot fasse sa magie !

## ⚠️ Limitations
- Les vidéos ne sont récupérables que si elles ont été archivées par la Wayback Machine.
- La taille maximale des fichiers envoyés est limitée par Discord (25MB par défaut pour les bots sans Nitro).

---
Développé avec ❤️ pour la préservation du contenu web.
