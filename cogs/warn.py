import discord
from discord.ext import commands
from discord.ext.buttons import Paginator


class Pag(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass



class Warns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        
        if member.id in [ctx.author.id, self.bot.user.id]:
            return await ctx.send("You cannot warn yourself or the bot!")
        
        current_warn_count = len(
            await self.bot.warns.find_many_by_custom(
                {
                    "user_id": member.id,
                    "guild_id": member.guild.id
                }
            )
        ) + 1
        
        warn_filter = {"user_id": member.id, "guild_id": member.guild.id, "number": current_warn_count}
        warn_data = {"reason": reason, "timestamp": ctx.message.created_at, "warned_by": ctx.author.id}
        
        await self.bot.warns.upsert_custom(warn_filter, warn_data)
        
        embed = discord.Embed(
            title="You are being warned:",
            description=f"__**Reason**__:\n{reason}",
            colour=discord.Colour.red(),
            timestamp=ctx.message.created_at
        )
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f"Warn: {current_warn_count}")
        
        try:
            await member.send(f"You Have been Warned | {reason}\nWarns: {current_warn_count}")
            em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been warned.**\nWarnings Count: {current_warn_count}")
            await ctx.send(embed=em)
        except discord.HTTPException:
            emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **Warning Logged For {member.name}  I couldn't DM them.** Warnings Count: {current_warn_count}")
            await ctx.send(embed=emb)

        log_channel = self.bot.get_channel(827245906331566180)

        embed = discord.Embed(title=f"Warn | {member.name}")
        embed.add_field(name="User", value=f"{member.mention}")
        embed.add_field(name="Moderator", value=f"{ctx.author.mention}")
        embed.add_field(name="Reason", value=f"{reason}")
        embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

        await channel.send(embed=embed)
            
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member):
        warn_filter = {"user_id": member.id, "guild_id": member.guild.id}
        warns = await self.bot.warns.find_many_by_custom(warn_filter)
        
        if not bool(warns):
            return await ctx.send(f"Couldn't find any warns for: `{member.display_name}`")
        
        warns = sorted(warns, key=lambda x: x["number"])
        
        pages = []
        for warn in warns:
            description = f"""
            Warn Number: `{warn['number']}`
            Warn Reason: `{warn['reason']}`
            Warned By: <@{warn['warned_by']}>
            Warn Number: {warn['timestamp'].strftime("%I:%M %p %B %d, %Y")}
            """
            pages.append(description)
        
        await Pag(
            title=f"Warns for `{member.display_name}`",
            colour=0xCE2029,
            entries=pages,
            length=1
        ).start(ctx)


def setup(bot):
    bot.add_cog(Warns(bot))