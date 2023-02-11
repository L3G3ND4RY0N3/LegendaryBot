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

jura = 768786872184078357
legend = 247342650917650434

    

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
                    

@bot.tree.command(name="hello", description="The Bot says hello to you")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user.mention}! This is my first slash (/) command.")

@bot.tree.command(name="say", description="Let the bot say something")
@app_commands.describe(resp = "What do you want me to say?")
async def say(interaction: discord.Interaction, resp: str):
    await interaction.response.send_message(f"{interaction.user.name} said: `{resp}`")

@bot.tree.command(name="slapjura", description="Gib Jura eine Schelle, weil er das verdient hat!")
async def slapjura(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention} gibt <@{jura}> eine krasse Schelle!")

@bot.tree.command(name="slaplegend", description="Schlage L3G3ND")
async def slaplegend(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention} gibt <@{legend}> eine krasse Schelle!")

@bot.tree.command(name="hug", description="Give someone a hug!")
@app_commands.describe(user = "Who do you want to hug?")
async def hug(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(f"{interaction.user.mention} gives {user.mention} a hug <3")

    

#keep_alive()

async def main():
    async with bot:
        await load()
        await bot.start(os.getenv('TOKEN'))

asyncio.run(main())



