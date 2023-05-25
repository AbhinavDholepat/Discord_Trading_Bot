import discord
from discord.ext import commands
from db.operations import (get_user_balance, update_user_balance, insert_trade, 
                           get_short_trades, cover_short_trade, insert_user_shares, 
                           get_user_shares, update_user_shares, update_bank_info, insert_short_trade,
                           update_short_trade)  # Import new operations
from utils.misc import get_price

def setup(bot):

    @bot.command(
        name="buy",
        description="This will buy a stock"
    )
    async def buy(ctx, symbol: str, shares: int):
        try:
            current_price = get_price(symbol)

            if current_price is None:
                await ctx.send(f"Failed to fetch the price for {symbol}. Please try again later.")
                return

            current_price = float(current_price)
            cost = current_price * shares
            balance = get_user_balance(str(ctx.author.id))

            if balance < cost:
                await ctx.send("You don't have enough balance to make this trade.")
                return

            update_user_balance(str(ctx.author.id), balance - cost)
            insert_trade(str(ctx.author.id), "BUY", symbol, current_price, shares)
            update_bank_info(symbol, -shares)

            # Add the shares to the UserShares table
            insert_user_shares(str(ctx.author.id), symbol, shares, current_price)

            await ctx.send(f"You have successfully bought {shares} shares of {symbol} at ${current_price} each.")
        except Exception as e:
            await ctx.send(f"An error occurred while processing the request: {str(e)}")
            

    @bot.command(
        name="sell",
        description="This will sell a stock"
    )
    async def sell(ctx, symbol: str, shares: int):
        try:
            current_price = get_price(symbol)

            # Check if the user owns enough shares of the stock to sell using UserShares table
            owned_shares = get_user_shares(str(ctx.author.id), symbol)

            if owned_shares is None or owned_shares[2] < shares:
                await ctx.send(f"You do not own enough shares of {symbol} to sell.")
                return

            earnings = current_price * shares
            balance = get_user_balance(str(ctx.author.id))
            update_user_balance(str(ctx.author.id), balance + earnings)
            insert_trade(str(ctx.author.id), "SELL", symbol, current_price, shares)
            update_bank_info(symbol, shares)

            # Subtract the shares from the UserShares table
            if not update_user_shares(str(ctx.author.id), symbol, shares):
                await ctx.send(f"Error updating the shares owned by the user.")
                return

            await ctx.send(f"You have successfully sold {shares} shares of {symbol} at ${current_price} each.")
        except Exception as e:
            await ctx.send(f"An error occurred while processing the request: {str(e)}")



    # Command for users to short a stock
    @bot.command(
        name="short",
        description="This will short a stock"
    )
    async def short(ctx, symbol: str, shares: float):
        try:
            # Get the current price of the stock
            current_price = get_price(symbol)

            # Calculate the number of shares to short based on the amount
            amount = shares * current_price

            # Fetch the user's balance
            balance = get_user_balance(str(ctx.author.id))

            # Check if the user has enough balance to short the stock
            if balance < amount:
                await ctx.send("You do not have enough balance to short this stock.")
                return

            # Deduct the amount from the user's balance
            update_user_balance(str(ctx.author.id), balance + amount)

            # Record the short in the ShortTrades table
            # You need to write a separate function for this, similar to insert_trade
            insert_short_trade(str(ctx.author.id), symbol, current_price, shares)

            # Update the Bank table to reflect the short
            update_bank_info(symbol, shares)

            # Format the values with two decimal places
            balance = round(balance, 2)
            amount = round(amount, 2)
            shares = round(shares, 0)
            current_price = round(current_price, 2)

            await ctx.send(f"You have successfully shorted ${amount} of {symbol} at ${current_price} per share. Total shorted shares {shares}.")
        except Exception as e:
            # If there's an error, send a message to the user
            await ctx.send(f"An error occurred while processing the request: {str(e)}")


    # Command for users to cover the short of a stock
    @bot.command(
        name="cover",
        description="This will cover a short"
    )
    async def cover(ctx, symbol: str, shares: float):
        try:
            # Fetch the current price of the stock
            current_price = get_price(symbol)

            # Check if the user has a short position for the stock
            short_trades = get_short_trades(str(ctx.author.id), symbol)
            if not short_trades:
                await ctx.send(f"You do not have a short position for {symbol}.")
                return

            # Iterate over all short trades, covering them until we've covered the desired amount
            total_covered = 0
            for short_trade in short_trades:
                if total_covered >= shares:
                    break
                short_shares = short_trade[3]
                shares_to_cover = min(shares - total_covered, short_shares)

                # Calculate the cost to cover the short
                cost = current_price * shares_to_cover

                # Fetch the user's balance and check if the user has enough balance to cover the short
                balance = get_user_balance(str(ctx.author.id))
                if balance < cost:
                    await ctx.send("You do not have enough balance to cover this short.")
                    return

                # Deduct the cost from the user's balance
                update_user_balance(str(ctx.author.id), balance - cost)

                # Cover the short
                cover_short_trade(str(ctx.author.id), symbol, current_price, shares_to_cover)

                total_covered += shares_to_cover

            await ctx.send(f"You have successfully covered {total_covered} shares of {symbol} at ${current_price} per share.")

            # Update the Bank table, increase the number of shares
            update_bank_info(symbol, total_covered)

        except Exception as e:
            await ctx.send(f"An error occurred while processing the request: {str(e)}")


