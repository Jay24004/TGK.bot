import discord
from copy import deepcopy
from discord.ext import commands, tasks
import datetime
import asyncio
from humanfriendly import format_timespan
import time

description = "an Freeload Banning Class"

class freeloader(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.free_task = self.check_current_free.start()

	def is_me():
	    def predicate(ctx):
	        return ctx.message.author.id in [488614633670967307 , 301657045248114690]
	    return commands.check(predicate)

	def perm_check():
	    async def predicate(ctx):
	        mod_role = [785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889, 843775369470672916]
	        for mod in mod_role:
	            role = discord.utils.get(ctx.guild.roles, id=mod)
	            if role in ctx.author.roles:
	                permissions = await ctx.bot.config.find(role.id)
	                check = permissions['perm']
	                return (ctx.command.name in check)
	    return commands.check(predicate)

	@tasks.loop(seconds=10)
	async def check_current_free(self):
	    currentTime = datetime.datetime.now()
	    frees = deepcopy(self.bot.free_users)
	    for key, value in frees.items():
	        if value['time'] is None:
	            continue

	        time = value['time']
	        removeTime = (currentTime - time)
	        removeTime = removeTime.total_seconds()


	        if removeTime >= 1209600:
	        	await self.bot.free.delete(value['_id'])
	        	try:
	        		self.bot.free_users.pop(value['_id'])
	        	except KeyError:
	        		pass

	@check_current_free.before_loop
	async def before_check_current_free(self):
	    await self.bot.wait_until_ready()


	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.__class__.__name__} Cog has been loaded\n-----")

	@commands.Cog.listener()
	async def on_member_join(self, member):
		if member.guild.id != 785839283847954433:
			return

		if member.id == 391913988461559809:
			await member.guild.kick(member)
		guild = self.bot.get_guild(785839283847954433)
		data = await self.bot.free.find(member.id)
		if data is None:
			return

		ban = {"_id": member.id,
				"BanedBy": data['BanedBy'],
				"guildId": data['guildId'],
				"BanDuration": 50400
		}
		#await self.bot.bans.upsert(ban)
		#await self.bot.free.delete(member.id)
		try:
			than = data['time']
			now = datetime.datetime.utcnow()
			newtime = (now - than)
			total_s = newtime.total_seconds()

			await member.send(f"You Have Been Found Doing Freloading on this Server at {than.strftime('%d-%B-%Y %I:%m %p')} | {format_timespan(total_s)} ago beacuse of that you have been Banned for 14 Day")
			reason = " Doing Freloading and Joining Again"
			#await guild.ban(member, reason=reason, delete_message_days=0)

			log_channel = self.bot.get_channel(855784930494775296)
			data = await self.bot.config.find(member.guild.id)
			log_embed = discord.Embed(title=f"🔨 Ban | Case ID: {data['case']}",
			    description=f" **Offender**: {member.name} | {member.mention} \n**Reason**: Found Doing Freloading at {than.strftime('%d-%B-%Y %I:%m %p')} | {format_timespan(total_s)} \n **Moderator**: <@{ban['BanedBy']}> {ban['BanedBy']}", color=0xE74C3C)
			log_embed.set_thumbnail(url=member.avatar_url)
			log_embed.timestamp = datetime.datetime.utcnow()
			log_embed.set_footer(text=f"ID: {member.id}")

			await log_channel.send(embed=log_embed)

			data["case"] += 1
			#await self.bot.config.upsert(data)


		except discord.HTTPException:

			reason = " Doing Freloading and Joining Again"
			#await guild.ban(member, reason=reason, delete_message_days=0)

			log_channel = self.bot.get_channel(855784930494775296)
			data = await self.bot.config.find(ctx.guild.id)
			log_embed = discord.Embed(title=f"🔨 Ban | Case ID: {data['case']}",
			    description=f" **Offender**: {member.name} | {member.mention} \n**Reason**: {reason}\n **Moderator**: <@{data['BanedBy']}> {data['BanedBy']}", color=0xE74C3C)
			log_embed.set_thumbnail(url=member.avatar_url)
			log_embed.timestamp = datetime.datetime.utcnow()
			log_embed.set_footer(text=f"ID: {member.id}")

			await log_channel.send(embed=log_embed)

			data["case"] += 1
			#await self.bot.config.upsert(data)

	@commands.command(name="fban", description="add User to freeloader")
	@commands.check_any(is_me(), perm_check())
	async def fban(self , ctx, user:int):
		user = await self.bot.fetch_user(user)
		if user is None:
			return await ctx.reply("please Enter valid Id")

		data = await self.bot.free.find(user.id)

		if bool(data):
			return await ctx.reply("User is alredy add to database")

		data = {"_id": user.id,
				"BanedBy": ctx.author.id,
				"guildId": ctx.guild.id,
				"time": datetime.datetime.utcnow()
		}

		await self.bot.free.upsert(data)

		embed = discord.Embed(color=0x2f3136,
		            description=f"<:allow:819194696874197004>|**{user.name}** Has Been added to freeloader"
		        )

		await ctx.reply(embed=embed, mention_author=False)

	@commands.command(name="funban", description="Remove user from freeloader")
	@commands.check_any(is_me(), perm_check())
	async def funban(self, ctx, user: int):
		user = await self.bot.fetch_user(user)
		if user is None:
			return await ctx.reply("please Enter valid Id")

		data = await self.bot.free.find(user.id)

		if data is None:
			return await ctx.reply(f"No User found with {user.name} | {user.id} in DataBase")

		embed = discord.Embed(color=0x2f3136,
		            description=f"<:allow:819194696874197004>|**{user.name}** Has Been Removed from freeloader"
		        )
		await self.bot.free.delete(user.id)

		await ctx.reply(embed=embed, mention_author=False)

def setup(bot):
    bot.add_cog(freeloader(bot))