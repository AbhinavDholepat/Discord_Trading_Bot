import discord
from discord.ext import commands
from db.operations import get_user, insert_user, update_user_balance


# You need to pass the bot as a parameter to use its decorators
def setup(bot):

    # Command for users to request to join the game
    @bot.command(
        name="request",
        description="Request to join the game"
    )
    async def request(ctx):
        # Check if the user has already requested to join the game
        user = get_user(str(ctx.author.id))
        if user is not None:
            await ctx.send("You have already requested to join the game.")
            return

        # If not, insert the user into the Users table with a null balance
        insert_user(str(ctx.author.id), None)

        await ctx.send("Your request to join the game has been sent.")

    # Command for moderators to accept a user's request to join the game
    @bot.command(
        name="accept",
        description="Accept a user's request to join the game" # Replace 'Moderator' with the actual name of the moderator role
    )
    async def accept(ctx, user: discord.User):
        # Check if the user has requested to join the game
        user_in_db = get_user(str(user.id))
        if user_in_db is None:
            await ctx.send(f"{user.name} has not requested to join the game.")
            return

        # If the user has been accepted already, inform the moderator
        if user_in_db[1] is not None:
            await ctx.send(f"{user.name} has already been accepted into the game.")
            return

        # If not, update the user's balance to $100,000
        update_user_balance(str(user.id), 100000)

        await ctx.send(f"{user.name} has been accepted into the game.")