import discord
from discord.ext import commands
from pytube import YouTube
from dotenv import load_dotenv
from os import getenv

load_dotenv()

TOKEN = getenv("BOT_KEY")

intents = discord.Intents.all()

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
async def play(ctx, url):
    voice_client = ctx.guild.voice_client
    if not voice_client:
        await ctx.send("I'm not in a voice channel. Use !join to summon me.")
        return

    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        await ctx.send(f"Now playing: {yt.title}")
        voice_client.play(discord.FFmpegPCMAudio(audio_stream.url))
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

# Run the bot
bot.run(TOKEN)
