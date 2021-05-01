import re
import datetime
from copy import deepcopy
from discord.ext.buttons import Paginator
import asyncio
import discord
from discord.ext import commands, tasks
from dateutil.relativedelta import relativedelta

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

def comman_ping(role1, role2):
    ping1 = set(role1)
    ping2 = set(role2)

    if len(ping1.intersection(ping2)) > 0:
        return(ping1.intersection(ping2))  
    else:
        return("no common elements")

def fomat_time(time):
  return time.strftime('%d-%B-%Y %I:%m %p')

class roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    #geting All Info mantions
    @commands.command(name="roleinfo", description="members with this role", usage="[role.id]")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def roleinfo(self, ctx, *,role: discord.Role=None):
        if role == None:
            return await ctx.send("Looks like you forget to add role")

        if role == int:

            role = discord.utils.get(ctx.guild.roles, id=role)
        else:
            role = discord.utils.get(ctx.guild.roles, name=f"{role}")

        await ctx.message.delete()

        role_color = role.color
        embed = discord.Embed(title=f"Role Infomation for {role.name}", color=role_color)
        embed.add_field(name=f"Name:", value=f"{role.name}")
        embed.add_field(name=f"Members:", value=f"{len(role.members)}", inline=False)
        embed.add_field(name=f"Created At", value=fomat_time(role.created_at))
        embed.add_field(name=f"color", value=f"{role.color}", inline=False)
        embed.set_footer(text=f"ID {role.id}")

        await ctx.send(embed=embed, delete_after=60)
        
    #Added Roel/Remove to any User
    @commands.command(name="role", description="add Role fored user", usage="[member][role]")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376)
    async def role(self, ctx, member:discord.Member, *,role: discord.Role):
        if role == None:
            return await ctx.send("Looks like you forget to add role")

        if role == int:

            role = discord.utils.get(ctx.guild.roles, id=role)
        else:
            role = discord.utils.get(ctx.guild.roles, name=f"{role}")


        if role >= ctx.author.top_role:
            return await ctx.send("You can't You cannot do this action due to role hierarchy.")
        
        roles = member.roles
        await ctx.message.delete()
        if role in roles:
            await member.remove_roles(role)
            embed = discord.Embed(description=f"<:allow:819194696874197004> | Removed {role} from {member}")
            await ctx.send(embed=embed)
        else:
            await member.add_roles(role)
            embed = discord.Embed(description=f"<:allow:819194696874197004> | Added {role} from {member}")
            await ctx.send(embed=embed)

   
    #some Important roles members count 
    @commands.command(name="Pings", description="Give numbers of some the pings roles", usage="")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889, 831405039830564875)
    async def pings(self, ctx):
        await ctx.message.delete()

        heist = discord.utils.get(ctx.guild.roles, id=804068344612913163 )
        partner_heist = discord.utils.get(ctx.guild.roles, id=804069957528584212)
        giveaway = discord.utils.get(ctx.guild.roles, id=800685251276963861)
        othere_heist = discord.utils.get(ctx.guild.roles, id=806795854475165736)
        danker = discord.utils.get(ctx.guild.roles, id=801392998465404958)
        partnership = discord.utils.get(ctx.guild.roles, id=797448080223109120)

        embed = discord.Embed(title=f"Showing some pings counts",
            description=f"{heist.mention} = {len(heist.members)}\n-----\n{partner_heist.mention} = {len(partner_heist.members)}\n-----\n{othere_heist.mention} = {len(othere_heist.members)}\n-----\n{danker.mention} = {len(danker.members)}\n-----\n{partnership.mention} = {len(partnership.members)}\n-----\n{giveaway.mention} = {len(giveaway.members)}", color=0x06f79e)

        await ctx.send(embed=embed, delete_after=60)

    #getting Mutual Pings 
    @commands.command(name="mping", description="Mutual Pings for tow role", usage="[role 1] [role 2]", hidden=True)
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889, 831405039830564875)
    async def mping(self, ctx, role1: discord.Role, role2: discord.Role):
        pings1 = role1.members
        pings2 = role2.members

        if role1 == role2:
            return await ctx.send("you can't use same role for mutual pings")

        embed= discord.Embed(title="Mutual Pings", color=0xF1C40F,
            description=f"Showing Mutual pings for the two Role\n1.Role {role1.mention} total members: {len(pings1)}\n2.Role{role2.mention} total members: {len(pings2)}\n\n**Unique Members are: {int(len(pings1) + len(pings2) - len(comman_ping(pings1, pings2)))}**")#(comman_ping(pings1, pings2))

        await ctx.send(embed=embed)

    #Verify Command when Carl is down
    @commands.command(name="verify", description="Very Your self in Server", usage="[]", hidden=True)
    async def verify(self, ctx):
        if ctx.channel.id == 812906607301099520:

            role = discord.utils.get(ctx.guild.roles, id=787566421592899614)

            await ctx.author.add_roles(role)

            await ctx.message.delete()


def setup(bot):
    bot.add_cog(roles(bot))

"""
 @commands.command(name="temprole", description="add the Temp role to user", usage="[member] [role.id]")
    @commands.has_any_role(785842380565774368, 799037944735727636, 785845265118265376)
    async def temprole(self, ctx, member: discord.Member, role: discord.Role, *, time: TimeConverter=None):
        await ctx.message.delete()
        
        data = {
            '_id': member.id,
            'temp_role': role.name,
            'temp_roledAt': datetime.datetime.now(),
            'temp_roleDuration': time,
            'temptedBy': ctx.author.id,
            'guildId': ctx.guild.id,
        }
        await self.bot.temp_roles.upsert(data)
        self.bot.temp_roled_users[member.id] = data

        await member.add_roles(role)

        if time and time < 30:
            await asyncio.sleep(time)

            if role in member.role:
                await member.remove_roles(role)

            await self.bot.temp_roles.delete(member.id)
            try:
                self.bot.temp_roled_users.pop(member.id)
            except  KeyError:
                pass
"""
"""
Taskks 
"""
"""
        self.temp_role_task = self.check_current_temp_roles.start()

        def cog_unload(self):
            self.temp_role_task.cancel()

    @tasks.loop(minutes=5)
    async def check_current_temp_roles(self):
        currentTime = datetime.datetime.now()
        temp_roles = deepcopy(self.bot.temp_roled_users)
        for key, value in temp_roles.items():
            if value['temp_roleDuration'] is None:
                continue

            untemp_roleTime = value['temp_roledAt'] + relativedelta(seconds=value['temp_roleDuration'])

            if currentTime >= untemp_roleTime:
                guild = self.bot.get_guild(value['guildId'])
                member = guild.get_member(value['_id'])

                role = discord.utils.get(guild.roles, name=f"{value['temp_role']}")
                if role in member.roles:
                    await member.remove_roles(role)
                    print(f"Untemp_roled: {member.display_name}")

                await self.bot.temp_roles.delete(member.id)
                try:
                    self.bot.temp_roled_users.pop(member.id)
                except KeyError:
                    pass

    @check_current_temp_roles.before_loop
    async def before_check_current_temp_roles(self):
        await self.bot.wait_until_ready()
"""
