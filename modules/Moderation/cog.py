import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog, name="Moderation"):
    def __innit__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        print("Moderation.py is ready!")    

    @app_commands.command(name="kick", description="Kick a member!")
    @app_commands.describe(member="Who do you want to kick?")
    async def kick(self, interaction: discord.Interaction, member: discord.Member):
        try:
            await member.kick()
        except discord.Forbidden:
            conf_embed = discord.Embed(color=discord.Color.yellow())
            conf_embed.add_field(name="Failure!", value=f"I am missing the permissions to kick {member.mention}.")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return

        conf_embed = discord.Embed(color=discord.Color.red())
        conf_embed.add_field(name="Member kicked!", value=f"{member.mention} has been kicked from the server!.")
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

        await interaction.response.send_message(embed=conf_embed)

    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"Following error has occured: ```{error}```")
        raise error


async def setup(bot):
    await bot.add_cog(Moderation(bot))