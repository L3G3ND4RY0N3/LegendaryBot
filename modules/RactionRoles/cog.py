import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import create_reaction_role_setup_embed
from utils.views.ReactionRoleSetupView import ReactionRoleSetupSetupView
from utils import settings

logger=settings.logging.getLogger("discord")

class ReactionRoles(commands.Cog, name="RactionRoles"):
    def __init__(self, bot: discord.Client):
        self.bot = bot

#region events
####################### events #######################################################################################
    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!") 
#endregion

#region commands
################################ commands #######################################################################################
    @app_commands.command(name="reaction_roles_setup", description="Set up reaction roles for this guild.")
    @app_commands.describe(channel="The channel where the reaction roles message will be sent.")
    @app_commands.checks.has_permissions(administrator=True)
    async def reaction_roples_setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        embed = create_reaction_role_setup_embed(interaction.guild)
        interaction.guild.emojis
        await interaction.response.send_message(embed=embed, view=ReactionRoleSetupSetupView(self.bot, interaction.guild.id, interaction.guild.roles, channel))

#endregion

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))