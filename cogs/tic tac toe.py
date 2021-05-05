import asyncio
import dataclasses
import logging
import random
from itertools import islice
from string import Template

import discord
from discord.ext import commands

from utils import Winner, TicTacToe, InvalidMove, PlayerStats
from utils.util import Pag

description = "Clasis Tic Tac Toe"
#hell YEs
class Games(commands.Cog, description=description):
    def __init__(self, bot):
        self.bot = bot
        self.stats = {}
        self.logger = logging.getLogger(__name__)

    async def chunk_results(self, it, size):
        it = iter(it)
        return iter(lambda: tuple(islice(it, size)), ())

    async def display_board(self, messageable, game, *, content=None):
        board = game.board
        desc = f"""
        ```yaml
    
          {board[0][0].to_piece()}|{board[0][1].to_piece()}|{board[0][2].to_piece()}
          {board[1][0].to_piece()}|{board[1][1].to_piece()}|{board[1][2].to_piece()}
          {board[2][0].to_piece()}|{board[2][1].to_piece()}|{board[2][2].to_piece()}
        ```
        """

        embed = discord.Embed(
            title=f"TicTacToe ({game.player_one.display_name} VS {game.player_two.display_name})",
            description=desc,
        )
        await messageable.edit(content=content, embed=embed)

    async def update_stats(self, member, end_state, was_player_one):
        player = self.stats.get(member.id, PlayerStats(member.id))

        if end_state.value == 1:
            if was_player_one:
                player.wins += 1
            else:
                player.losses += 1

        elif end_state.value == 2:
            if was_player_one:
                player.losses += 1
            else:
                player.wins += 1

        elif end_state.value == 3:
            player.draws += 1

        self.stats[member.id] = player

        data = dataclasses.asdict(player)
        data["_id"] = data.pop("player_id")
        await self.bot.tictactoe.upsert(data)

    async def populate_stats(self):
        # Handle on_ready being called multiple times
        if self.stats:
            return

        data = await self.bot.tictactoe.get_all()
        for document in data:
            player = PlayerStats(
                document["_id"],
                wins=document["wins"],
                losses=document["losses"],
                draws=document["draws"],
            )
            self.stats[document["_id"]] = player

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
        await self.populate_stats()

    @commands.command(name="tictactoe",description="old tictactoe Games", aliases=["ttt"])
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def tictactoe(self, ctx, player_two: discord.Member = None):
        if ctx.channel.id in [785849567518130176, 792246185238069249, 785860772470849536]:
            def check(m):
                return m.channel == ctx.channel and m.author == current_player

            def react_check(payload):
                return (
                    payload.message_id == difficulty_message.id
                    and payload.user_id == ctx.author.id
                    and str(payload.emoji) in ["1️⃣", "2⃣"]
                )

            is_bot = False
            difficulty = 1
            if not player_two or player_two == ctx.guild.me:
                player_two = ctx.guild.me
                is_bot = True

                embed = discord.Embed(
                    title="Please pick a difficulty",
                    description=":one: - Easy\n:two: - Hard",
                )

                difficulty_message = await ctx.send(embed=embed)
                await difficulty_message.add_reaction("1️⃣")
                await difficulty_message.add_reaction("2⃣")

                try:
                    payload = await self.bot.wait_for(
                        "raw_reaction_add", check=react_check, timeout=25
                    )
                except asyncio.TimeoutError:
                    await ctx.send("I picked hard on your behalf :)")
                else:
                    if str(payload.emoji) == "1️⃣":
                        difficulty = 2.5
                        await ctx.send("Set difficulty to easy", delete_after=10)
                    else:
                        await ctx.send("Set difficulty to hard", delete_after=10)
                finally:
                    await difficulty_message.delete()

            m = await ctx.send("Starting game!")

            game = TicTacToe(
                player_one=ctx.author,
                player_two=player_two,
                is_agaisnt_computer=is_bot,
                difficulty=difficulty,
            )

            player_one_start = random.choice([True, False])
            if not player_one_start:
                await game.flip_player()

            await self.display_board(m, game)

            while (winner := await game.is_over()) == Winner.NO_WINNER:
                current_player = ctx.author if game.is_player_one_move else player_two

                if not game.is_player_one_move and is_bot:
                    await self.display_board(
                        m,
                        game,
                        content=f"{current_player.mention}, please pick where you wish to play in the format `row column`",
                    )
                    await game.ai_turn()
                    await asyncio.sleep(random.randrange(0, 5))
                    continue

                try:
                    await self.display_board(
                        m,
                        game,
                        content=f"{current_player.mention}, please pick where you wish to play in the format `row column`",
                    )
                    msg = await self.bot.wait_for("message", check=check, timeout=25)
                except asyncio.TimeoutError:
                    await game.flip_player()
                    await ctx.send(f"{current_player.mention}, you missed your turn!")
                else:
                    content = msg.content

                    await msg.delete()

                    if not len(content) == 3:
                        await ctx.send(
                            f"{current_player.mention}, Invalid move sequence, please see the format and try again",
                            delete_after=10,
                        )
                        continue

                    row, column = content.split()
                    try:
                        await game.make_move(row, column)
                    except InvalidMove:
                        await ctx.send(
                            f"{current_player.mention}, illegal move sequence, please try again",
                            delete_after=10,
                        )
                        continue

            content = Template(str(winner)).safe_substitute(
                {"MENTIONONE": ctx.author.mention, "MENTIONTWO": player_two.mention}
            )
            await self.display_board(m, game, content=content)

            await self.update_stats(ctx.author, winner, True)
            await self.update_stats(player_two, winner, False)
        else:
            await ctx.send('Please Use the <#785849567518130176> to paly this Game')

    @commands.command(name="profile", description="Show Your Stats for the tic TicTacToe Game")
    async def profile(self, ctx, player: discord.Member = None):
        if ctx.channel.id in [785849567518130176, 792246185238069249, 785860772470849536]:

            """Returns your TicTacToe stats"""
            player = player or ctx.author
            if not (player_stats := self.stats.get(player.id)):
                return await ctx.send(f"I have no stats for `{player.display_name}`")

            embed = discord.Embed(
                title=f"TicTacToe stats for: `{player.display_name}`",
                description=f"Wins: **{player_stats.wins}**\n"
                f"Losses: **{player_stats.losses}**\n"
                f"Draws: **{player_stats.draws}**",
                timestamp=ctx.message.created_at,
            )
            embed.set_footer(text=f"Developed by Jay and utki007")
            await ctx.send(embed=embed)
        else:
            return

    @commands.command(nmae="leaderboard",description="leaderboard For the TicTacToe",aliases=["lb"])
    async def leaderboard(self, ctx, stat_type="wins"):
        """Shows the TicTacToe leaderboard"""
        if ctx.channel.id in [785849567518130176, 792246185238069249, 785860772470849536]:
            if (stat_type := stat_type.lower()) not in ["wins", "losses", "draws"]:
                return await ctx.send("Invalid stat type requested!")

            data = list(self.stats.values())
            if not data:
                return await ctx.send("I have no stats to show.")

            data = sorted(data, key=lambda x: getattr(x, stat_type), reverse=True)
            data = await self.chunk_results(data, 10)

            pages = []
            for item in data:
                page = ""
                for result in item:
                    page += f"<@{result.player_id}> - {getattr(result, stat_type)} {stat_type}\n"
                pages.append(page)

            await Pag(
                title=f"TicTacToe leaderboard for `{stat_type}`",
                colour=0x00008B,
                entries=pages,
                length=1,
            ).start(ctx)
        else:
            return


def setup(bot):
    bot.add_cog(Games(bot))
