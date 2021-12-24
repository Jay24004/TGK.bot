import asyncio
import datetime
import discord
import re
from discord import user
import requests
import json

from humanfriendly import format_timespan
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from discord.ext import tasks
from typed_flags import TypedFlags

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

description = "Moderation commands"


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return round(time)


class v2Moderation(commands.Cog, description=description, command_attrs=dict(hidden=False)):
    def __init__(self, bot):
        self.bot = bot

    def is_me():
        def predicate(ctx):
            return ctx.message.author.id in [488614633670967307, 301657045248114690]
        return commands.check(predicate)

    def perm_check():
        async def predicate(ctx):
            mod_role = [785842380565774368, 803635405638991902, 799037944735727636,
                        785845265118265376, 787259553225637889, 843775369470672916]
            for mod in mod_role:
                role = discord.utils.get(ctx.guild.roles, id=mod)
                if role in ctx.author.roles:
                    permissions = await ctx.bot.config.find(role.id)
                    check = permissions['perm']
                    return (ctx.command.name in check)
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(name="uerinfo", description="Give all Infomation about user", usage="[member]", aliases=['whois'])
    @commands.check_any(perm_check(), is_me())
    async def uerinfo(self, ctx, member: discord.Member = None):
        await ctx.message.delete()

        def fomat_time(time):
            return time.strftime('%d-%B-%Y %I:%m %p')

        member = member if member else ctx.author
        usercolor = member.color

        today = (datetime.datetime.utcnow() -
                 member.created_at).total_seconds()

        embed = discord.Embed(title=f'{member.name}', color=usercolor)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name='Account Name:',
                        value=f'{member.name}', inline=False)
        embed.add_field(
            name='Created at:', value=f"{fomat_time(member.created_at)}\n{format_timespan(today)}")
        embed.add_field(name='Joined at', value=fomat_time(member.joined_at))
        embed.add_field(name='Account Status',
                        value=str(member.status).title())
        embed.add_field(name='Account Activity',
                        value=f"{str(member.activity.type).title().split('.')[1]} {member.activity.name}" if member.activity is not None else "None")

        hsorted_roles = sorted(
            [role for role in member.roles[-2:]], key=lambda x: x.position, reverse=True)

        embed.add_field(name='Top Role:', value=', '.join(
            role.mention for role in hsorted_roles), inline=False)
        embed.add_field(name='Number of Roles',
                        value=f"{len(member.roles) -1 }")
        embed.set_footer(text=f'ID {member.id}', icon_url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="flags")
    @commands.check_any(is_me())
    async def flags(self, ctx, user: discord.Member, *, args: TypedFlags):
        data = args.lower()
        await ctx.send(f'{user.name}|{args}')

    @commands.command(name="mute", description="put user in timeout", usage="[member] [time]", aliases="timeout")
    async def mute(self, ctx, user: discord.Member, time: TimeConverter):
        if int(time) > 2419200:return await ctx.send("You can't set timeout for more than 28days")
        time = datetime.datetime.utcnow() + datetime.timedelta(seconds=time)
        time = time.isoformat()
        payload = {
            "communication_disabled_until": time
            }
        headers = {
            "Authorization": f"Bot {self.bot.config_token}",
            "Content-Type": "application/json",
            }

        r = requests.patch(f'https://discord.com/api/v9/guilds/{ctx.guild.id}/members/{user.id}', data=json.dumps(payload),headers=headers)
        embed = discord.Embed(description=f"<:dynosuccess:898244185814081557> ***{user} Was Timeout***",color=0x11eca4)
        await ctx.channel.send(embed=embed)
        log_embed = discord.Embed(title=f"Mute | {user}")
        log_embed.add_field(name="User", value=user.mention)
        log_embed.add_field(name="Moderator", value=ctx.author.mention)
        channel = self.bot.get_channel(803687264110247987)
        await channel.send(embed=log_embed)

def setup(bot):
    bot.add_cog(v2Moderation(bot))
