import discord
from discord.ext import commands
from db.operations import (get_user_balance, get_total_buys, get_total_shorts,
                               get_all_users, get_trade_history)  # import the necessary functions
from utils.misc import get_price

# You need to pass the bot as a parameter to use its decorators
def setup(bot):

    # Command for users to view their portfolio value broken down by cash, long, short and net values
    @bot.command(
        name="bank",
        description="This will display the total portfolio value"
    )
    async def bank(ctx):
        try:
            # Fetch the user's balance
            balance = get_user_balance(str(ctx.author.id))

            # Fetch the total value of the buys (long positions)
            total_buys = get_total_buys(str(ctx.author.id)) or 0

            # Fetch the total value of the shorts
            total_shorts = get_total_shorts(str(ctx.author.id)) or 0

            # Calculate the net position
            net_position = round(total_buys - total_shorts, 2)
            net_cash_position = round(balance + total_buys - total_shorts, 2)

            # Format the values with two decimal places
            balance = round(balance, 2)
            total_buys = round(total_buys, 2)
            total_shorts = round(total_shorts, 2)

            await ctx.send(f"User ID: {ctx.author.id}\nCash: ${balance}\nLong Positions: ${total_buys}\nShort Positions: ${total_shorts}\nNet Position: ${net_position}\nNet Cash Position: ${net_cash_position}")
        except Exception as e:
            await ctx.send(f"An error occurred while processing the request: {str(e)}")


    # Command for users to get the portfolio value broken down by cash, long, short and net values for all players
    @bot.command(
        name="scorecard",
        description="This will display the portfolio values of all users"
    )
    async def scorecard(ctx):
        try:
            # Fetch all users
            users = get_all_users()

            for user in users:
                # Fetch the user's balance
                balance = get_user_balance(user[0]) or 0

                # Fetch the total value of the buys (long positions)
                total_buys = get_total_buys(user[0]) or 0

                # Fetch the total value of the shorts
                total_shorts = get_total_shorts(user[0]) or 0

                # Calculate the net position
                net_position = round(total_buys - total_shorts, 2)
                net_cash_position = round(balance + total_buys - total_shorts, 2)

                # Format the values with two decimal places
                balance = round(balance, 2)
                total_buys = round(total_buys, 2)
                total_shorts = round(total_shorts, 2)

                await ctx.send(f"User ID: {user[0]}\nCash: ${balance}\nLong Positions: ${total_buys}\nShort Positions: ${total_shorts}\nNet Position: ${net_position}\nNet Cash Position: ${net_cash_position}")
        except Exception as e:
            await ctx.send(f"An error occurred while processing the request: {str(e)}")


    # Command for users to fetch the price of a stock
    @bot.command(
        name="price",
        description="This will fetch the price of a stock"
    )
    async def price(ctx, symbol: str):
        try:
            # Fetch the current price of the stock
            current_price = get_price(symbol)

            await ctx.send(f"The current price of {symbol} is ${current_price}.")
        except Exception as e:
            await ctx.send(f"An error occurred while fetching the price: {str(e)}")

            

    @bot.command(
        name="trade_history",
        description="This will print the last 25 trades made by the user"
    )
    async def trade_history(ctx):
        try:
            # Fetch the last 25 trades made by the user
            trades = get_trade_history(str(ctx.author.id))

            # If the user has not made any trades yet
            if not trades:
                await ctx.send("You have not made any trades yet.")
                return

            # Generate a response
            response = "Here are your last 25 trades:\n"
            for trade in trades:
                # For buy and sell trades, display shares and total value
                response += f"On {trade[7]} at hour {trade[8]}, you made a {trade[2]} trade, trading {trade[5]} shares of {trade[3]} at a price of ${trade[4]} per share, for a total value of ${trade[6]}.\n"

            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"An error occurred while processing the request: {str(e)}")

