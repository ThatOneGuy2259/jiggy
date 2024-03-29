from asyncio import run_coroutine_threadsafe
import discord
from discord.ext import commands
from pytube import YouTube
from dotenv import load_dotenv
from os import getenv

load_dotenv()

TOKEN = getenv("BOT_KEY")

intents = discord.Intents.all()

songQueue = []

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Command: Join voice channel
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You are not in a voice channel.")

# Command: Leave voice channel
@bot.command()
async def leave(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
    else:
        await ctx.send("I'm not in a voice channel.")

# Command: Play YouTube video
@bot.command()
async def play(ctx, urlInput=None, nextSong=None):
    voice_client = ctx.guild.voice_client
    if not voice_client:
        await ctx.send("I'm not in a voice channel. Use !join to summon me.")
        return
    
    def play_next(error=None):
        if len(songQueue) > 0:
            next_url = songQueue.pop(0)
            run_coroutine_threadsafe(play(ctx, nextSong=next_url), bot.loop)

    if voice_client.is_playing() and urlInput:
        songQueue.append(urlInput)
        await ctx.send(f"Added to queue: {urlInput}")
    else:
        if not nextSong:
            nextSong = urlInput
        try:
            yt = YouTube(nextSong)
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_stream.download(filename="audio.mp4")
            await ctx.send(f"Now playing: {yt.title}")
            voice_client.play(discord.FFmpegPCMAudio("audio.mp4"), after=play_next)
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")


# Command: Stop playing
@bot.command()
async def stop(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_playing():
        songQueue.clear()
        voice_client.stop()
        await ctx.send("Playback stopped.")
    else:
        await ctx.send("I'm not playing anything.")

# Command: Skip to next song
@bot.command()
async def skip(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Skipped to the next song.")
    else:
        await ctx.send("I'm not playing anything.")

# Run the bot
bot.run(TOKEN)
