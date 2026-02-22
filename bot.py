import discord
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import asyncio

# Import your brand new database file!
import database

# --- 1. SETUP CREDENTIALS ---
DISCORD_TOKEN = 'YOUR_DISCORD_BOT_TOKEN'
SPOTIFY_CLIENT_ID = 'your_spotify_client_id'
SPOTIFY_CLIENT_SECRET = 'your_spotify_client_secret'

# --- 2. INITIALIZE APIs AND DATABASE ---
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Run the setup function from your database.py file
database.setup_database()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'ytsearch'
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - Modules loaded and ready!')

# --- 3. DATABASE COMMANDS ---

@bot.command(name='save')
async def save_track(ctx, url: str):
    """Saves a Spotify track using the separate database file."""
    try:
        track = sp.track(url)
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        
        # Send the data over to database.py to be saved
        database.save_song_to_db(ctx.author.id, track_name, artist_name, url)
        
        await ctx.send(f"Success! Saved **{track_name}** by **{artist_name}** to your database.")
    except Exception as e:
        await ctx.send("Error: Make sure you sent a valid Spotify Track URL.")

@bot.command(name='myplaylist')
async def show_playlist(ctx):
    """Shows all your saved tracks by asking the database file."""
    # Ask database.py to get the songs
    rows = database.get_user_playlist(ctx.author.id)
    
    if not rows:
        await ctx.send("Your database is empty! Use !save <spotify_url> to add songs.")
        return
        
    response = "**Your Saved Tracks:**\n"
    for idx, row in enumerate(rows, start=1):
        response += f"{idx}. **{row[0]}** by {row[1]} \n"
    await ctx.send(response)

# --- 4. MUSIC PLAYER COMMANDS ---

@bot.command(name='play')
async def play_track(ctx, url: str):
    """Plays a Spotify track in the voice channel."""
    if not ctx.message.author.voice:
        await ctx.send("You need to join a voice channel first!")
        return
    
    channel = ctx.message.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        voice_client = await channel.connect()

    try:
        track = sp.track(url)
        search_query = f"{track['name']} {track['artists'][0]['name']} audio"
        await ctx.send(f"Looking up **{track['name']}**...")
    except Exception:
        await ctx.send("Invalid Spotify URL. Please send a single track link.")
        return

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search_query, download=False))
        song_url = data['entries'][0]['url']
        
        if voice_client.is_playing():
            voice_client.stop()

        ffmpeg_options = {'options': '-vn'}
        voice_client.play(discord.FFmpegPCMAudio(song_url, **ffmpeg_options))
        await ctx.send(f"Now playing: **{track['name']}** by **{track['artists'][0]['name']}**")
        
    except Exception as e:
        await ctx.send("Error: Failed to play audio. Make sure ffmpeg is in your bot folder.")
        print(e)

@bot.command(name='leave')
async def leave_channel(ctx):
    """Stops the music and leaves the voice channel."""
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I am not currently in a voice channel.")

bot.run(DISCORD_TOKEN)