import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        print("Moderation.py is ready!")    




    #Delete Messages Command
    @app_commands.command(name="delete_messages", description="Delete some messages in a channel or from a member!")
    @app_commands.describe(number="The number of messages you want to delete?")
    @app_commands.describe(member="Whose messages you want to delete")
    @app_commands.describe(reason="Why is the member being kicked?")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def delete(self, interaction: discord.Interaction, number: int, member: discord.Member=None, reason: str=None):
        try:
            delete_counter = 0
            async for message in interaction.channel.history():
                if message.author == member or member == None:
                    await message.delete()
                    delete_counter += 1
                if delete_counter == number:
                    conf_embed = discord.Embed(title="Success!", color=discord.Color.red())
                    conf_embed.add_field(name="Messages deleted!", value=f"{number} messages will be removed!")
                    if reason is not None:
                        conf_embed.add_field(name="Reason", value=f"{reason}", inline=False) #if reason is not specified, dont include in embed
                    conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

                    await interaction.response.send_message(embed=conf_embed)
                    return
                    

        except discord.Forbidden:
            conf_embed = discord.Embed(color=discord.Color.yellow())
            conf_embed.add_field(name="Failure!", value=f"I am missing the permissions to delete messages ('manage messages').")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return


    ####################################################################################################################################
    ##################################################### Kick Command #################################################################
    ####################################################################################################################################

    #Kick Command
    @app_commands.command(name="kick", description="Kick a member!")
    @app_commands.describe(member="Who do you want to kick?")
    @app_commands.describe(reason="Why is the member being kicked?")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str=None):
        try:
            await member.kick()
        except discord.Forbidden:
            conf_embed = discord.Embed(color=discord.Color.yellow())
            conf_embed.add_field(name="Failure!", value=f"I am missing the permissions to kick {member.mention}.")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return

        conf_embed = discord.Embed(title="Success!", color=discord.Color.red())
        conf_embed.add_field(name="Member kicked!", value=f"{member.mention} has been kicked from the server!")
        if reason is not None:
            conf_embed.add_field(name="Reason", value=f"{reason}", inline=False) #if reason is not specified, dont include in embed
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

        await interaction.response.send_message(embed=conf_embed)

    ####################################################################################################################################
    ##################################################### Ban Command ##################################################################
    ####################################################################################################################################

    
    @app_commands.command(name="ban", description="Ban a member!")
    @app_commands.describe(member="Who do you want to ban?")
    @app_commands.describe(reason="Why is the member being banned?")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str=None):
        try:
            await member.ban()
        except discord.Forbidden:
            conf_embed = discord.Embed(color=discord.Color.yellow())
            conf_embed.add_field(name="Failure!", value=f"I am missing the permissions to ban {member.mention}.")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)
            return

        conf_embed = discord.Embed(title="Success!", color=discord.Color.red())
        conf_embed.add_field(name="Member banned!", value=f"{member.mention} has been banned from the server!")
        if reason is not None:
            conf_embed.add_field(name="Reason", value=f"{reason}", inline=False) #if reason is not specified, dont include in embed
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

        await interaction.response.send_message(embed=conf_embed)


    ####################################################################################################################################
    ################################################# Error Handeling! #################################################################
    ####################################################################################################################################



    #On command error
    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"Following error has occured: ```{error}```")
        raise error


    #Delete error, when user lacks permissions
    @delete.error
    async def delete_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="Failure!", value=f"{interaction.user}, you do not have the permissions to delete messages!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

    #Kick error, when user lacks permissions
    @kick.error
    async def kick_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="Failure!", value=f"{interaction.user}, you do not have the permissions to kick a member!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)


    #Ban error, when user lacks permissions
    @ban.error
    async def ban_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="Failure!", value=f"{interaction.user}, you do not have the permissions to ban a member!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))