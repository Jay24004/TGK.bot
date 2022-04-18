from discord import Interaction
from discord.ext import commands
import random
import discord

class Start_Gn(discord.ui.View):
    def __init__(self, bot, interaction, number):
        self.bot = bot
        self.interaction = interaction
        self.number = number
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Start Game", style=discord.ButtonStyle.green)
    async def start_game(self, interaction: Interaction, button: discord.Button):
        right_num = random.randint(1, self.number)
        await interaction.response.send_message(f"Right number is: {right_num}", ephemeral=True)

        await interaction.user.send(f"Right Number is: {right_num}")

        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        button.label = str("Started")

        await interaction.message.edit(view=self)

        thread = await interaction.message.create_thread(name="Guess Number Here", auto_archive_duration=60)

        self.bot.dispatch('game_start', interaction.message, thread, right_num)

        self.bot.guess_number[thread.id] = {'thread': thread, 'right_num': right_num, 'guess_num': 0}

        await interaction.channel.send(f"Start guessing the number in thread above, {thread.mention}")
    
    async def on_timeout(self, interaction):
        self.stop()

    async def interaction_check(self ,interaction):
        if interaction.user.id == self.interaction.user.id:
            return True
        else:
            await interaction.response.send_message("You can't start the game, you are not the host", ephemeral=True)