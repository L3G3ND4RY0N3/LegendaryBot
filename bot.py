import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os as os
import asyncio
from itertools import cycle
#from keep_alive import keep_alive




load_dotenv()


bot = commands.Bot(command_prefix= "$", intents= discord.Intents.all())
bot_status = cycle(["Slapping Juratyp", "Preparing next Slap", "Searching for new Targets"])

@tasks.loop(seconds = 5)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(bot_status)))

@bot.event
async def on_ready():
    print(f"{bot.user.name} Bot is up and running!")
    change_status.start()
    try: 
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

async def load():
    for folder in os.listdir("modules"):
        if os.path.exists(os.path.join("modules", folder, "cog.py")):
            await bot.load_extension(f"modules.{folder}.cog")
                    

#keep_alive()

async def main():
    async with bot:
        await load()
        await bot.start(os.getenv('TOKEN'))

asyncio.run(main())



