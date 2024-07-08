import discord
from discord.ext import commands
from dotenv import load_dotenv
import os as os
import asyncio
from utils import settings
from utils.customwrappers import on_app_command_error

#Lädt das .env File mit dem Token!
load_dotenv()

logger=settings.logging.getLogger("discord")

#Bot initialiseren und Status Zyklus festlegen
bot = commands.Bot(command_prefix= "$", intents= discord.Intents.all())

#Nachrichten beim Starten des Bots, wie viele Slash Commands gefunden wurden und welche Module geladen sind.
@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} Bot is up and running and even logging!")
    #bot.owner_id = (await bot.application_info()).owner.id
    print(f"{bot.user.name} is running :)")
    try: 
        synced = await bot.tree.sync()
        bot.tree.error(on_app_command_error)
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(e)

#Laden der Module aus den cog.py Files
async def load():
    for folder in os.listdir("modules"):
        if os.path.exists(os.path.join("modules", folder, "cog.py")):
            await bot.load_extension(f"modules.{folder}.cog", package=__package__)


#Startet den Bot
async def main():
    async with bot:
        await load()
        await bot.start(os.getenv('TOKEN'))

asyncio.run(main())