import discord
from discord.ext import commands
import yt_dlp
import asyncio
import re

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# yt-dlp options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

# Queues per voice channel ID
queues = {}  # key: channel.id, value: list of YTDLSource

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')

    @classmethod
    async def from_input(cls, input_text, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        if re.match(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$', input_text):
            query = input_text
        else:
            query = f"ytsearch1:{input_text}"

        data = await loop.run_in_executor(
            None,
            lambda: ytdl.extract_info(query, download=not stream)
        )

        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

async def play_next(vc: discord.VoiceClient, channel_id: int):
    if queues.get(channel_id):
        next_source = queues[channel_id].pop(0)
        vc.play(next_source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(vc, channel_id), bot.loop))
        channel = vc.channel
        text_channel = discord.utils.get(channel.guild.text_channels, name="general") or channel.guild.text_channels[0]
        await text_channel.send(f'🎶 Now playing: **{next_source.title}**')
    else:
        pass

def get_queue(channel_id: int):
    return queues.setdefault(channel_id, [])

@bot.event
async def on_ready():
    print(f'✅ Bot connected as {bot.user}')

@bot.command(name="join")
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("✅ Connected to your voice channel.")
    else:
        await ctx.send("⚠️ You need to be in a voice channel first!")

@bot.command(name="leave")
async def leave(ctx):
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
        queues.pop(vc.channel.id, None)
        await ctx.send("✅ Disconnected and cleared queue.")
    else:
        await ctx.send("⚠️ Not in a voice channel.")

@bot.command(name="play")
async def play(ctx, *, input_text):
    if not ctx.author.voice:
        await ctx.send("⚠️ You need to be in a voice channel first!")
        return

    vc = ctx.voice_client
    if not vc:
        vc = await ctx.author.voice.channel.connect()

    async with ctx.typing():
        player = await YTDLSource.from_input(input_text, loop=bot.loop, stream=True)
        channel_id = vc.channel.id
        queue = get_queue(channel_id)

        if not vc.is_playing():
            vc.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(vc, channel_id), bot.loop))
            await ctx.send(f'🎶 Now playing: **{player.title}**')
        else:
            queue.append(player)
            await ctx.send(f'➕ Added to queue: **{player.title}**')

@bot.command(name="skip")
async def skip(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await ctx.send("⏭️ Skipped current track.")
    else:
        await ctx.send("⚠️ No track is currently playing.")

@bot.command(name="np")
async def now_playing(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        await ctx.send(f'🎶 Now playing: **{vc.source.title}**')
    else:
        await ctx.send("⚠️ No track is currently playing.")

@bot.command(name="volume")
async def volume(ctx, volume: int):
    vc = ctx.voice_client
    if vc and vc.source:
        vc.source.volume = max(0, min(volume / 100, 2))
        await ctx.send(f'🔊 Volume set to {volume}%')
    else:
        await ctx.send("⚠️ Not playing anything to adjust volume.")

@bot.command(name="queue")
async def show_queue(ctx):
    vc = ctx.voice_client
    if not vc:
        await ctx.send("⚠️ The bot is not in a voice channel.")
        return

    channel_id = vc.channel.id
    queue = queues.get(channel_id, [])

    if not queue:
        await ctx.send("✅ The queue is empty.")
        return

    message = "🎵 **Upcoming songs in this channel:**\n"
    for i, song in enumerate(queue, start=1):
        message += f"{i}. {song.title}\n"

    await ctx.send(message)

@bot.command(name="radio")
async def radio(ctx, *, station="antena1"):
    radios = {
        "antena1": "https://radiocast.rtp.pt/antena180a.mp3",
        "antena2": "https://radiocast.rtp.pt/antena280a.mp3",
        "antena3": "https://radiocast.rtp.pt/antena380a.mp3",
        "rfm": "https://29043.live.streamtheworld.com/RFM.mp3",
        "cidadefm": "https://stream-icy.bauermedia.pt/cidade.mp3",
        "radiocomercial": "https://stream-icy.bauermedia.pt/comercial.mp3",
        "m80": "https://stream-icy.bauermedia.pt/m80.mp3"
    }

    if not ctx.author.voice:
        await ctx.send("⚠️ You need to be in a voice channel first!")
        return

    vc = ctx.voice_client
    if not vc:
        vc = await ctx.author.voice.channel.connect()

    url = radios.get(station.lower())
    if not url:
        await ctx.send(f"⚠️ Station not found. Available: {', '.join(radios.keys())}")
        return

    vc.stop()
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url))
    vc.play(source)
    await ctx.send(f'📻 Playing radio: **{station}**')

@bot.command(name="stop")
async def stop(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.stop()
        queues.pop(vc.channel.id, None)
        await ctx.send("⏹️ Stopped playback and cleared queue.")
    else:
        await ctx.send("⚠️ Nothing is playing.")

bot.run("YOUR_DISCORD_BOT_TOKEN")
