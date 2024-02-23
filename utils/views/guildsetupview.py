import discord
import json
from utils import filepaths as fp
from utils.embeds import embedbuilder as emb
import utils.settings as settings
from utils import guildjsonfunctions as gjf

logger=settings.logging.getLogger("discord")

class GuildSetupView(discord.ui.View):
    def __init__(self, interaction, bot, currentPage, channel):
        self.interaction = interaction
        self.bot = bot
        self.currentPage = currentPage
        self.channel = channel
        super().__init__(timeout=180)


    ######################## Buttons 
    
    # Previous Page
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple, custom_id='Activate_Guild_Setup_Back', emoji="⬅")
    async def guild_setup_back(self, interaction: discord.Interaction, button:discord.ui.Button):
        self.currentPage -= 1
        embed = emb.createSettingEmbed(interaction.guild, pageNum=self.currentPage)
        self.channel = embed.fields[0].name.split(" ")[0].lower()

        await interaction.response.edit_message(embed=embed, view=GuildSetupView(interaction, self.bot, self.currentPage, self.channel))

        return


    # Next page
    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, custom_id='Activate_Guild_Setup_Forward', emoji="➡")
    async def guild_setup_forward(self, interaction: discord.Interaction, button:discord.ui.Button):
        self.currentPage += 1
        embed = emb.createSettingEmbed(interaction.guild, pageNum=self.currentPage)
        self.channel = embed.fields[0].name.split(" ")[0].lower()

        await interaction.response.edit_message(embed=embed, view=GuildSetupView(interaction, self.bot, self.currentPage, self.channel))

        return
    

    # Quit menu button
    @discord.ui.button(label="Quit", style=discord.ButtonStyle.grey, custom_id='Activate_Guild_Setup_Quit', emoji="❌")
    async def guild_setup_quit(self, interaction: discord.Interaction, button:discord.ui.Button):
        # TODO: build final embed ^^
        await interaction.response.edit_message(content="Bye!", embed=None, view=None)

        return
    

    ############# deaktivieren der jeweiligen Funktionalität 
    @discord.ui.button(label="Deactivate", style=discord.ButtonStyle.red, custom_id='Deactivate_Guild_Setup', emoji="🛑", row=1)
    async def guild_setup_activate(self, interaction: discord.Interaction, button:discord.ui.Button):
        try: # if for some reason anything fails, log the exception and still send an embed
            returncode = gjf.update_guild_channel(str(interaction.guild.id), 0, self.channel)
        except Exception as e:
            logger.exception(f"{e}")
            returncode = -1

        if returncode < 0:
            embed = emb.warn_embed(f"There was an error deactivating the {self.channel} feature.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = emb.success_embed(f"Successfully deactivatet the {self.channel} module for this guild!")
        await interaction.response.send_message(embed=embed)

        return


    # ############## aktivieren der jeweiligen Funktionalität, TODO: neue Viewklasse mit Selectionmenü für Kanal, oder simple Aktivierung, wenn Activity
    # @discord.ui.button(label="Activate", style=discord.ButtonStyle.green, custom_id='Activate_Guild_Setup', emoji="✅", row=1)
    # async def guild_setup_activate(self, interaction: discord.Interaction, button:discord.ui.Button):

    #     await interaction.response.edit_message()

    #     return