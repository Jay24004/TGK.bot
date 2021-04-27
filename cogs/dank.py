import random
import asyncio
import discord
from discord.ext import commands
from discord.ext.buttons import Paginator



class dank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def our_custom_check():
        async def predicate(ctx):
            return ctx.guild is not None \
                and ctx.author.guild_permissions.manage_channels \
                and ctx.me.guild_permissions.manage_channels
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(
        name="dankdown",
        description="Use this commands when dank is down",
        usage="")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def dankdown(self, ctx):
        async with ctx.typing():
            role = ctx.guild.default_role

            dank_1 = self.bot.get_channel(799364834927968336)
            dank_2 = self.bot.get_channel(799378297855279125)
            dank_pre = self.bot.get_channel(812724720675061770)
            dank_vip = self.bot.get_channel(822409174271918120)

            override_dank_1 = dank_1.overwrites_for(role)
            override_dank_1.send_messages = False

            override_dank_2 = dank_2.overwrites_for(role)
            override_dank_2.send_messages = False

            override_dank_pre = dank_pre.overwrites_for(role)
            override_dank_pre.send_messages = False

            override_dank_vip = dank_vip.overwrites_for(role)
            override_dank_vip.send_messages = False

            await dank_1.set_permissions(role, overwrite=override_dank_1)
            await dank_2.set_permissions(role, overwrite=override_dank_2)
            await dank_pre.set_permissions(role, overwrite=override_dank_pre)
            await dank_vip.set_permissions(role, overwrite=override_dank_vip)

            embed = discord.Embed(
                title="Dank is Down",
                color=0xff0000,
                description="The Dank memer is Down in mean time head to the <#785847439579676672> and chat with other"
            )

            await dank_1.send(embed=embed)
            await dank_2.send(embed=embed)
            await dank_pre.send(embed=embed)
            await dank_vip.send(embed=embed)

        await ctx.send("Dank is LockedUp")


    @commands.command(
        name="dankup",
        description="Use this commands when dank is Comes Back",
        usage="")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def dankup(self, ctx):
        async with ctx.typing():
            role = ctx.guild.default_role

            dank_1 = self.bot.get_channel(799364834927968336)
            dank_2 = self.bot.get_channel(799378297855279125)
            dank_pre = self.bot.get_channel(812724720675061770)
            dank_vip = self.bot.get_channel(822409174271918120)

            override_dank_1 = dank_1.overwrites_for(role)
            override_dank_1.send_messages = None

            override_dank_2 = dank_2.overwrites_for(role)
            override_dank_2.send_messages = None

            override_dank_pre = dank_pre.overwrites_for(role)
            override_dank_pre.send_messages = None

            override_dank_vip = dank_vip.overwrites_for(role)
            override_dank_vip.send_messages = None

            await dank_1.set_permissions(role, overwrite=override_dank_1)
            await dank_2.set_permissions(role, overwrite=override_dank_2)
            await dank_pre.set_permissions(role, overwrite=override_dank_pre)
            await dank_vip.set_permissions(role, overwrite=override_dank_vip)
        
            await dank_1.purge(limit=1)
            await dank_2.purge(limit=1)
            await dank_pre.purge(limit=1)
            await dank_vip.purge(limit=1)

            embed = discord.Embed(
                title="Dank is Back",
                color=0xff0000,
                description="The Dank memer is Back to Grinding"
            )

            await dank_1.send(embed=embed)
            await dank_2.send(embed=embed)
            await dank_pre.send(embed=embed)
            await dank_vip.send(embed=embed)

        await ctx.send("Dank is unlocked")

        



def setup(bot):
    bot.add_cog(dank(bot))
