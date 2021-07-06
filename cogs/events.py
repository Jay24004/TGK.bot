import datetime
import discord

from discord_slash import cog_ext, SlashContext, cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice, create_permission
from discord_slash.model import SlashCommandPermissionType

from discord.ext import commands, tasks
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType

class Events(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.update_task = self.check_update_task.start()

    @tasks.loop(seconds=3600)
    async def check_update_task(self):

        self.bot.blacklist_user = {}
        current_blacklist_user = await self.bot.blacklist.get_all()
        for blacklisted_user in current_blacklist_user:
            self.bot.blacklist_user[blacklisted_user["_id"]] = blacklisted_user

        self.bot.muted_users = {}
        currentMutes = await self.bot.mutes.get_all()
        for mute in currentMutes:
            self.bot.muted_users[mute["_id"]] = mute

        self.bot.ban_users = {}
        currentBans = await self.bot.bans.get_all()
        for ban in currentBans:
            self.bot.ban_users[ban["_id"]] = ban

        self.bot.free_users = {}
        currentFree = await self.bot.free.get_all()
        for free in currentFree:
            self.bot.free_users[ban["_id"]] = free

    @check_update_task.before_loop
    async def before_check_current_free(self):
        await self.bot.wait_until_ready()


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, ex):
        if isinstance(ex, commands.MissingPermissions):
            await ctx.send("Hey! You lack permission to use this command.")
        elif isinstance(ex, commands.MissingAnyRole):
            await ctx.send("Hey! You lack permission to use this command.")
        else:
            embed = discord.Embed(color=0xE74C3C, 
                description=f"Error: `{ex}`")
            await ctx.send(embed=embed)

    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignore these errors
        if isinstance(error, commands.CommandOnCooldown):
            # If the command is currently on cooldown trip this
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            if int(h) == 0 and int(m) == 0:
                await ctx.send(f" You must wait {int(s)} seconds to use this command!")
            elif int(h) == 0 and int(m) != 0:
                await ctx.send(
                    f" You must wait {int(m)} minutes and {int(s)} seconds to use this command!"
                )
            else:
                await ctx.send(
                    f" You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!"
                )
        elif isinstance(error, commands.CheckFailure):
            # If the command has failed a check, trip this
            await ctx.send("Hey! You lack permission to use this command.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send('The command is disabed by Owner')
        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send('Please Wait for last Game to End')
        elif isinstance(error, commands.CommandInvokeError):
            return
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            #raise error
            embed = discord.Embed(color=0xE74C3C, 
                description=f"<:dnd:840490624670892063> | Error: `{error}`")
            await ctx.send(embed=embed)
            #mess = await ctx.send_help(ctx.command, )      
    
    @commands.Cog.listener()
    async def on_message(self, message):
        word_list = ['vote link','vote Link','Vote link', 'pls vote', 'pls Vote', 'Pls vote']
        components = [
            [
                Button(style=ButtonStyle.URL, label="Vote Here", url="https://top.gg/servers/785839283847954433/vote"),
            ]
        ]
        if message.author.bot:
            return

        messageContent = message.content.lower()
        if len(messageContent) > 0:
            for word in word_list:
                if word in messageContent:
                    return await message.reply('__**Voting Perks**__\n❥ Special "Voted" Role.\n❥ 2,500 Casino Cash. Collect using ,collectincome in #:game_die:。casino.\n❥ Access to Dank Memer Premium with 2x Amaari.\n❥ Guild wide 1x Amaari.\n\n', mention_author=False, components=components)

            for word in ['when heist', 'where heist', 'heist when', 'where is the heist']:
                if word in messageContent:
                    return await message.reply('We have daily heist in <#804708111301738576>, and heists for special requirements and occasions in <#812992825801179136>', delete_after=30)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        #if guild.id != 785839283847954433:
            #return
        logs = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
        channel = self.bot.get_channel(806107399005667349)
        logs = logs[0]
        if logs.user.id == 816699167824281621:
            return
        if logs.target == member:
            data = await self.bot.config.find(guild.id)
            if data is None:
                return
            if logs.reason is None:
                logs.reason = "None"
            log_channel = self.bot.get_channel(855784930494775296)
            log_embed = discord.Embed(title=f"🔨 Ban | Case ID: {data['case']}",
                description=f" **Offender**: {logs.target.name} | {logs.target.mention} \n**Reason**: {logs.reason}\n **Moderator**: {logs.user.name} {logs.user.mention}", color=0xE74C3C)
            log_embed.set_thumbnail(url=member.avatar_url)
            log_embed.timestamp = datetime.datetime.utcnow()
            log_embed.set_footer(text=f"ID: {member.id}")

            await log_channel.send(embed=log_embed)

            data["case"] += 1
            await self.bot.config.upsert(data)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        #if guild.id != 785839283847954433:
            #return
        log = await guild.audit_logs(limit=1, action=discord.AuditLogAction.unban).flatten()
        channel = self.bot.get_channel(806107399005667349)
        logs = log[0]
        data = await self.bot.config.find(guild.id)

        if logs.user.id == 816699167824281621:
            return
        if logs.target == member:
            data = await self.bot.config.find(guild.id)
            if data is None:
                return
            if logs.reason is None:
                logs.reason = "None"
            log_channel = self.bot.get_channel(855784930494775296)
            log_embed = discord.Embed(title=f"🔓 UnBan | Case ID: {data['case']}",
                description=f" **Offender**: {logs.target.name} | {logs.target.mention} \n**Reason**: {logs.reason}\n **Moderator**: {logs.user.name} {logs.user.mention}", color=0x2ECC71)
            log_embed.set_thumbnail(url=member.avatar_url)
            log_embed.timestamp = datetime.datetime.utcnow()
            log_embed.set_footer(text=f"ID: {member.id}")

            await log_channel.send(embed=log_embed)

            data["case"] += 1
            await self.bot.config.upsert(data)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild 
    
        if member.guild.id != 785839283847954433:
            return
        data = await self.bot.config.find(guild.id)
        if data is None:
            return

        channel =  self.bot.get_channel(data["welcome"])
        robot = discord.utils.get(guild.roles, id=810153515610537994)
        count = guild.member_count
        ping = discord.utils.get(guild.roles, id=810400876657115166)
        level = discord.utils.get(guild.roles, id=810132828250832948)
        game = discord.utils.get(guild.roles, id=810135369177759774)
        dono = discord.utils.get(guild.roles, id=810134737829888050)
        special = discord.utils.get(guild.roles, id=810134311163920404)
    
        embed = discord.Embed(title=f'**WELCOME TO TGK, {member.display_name}!**',
            description=f"\n\nGet your favorite roles from [self-roles](https://discord.gg/58bc5QWE4q),\nand say _Hello_ to everyone in [chat](https://discord.gg/yEPYYDZ3dD)!\n\nAlso check out other fun game bots on the server:\n✦ [Casino](https://discord.gg/DJycdCqnqt) ✦ [Mudae](https://discord.gg/ujCHVRctHY) ✦ [Akinator](https://discord.gg/fzDTdGZFh6) ✦ [Pokemon](https://discord.gg/DpJ4mAUC9m)\n\nMake sure you follow the [rules](https://discord.gg/NmD4JGCaNc) of the house for a good time here. Also, check out rules and instructions of game bots in respective channels.\n\n:love_letter: To get in touch with staff, simply raise a ticket from [support](https://discord.gg/T8VWyvDfeB).\n\nHave fun!\n\n__Server Member Count:__ {guild.member_count - len([m for m in guild.members if m.bot])}",
            color=0x000000)
        embed.set_thumbnail(url=member.avatar_url)
        await channel.send(f"{member.mention}", embed=embed)
        await member.add_roles(ping)
        await member.add_roles(level)
        await member.add_roles(game)
        await member.add_roles(dono)
        await member.add_roles(special)

        try:
            await member.send(embed=embed)
        except discord.HTTPException:
            pass
    

    @commands.command(name="joint", hidden=True)
    @commands.has_any_role(785842380565774368,799037944735727636)
    async def joint(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f'**WELCOME TO TGK, {ctx.author.display_name}!**',
            description=f"\n\nGet your favorite roles from [self-roles](https://discord.gg/58bc5QWE4q),\nand say _Hello_ to everyone in [chat](https://discord.gg/yEPYYDZ3dD)!\n\nAlso check out other fun game bots on the server:\n✦ [Casino](https://discord.gg/DJycdCqnqt) ✦ [Mudae](https://discord.gg/ujCHVRctHY) ✦ [Akinator](https://discord.gg/fzDTdGZFh6) ✦ [Pokemon](https://discord.gg/DpJ4mAUC9m)\n\nMake sure you follow the [rules](https://discord.gg/NmD4JGCaNc) of the house for a good time here. Also, check out rules and instructions of game bots in respective channels.\n\n:love_letter: To get in touch with staff, simply raise a ticket from [support](https://discord.gg/T8VWyvDfeB).\n\nHave fun!\n\n__Server Member Count:__ {guild.member_count - len([m for m in guild.members if m.bot])}",
            color=0x2ECC71)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Events(bot))