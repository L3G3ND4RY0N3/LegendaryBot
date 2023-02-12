import discord
from discord.ext import commands

class Autoroles(commands.Cog, name="Autoroles"):
    def __innit__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        print("Autoroles.py is ready!")    

    @commands.Cog.listener()
    async def on_member_join(self, member):
        join_role1 = discord.utils.get(member.guild.roles, name="Member")
        join_role2 = discord.utils.get(member.guild.roles, name="Advanced Member")

        await member.add_roles(join_role1, join_role2)

async def setup(bot):
    await bot.add_cog(Autoroles(bot))