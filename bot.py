import discord
from discord.ext import tasks, commands
import asyncio
import os
from config import TOKEN, GUILD_ID, VOICE_CHANNEL_ID

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None
SILENT_FILE = "silent.mp3"

async def ensure_voice():
    global voice_client
    guild = bot.get_guild(GUILD_ID)

    if guild is None:
        print("❌ 找不到伺服器")
        return

    channel = guild.get_channel(VOICE_CHANNEL_ID)

    if channel is None:
        print("❌ 找不到語音頻道")
        return

    try:
        if voice_client is None or not voice_client.is_connected():
            print("🔄 正在連接語音頻道...")
            voice_client = await channel.connect(reconnect=True)
            print(f"✅ 已進入 {channel.name}")

        if not voice_client.is_playing():
            print("🎵 開始播放靜音串流")
            source = discord.FFmpegPCMAudio(
                SILENT_FILE,
                options='-stream_loop -1'
            )
            voice_client.play(source)

    except Exception as e:
        print("⚠️ 語音連接錯誤:", e)

async def reconnect_voice():
    global voice_client
    try:
        if voice_client:
            await voice_client.disconnect(force=True)
    except:
        pass
    voice_client = None
    await asyncio.sleep(3)
    await ensure_voice()

@bot.event
async def on_ready():
    print(f"🤖 Bot上線成功：{bot.user}")
    await ensure_voice()
    watchdog.start()

@tasks.loop(minutes=1)
async def watchdog():
    global voice_client
    try:
        if voice_client is None:
            print("⚠️ 沒有語音客戶端，重連")
            await reconnect_voice()
            return

        if not voice_client.is_connected():
            print("⚠️ Bot掉出語音，重連")
            await reconnect_voice()
            return

        if not voice_client.is_playing():
            print("⚠️ 靜音串流停止，重新播放")
            await reconnect_voice()
            return

    except Exception as e:
        print("⚠️ watchdog錯誤:", e)
        await reconnect_voice()

@bot.command()
async def ping(ctx):
    await ctx.send("✅ 我正在24小時掛語音中")

@bot.command()
async def rejoin(ctx):
    await ctx.send("♻️ 重新掛回語音")
    await reconnect_voice()

bot.run(TOKEN)