import random
import asyncio
import datetime
import discord
from discord.ext import commands
from discord.ext.buttons import Paginator

class Pag(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass

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



async def GetMessage(
    bot, ctx, contentOne="Default Message", contentTwo="\uFEFF", timeout=100
):
    """
    This function sends an embed containing the params and then waits for a message to return
    Params:
     - bot (commands.Bot object) :
     - ctx (context object) : Used for sending msgs n stuff
     - Optional Params:
        - contentOne (string) : Embed title
        - contentTwo (string) : Embed description
        - timeout (int) : Timeout for wait_for
    Returns:
     - msg.content (string) : If a message is detected, the content will be returned
    or
     - False (bool) : If a timeout occurs
    """
    embed = discord.Embed(title=f"{contentOne}", description=f"{contentTwo}",)
    sent = await ctx.send(embed=embed)
    try:
        msg = await bot.wait_for(
            "message",
            timeout=timeout,
            check=lambda message: message.author == ctx.author
            and message.channel == ctx.channel,
        )
        if msg:
            return msg.content
    except asyncio.TimeoutError:
        return False
counter = 0

class ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
   
    @commands.command(name="Support", description="make an Support ticket for user", usage="")
    @commands.cooldown(3, 86400, commands.BucketType.user)
    async def support(self, ctx):
        if ctx.channel.id == 830493297407164426:
            async with ctx.typing():
                member = ctx.author
                guild = ctx.guild

                channel = await guild.create_text_channel(category=self.bot.get_channel(829230513516445736), sync_permissions=True, name=f"{ctx.author.name} ticket", topic=f"{ctx.author.id}")
                overwrites = channel.overwrites_for(member)
                overwrites.send_messages = True
                overwrites.view_channel = True
                
                embed = discord.Embed(title=f"{ctx.author.display_name} Welcome to Your Support ticket",
                    color=0x008000,
                    description="Welcome to the Server Support. Mention any of the online staff only once and and please be patient until they approach you.")

                current_ticket_count = len(
                    await self.bot.ticket.find_many_by_custom(
                        {
                            "user_id": ctx.author.id,
                            "guild_id": member.guild.id
                        }
                    )
                ) + 1

                ticket_filter = {"user_id": ctx.author.id, "guild_id": ctx.guild.id, "ticket_number": current_ticket_count}
                ticket_data = {"ticket_id": channel.id, "timestamp": datetime.datetime.now()}

                await self.bot.ticket.upsert_custom(ticket_filter, ticket_data)

                await channel.edit(name=f"{ctx.author.display_name} ticket {current_ticket_count}")
                await channel.set_permissions(member, view_channel=True, send_messages=True)

            await channel.send(f"{ctx.author.mention}", embed=embed)
            await ctx.message.delete()
        else:
            return

    @commands.command(name="close", description="close The ticket", usage="")
    async def close(self, ctx):
        if ctx.channel.category.id == 829230513516445736:
            if ctx.channel.permissions_synced:
                await ctx.send("ticket Is Closed already")
            else:
                await ctx.channel.edit(sync_permissions=True)
                await ctx.channel.edit(name=f"{ctx.channel.name} Closed")
                await ctx.send("ticket Close")
        else:
            await ctx.send("You can't use this command here")

    @commands.command(name="open", description="delete current ticket", usage="")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def open(self, ctx):
        ticket_filter= {"ticket_id": ctx.channel.id," guild_id": ctx.guild.id}
        tickets = await self.bot.ticket.find_many_by_custom(ticket_filter)
        
        if not bool(ticket):
            return

        await self.bot.ticket.find_one()


        await ctx.send(f"{tickets}, {member}")
    @commands.command(name="delete", description="delete the ticket", usage="")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def delete(self, ctx):
        channel = ctx.channel
        async with ctx.typing():
            if ctx.channel.category.id == 829230513516445736:
                await ctx.send("Are Your sure?[Y/N]")
                try:

                    await self.bot.wait_for("message", check=lambda m: m.content.startswith(f"Y"), timeout=3600)
                    embed_delete = discord.Embed(description="``Deleting this ticket in 10 seconds``")
                    await ctx.send(embed=embed_delete)
                    ticket_filter = {"ticket_id": channel.id}

                    await self.bot.ticket.delete_by_custom(ticket_filter)
                    await asyncio.sleep(10)
                    await channel.delete()
                except asyncio.TimeoutError:
                    embed = discord.Embed(description="``Time out canceling the cancel ``")
                    await ctx.send(embed=embed)

    @commands.command(name="adduser", description="add User to the channel", usage="[member] [channel]")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def adduser(self, ctx, member: discord.User=None, channel: discord.TextChannel=None):
        channel = channel if channel else ctx.channel
        if ctx.channel.category.id == 829230513516445736:

            if member == ctx.author:
                await ctx.send("you use command on your self")

            overwrite = channel.overwrites_for(member)
            overwrite.view_channel = True
            overwrite.send_messages = True

            await channel.set_permissions(member, overwrite=overwrite)

            embed = discord.Embed(
                color=0x02ff06,
                description=f"The User {member.mention} Is added to the Channel"
                )
            await ctx.message.delete()
            await ctx.send(embed=embed)


    @commands.command(name="removeuser", description="Remove User to the channel", usage="[member] [channel]")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def removeuser(self, ctx, member:discord.Member, channel: discord.TextChannel=None):
        channel = channel if channel else ctx.channel
        if ctx.channel.category.id == 829230513516445736:

            if member == ctx.author:
                await ctx.send("you use command on your self")

            overwrite = channel.overwrites_for(member)
            overwrite.view_channel = False
            overwrite.send_messages = False

            await channel.set_permissions(member, overwrite=overwrite)

            embed = discord.Embed(
                color=0x02ff06,
                description=f"The User {member.mention} Is Remove from the Channel"
                )
            await ctx.message.delete()
            await ctx.send(embed=embed)

    @commands.command(name="addrole", description="add User to the channel", usage="[member] [channel]")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def addrole(self, ctx, role: discord.Role, channel: discord.TextChannel=None):
        channel = channel if channel else ctx.channel
        if ctx.channel.category.id == 829230513516445736:

            if role == None or ctx.guild.default_role:
                return await ctx.send("you need to enter role mention/id or u can't add this role")

            overwrite = channel.overwrites_for(role)
            overwrite.view_channel = True
            overwrite.send_messages = True

            await channel.set_permissions(role, overwrite=overwrite)

            embed = discord.Embed(
                color=0x02ff06,
                description=f"The Role {role.mention} Is added to the Channel"
                )
            await ctx.message.delete()
            await ctx.send(embed=embed)

    @commands.command(name="removerole", description="Remove User to the channel", usage="[Role.id/mention] [channel]", aliases=["removr"])
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def removerole(self, ctx, role:discord.Role, channel: discord.TextChannel=None):
        channel = channel if channel else ctx.channel
        if ctx.channel.category.id == 829230513516445736:

            if role == None:
                await ctx.send("you need to enter role mention/id")

            overwrite = channel.overwrites_for(role)
            overwrite.view_channel = False
            overwrite.send_messages = False

            await channel.set_permissions(role, overwrite=overwrite)

            embed = discord.Embed(
                color=0x02ff06,
                description=f"The Role {role.mention} Is Remove from the Channel"
                )
            await ctx.message.delete()
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ticket(bot))