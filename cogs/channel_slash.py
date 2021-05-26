import random

import discord

from discord.ext import commands
from discord_slash import SlashContext
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_choice
from discord_slash.utils.manage_commands import create_option

description="Channel Management Slash Commands "
guild_ids = [797920317871357972, 785839283847954433]

class channel_slash(commands.Cog, description=description):
    def __init__(self, bot):
        self.bot = bot

    def is_me():
        def predicate(ctx):
            return ctx.author.id == 488614633670967307
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @cog_ext.cog_slash(name="lock",
        description="Lock channel for Role",
        guild_ids=guild_ids,
        options=[
        create_option(
            name="role",
            description="Role you want to lock",
            required=False,
            option_type=8
            ),
        create_option(
            name="channel",
            description="channel You want to lock",
            required=False,
            option_type=7
            )
        ]
    )
    @commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889), is_me())
    async def lock(self, ctx, role: str=None, channel: str=None):
        role = role if role else ctx.guild.default_role
        channel = channel if channel else ctx.channel

        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = False

        await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(color=0x02ff06, description=f'The `{channel.name}` is Lock for `{role.name}`')
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="unlock",
        description="Unlock channel for Role",
        guild_ids=guild_ids,
        options=[
        create_option(
            name="role",
            description="Role you want to Unlock",
            required=False,
            option_type=8
            ),
        create_option(
            name="channel",
            description="channel You want to Unlock",
            required=False,
            option_type=7
            ),
        create_option(
            name="unlock_type",
            description="Role unlock Type",
            required=False,
            option_type=5,
            )
        ]
    )

    @commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889), is_me())
    async def unlock(self, ctx, role=None, channel=None,unlock_type=None):
        unlock_type = unlock_type if unlock_type else None
        role = role if role else ctx.guild.default_role
        channel = channel if channel else ctx.channel

        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = unlock_type

        await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(color=0x02ff06, description=f'The `{channel.mention}` is Unloock for `{role.name}`')
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
    name="slowmode", description="Set Slowmode In Current Channel",
    guild_ids=guild_ids,
    options=[
        create_option(
            name="time",
            description="Slowmode Time max 6h",
            option_type=3,
            required=True)
        ]
    )
    @commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889), is_me())
    async def slowmode(self, ctx, time: str = '0'):

        unit = ['h', 'H', 'm', 'M', 's', 'S']

        cd = 0
        if time[-1] in unit:
            unit = time[-1]
            cd = int(time[:-1])
            if unit == 'h' or unit == 'H':
                cd = cd * 60 * 60
            elif unit == 'm' or unit == 'M':
                cd = cd * 60
            else:
                cd = cd
        else:
            cd = int(time) if time else 0


        if cd > 21600:
            await ctx.send(f"Slowmode interval can't be greater than 6 hours.")
        elif cd == 0:
            await ctx.channel.edit(slowmode_delay=cd)
            await ctx.send(f"Slowmode has been removed!! 🎉")
        else:
            await ctx.channel.edit(slowmode_delay=cd)
            if unit == 'h' or unit == 'H':
                await ctx.send(f'Slowmode interval is now **{int(cd/3600)} hours**.')
            elif unit == 'm' or unit == 'M':
                await ctx.send(f'Slowmode interval is now **{int(cd/60)} mins**.')
            else:
                await ctx.send(f'Slowmode interval is now **{cd} secs**.')

    @cog_ext.cog_slash(name="Hide",
        description="Hide Channels For mentioned Role",
        guild_ids=guild_ids,
        options=[
            create_option(
                name="role",
                description="Role you want to hide channel",
                option_type=8,
                required=False
                ),
            create_option(
                name="channel",
                description="Channel you want to hide",
                option_type=7,
                required=False
                )
            ]
    )
    @commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376), is_me())
    async def hide(self, ctx, role=None, channel=None):
        channel = channel if channel else ctx.channel
        role = role if role else ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = False
        await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(
            color=0x02ff06, description=f'The {channel.name} is Now hidded for for {role.name}')
        await ctx.send(embed=embed)


    @cog_ext.cog_slash(name="UnHide",
        description="UnHide Channels For mentioned Role",
        guild_ids=guild_ids,
        options=[
            create_option(
                name="role",
                description="Role you want to Unhide channel",
                option_type=8,
                required=False
                ),
            create_option(
                name="channel",
                description="Channel you want to Unhide",
                option_type=7,
                required=False
                )
            ]
    )
    @commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376), is_me())
    async def Unhide(self, ctx, role=None, channel=None):
        channel = channel if channel else ctx.channel
        role = role if role else ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = None
        await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(
            color=0x02ff06, description=f'The {channel.name} is Now Visible for for {role.name}')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(channel_slash(bot))


"""
@commands.command(name="lockdown", description="Put Server in lockdown", usage="")
    @commands.has_permissions(ban_members=True)
    async def lockdown(self, ctx, *,reason=None):
        role = ctx.guild.default_role
        permissions = discord.PermissionOverwrite()
        PermissionOverwrite.update(send_messages = False)

        await role.edit(reason=reason, permissions=permissions)
        await ctx.send("Server LOck")

    @commands.command(name="server_unlock", description="Unlock Server from lockdown", usage="")
    @commands.has_permissions(ban_members=True)
    async def server_unlock(self, ctx, *,reason= None):
        role = ctx.guild.default_role
        permissions = discord.PermissionOverwrite()
        PermissionOverwrite.update(send_messages = True)

        await role.edit(reason=reason, permissions=permissions)

        await ctx.send("Server UnLock")
"""