import discord
from discord.ext import commands
from discord import app_commands, ButtonStyle
from discord.ui import View, Button
import json
from utils import settings

logger=settings.logging.getLogger("discord")

class Help(commands.Cog, name="Help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info("Help.py is ready!")

    def createHelpEmbed(self, pageNum=0, inline=False):
        with open("modules/Help/json/help.json", "r") as f:
            helpGuide = json.load(f)
        pageNum = pageNum % len(list(helpGuide))
        pageTitle = list(helpGuide)[pageNum]
        embed=discord.Embed(color=discord.Color.blurple(), title=pageTitle)
        for key, val in helpGuide[pageTitle].items():
            embed.add_field(name=key, value=val, inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {len(list(helpGuide))}")
        return embed

    @app_commands.command(name="help", description="Lists some commands with explanations!")
    async def help(self, interaction: discord.Interaction):
        currentPage = 0

        async def next_callback(interaction: discord.Interaction):
            nonlocal currentPage, sent_msg
            currentPage += 1
            await interaction.response.edit_message(embed=Help.createHelpEmbed(self, pageNum=currentPage), view=myview)

        async def prev_callback(interaction: discord.Interaction):
            nonlocal currentPage, sent_msg
            currentPage -= 1
            await interaction.response.edit_message(embed=Help.createHelpEmbed(self, pageNum=currentPage), view=myview)

        async def quit_callback(interaction: discord.Interaction):
            await interaction.response.edit_message(content="Hope this helped!", embed=None, view=None)

        nextButton = Button(label=">", style=ButtonStyle.blurple)
        nextButton.callback = next_callback
        prevButton = Button(label="<", style=ButtonStyle.blurple)
        prevButton.callback = prev_callback
        quitbutton = Button(label="x", style=ButtonStyle.red)
        quitbutton.callback = quit_callback

        myview = View(timeout=180)
        myview.add_item(prevButton)
        myview.add_item(nextButton)
        myview.add_item(quitbutton)

        sent_msg = await interaction.response.send_message(embed=Help.createHelpEmbed(self, 0, False), view=myview)

async def setup(bot):
    await bot.add_cog(Help(bot))