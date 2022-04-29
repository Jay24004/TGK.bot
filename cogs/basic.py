import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal
from utils.checks import Commands_Checks
import time
import datetime
class Basic(commands.Cog, name="Basic", description="General Basic Commands"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != 520830713696878592: return
        if message.author.bot and message.channel.id == 962771383996284979:
            update_channel = self.bot.get_guild(785839283847954433).get_channel(855717169584537660)
            if len(message.embeds) > 0:
                await update_channel.send(embeds=message.embeds)
            if len(message.attachments) > 0:
                await update_channel.send(attachments=message.attachments)
            if message.content:
                await update_channel.send(content=message.content)
        
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        if message.content.startswith("gk") or message.content.startswith(">") or message.content.startswith("?"):
            return
        self.bot.snipe['delete'][message.channel.id] = {'id': message.id, 'content': message.content, 'author': message.author.id}
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        if before.content.startswith("gk") or before.content.startswith(">") or before.content.startswith("?"):
            return
        self.bot.snipe['edit'][before.channel.id] = (before.content, after.content)
    
    @app_commands.command(name="ping", description="Pong!")
    @app_commands.guilds(785839283847954433)
    async def ping(self, interaction: discord.Interaction):
        start_time = time.time()
        await interaction.response.send_message("Pong!")
        end_time = time.time()

        dstart = datetime.datetime.utcnow()
        await self.bot.config.find(interaction.guild.id)
        dend = datetime.datetime.utcnow()
        dping = (dend - dstart)
        dping = dping.total_seconds()

        await interaction.edit_original_message(content=f"**Response TIme** {round(self.bot.latency * 1000)}ms\n**API**: {round((end_time - start_time) * 1000)}ms\n**Database Ping**: {round(dping * 1000)}Ms\n**Last Reboot**: <t:{round(self.bot.uptime.timestamp())}:R>")
    
    @commands.hybrid_command(name="snipe", description="Snipe the message in current channel")
    @app_commands.guilds(785839283847954433)
    @app_commands.describe(type="Select a type of snipe")
    async def snipe(self, ctx: commands.Context, type: Literal['delete', 'edit'], hidden: bool):
        if type == 'delete':
            message_data = self.bot.snipe['delete'].get(ctx.channel.id)
            if message_data is None:
                await ctx.send("No message to snipe")
                return
            message_author = self.bot.get_user(message_data['author'])
            embed = discord.Embed(color=ctx.author.color)
            embed.set_author(name=message_author.name, icon_url=message_author.avatar.url)
            embed.description = message_data['content']
            embed.set_footer(text=f"Sniped by {ctx.author}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed, ephemeral=hidden)
        
        elif type == 'edit':
            message_data = self.bot.snipe['edit'].get(ctx.channel.id)
            if message_data is None:
                await ctx.send("No message to snipe")
                return
            embed = discord.Embed(color=ctx.author.color)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
            embed.description = f"**Before:** {message_data[0]}\n**After:** {message_data[1]}"
            embed.set_footer(text=f"Sniped by {ctx.author}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed, ephemeral=hidden)

            

async def setup(bot):
    await bot.add_cog(Basic(bot))