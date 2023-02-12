import discord
from discord.ext import commands
from discord import app_commands
import json

class Autoroles(commands.Cog, name="Autoroles"):
    def __innit__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        print("Autoroles.py is ready!")    

    #adds the autorole to new members, so far only one role per server. 
    #TODO add more roles!
    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open("modules/Autoroles/json/autoroles.json", "r") as f:
            auto_role = json.load(f)

        join_role = discord.utils.get(member.guild.roles, name=auto_role[str(member.guild.id)])
        
        await member.add_roles(join_role)

    #Commando to add new autorole with normal prefix eg. $joinrole "roleidhere" (lame)
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def joinrole(self, ctx, role: discord.Role):
        with open("modules/Autoroles/json/autoroles.json", "r") as f:
            auto_role = json.load(f)

        auto_role[str(ctx.guild.id)] = str(role.name)

        with open("modules/Autoroles/json/autoroles.json", "w") as f:
            json.dump(auto_role, f, indent=4)

        conf_embed = discord.Embed(color=discord.Color.green())
        conf_embed.add_field(name="Success!", value=f"The automatic role for this guild/server has been set to {role.mention}.")
        conf_embed.set_footer(text=f"Action taken by {ctx.author.name}.")
        
        await ctx.send(embed=conf_embed)


    #Slash Command um eine neue Autorole hinzuzufügen :D
    @app_commands.command(name="add_autorole", description="Adds a role that is automatically assigned to a new member!")
    @app_commands.describe(role = "Select the role")
    async def add_join_role(self, interaction: discord.Interaction, role: discord.Role):
        with open("modules/Autoroles/json/autoroles.json", "r") as f:
            auto_role = json.load(f)

        auto_role[str(role.guild.id)] = {str(role.name): str(role.id)} #not working as roles cant be accessed
        
        #old singular version:
        #auto_role[str(role.guild.id)] = str(role.name)

        #new ideas
        #new_id = {str(role.name): str(role.id)}
        #auto_role.update(new_id)

        with open("modules/Autoroles/json/autoroles.json", "w") as f:
            json.dump(auto_role, f, indent=4)

        conf_embed = discord.Embed(color=discord.Color.green())
        conf_embed.add_field(name="Success!", value=f"The automatic role for this guild/server has been set to {role.mention}.")
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
        
        await interaction.response.send_message(embed=conf_embed)


    #Slash Command to remove an Autorole :D
    @app_commands.command(name="remove_autorole", description="Removes the autorole that is automatically assigned to a new member!")
    @app_commands.describe(role = "Select the role to remove")
    async def remove_join_role(self, interaction: discord.Interaction, role: discord.Role):
        with open("modules/Autoroles/json/autoroles.json", "r") as f:
            auto_role = json.load(f)

        for role in auto_role[str(role.name)]:
            del role[str(role.name)]

        with open("modules/Autoroles/json/autoroles.json", "w") as f:
            json.dumps(auto_role, f, indent=4)

        conf_embed = discord.Embed(color=discord.Color.red())
        conf_embed.add_field(name="Success!", value=f"The automatic role {role.mention} for this guild/server has been removed.")
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
        
        await interaction.response.send_message(embed=conf_embed)

async def setup(bot):
    await bot.add_cog(Autoroles(bot))