import sqlite3
from datetime import datetime

# Establish connection to SQLite database
conn = sqlite3.connect('data/trading_game.db')

# Create a cursor object to execute SQL commands
c = conn.cursor()

# Retrieve user details from Users table
def get_user(UserID):
    c.execute("SELECT * FROM Users WHERE UserID = ?", (str(UserID),))
    return c.fetchone()

# Insert or update user shares in UserShares table
def insert_user_shares(UserID, symbol, shares, price):
    c.execute("SELECT * FROM UserShares WHERE UserID = ? AND Symbol = ?", (UserID, symbol))
    result = c.fetchone()

    if result:  # If user already has shares in the symbol, update the record
        new_shares = result[2] + shares
        new_avg_price = ((result[2] * result[3]) + (shares * price)) / new_shares
        c.execute("""
            UPDATE UserShares 
            SET Shares = ?, AvgPrice = ?
            WHERE UserID = ? AND Symbol = ?
        """, (new_shares, new_avg_price, UserID, symbol))
    else:  # If user does not have shares in the symbol, insert a new record
        c.execute("""
            INSERT INTO UserShares (UserID, Symbol, Shares, AvgPrice)
            VALUES (?, ?, ?, ?)
        """, (UserID, symbol, shares, price))

    # Commit the changes to the database
    conn.commit()

# Retrieve user shares from UserShares table
def get_user_shares(UserID, symbol):
    c.execute("SELECT * FROM UserShares WHERE UserID = ? AND Symbol = ?", (UserID, symbol))
    result = c.fetchone()
    return result

# Update user shares in UserShares table
def update_user_shares(UserID, symbol, shares):
    c.execute("SELECT * FROM UserShares WHERE UserID = ? AND Symbol = ?", (UserID, symbol))
    result = c.fetchone()

    if result:  # If user has shares in the symbol
        new_shares = result[2] - shares
        if new_shares < 0:  # If trying to sell more shares than owned
            return False
        elif new_shares == 0:  # If selling all shares
            c.execute("DELETE FROM UserShares WHERE UserID = ? AND Symbol = ?", (UserID, symbol))
        else:  # If selling some but not all shares
            c.execute("""
                UPDATE UserShares 
                SET Shares = ?
                WHERE UserID = ? AND Symbol = ?
            """, (new_shares, UserID, symbol))

        # Commit the changes to the database
        conn.commit()
        return True
    return False  # If user does not have shares in the symbol

# Insert user into Users table
def insert_user(UserID, balance):
    c.execute("INSERT INTO Users (UserID, Balance) VALUES (?, ?)", (str(UserID), balance))
    conn.commit()

# Retrieve user balance from Users table
def get_user_balance(UserID):
    c.execute("SELECT Balance FROM Users WHERE UserID = ?", (str(UserID),))
    result = c.fetchone()
    return result[0] if result else None

# Update user balance in Users table
def update_user_balance(UserID, balance):
    c.execute("UPDATE Users SET Balance = ? WHERE UserID = ?", (balance, str(UserID)))
    conn.commit()

# Retrieve user trades from Trades table
def get_user_trades(UserID):
    c.execute("SELECT * FROM Trades WHERE UserID = ?", (str(UserID),))
    return c.fetchall()


# Retrieve bank info from Bank table
def get_bank_info(symbol):
    c.execute("SELECT * FROM Bank WHERE Symbol = ?", (symbol,))
    return c.fetchone()

# Update bank info in Bank table
def update_bank_info(symbol, shares):
    c.execute("UPDATE Bank SET Shares = Shares + ? WHERE Symbol = ?", (shares, symbol))
    conn.commit()


# Insert a new trade into Trades table
def insert_trade(UserID, order_type, symbol, trade_price, shares):
    total_value = trade_price * shares
    trade_date = datetime.now().date()
    trade_hour = datetime.now().hour
    c.execute("""
        INSERT INTO Trades 
        (UserID, OrderType, Symbol, TradePrice, Shares, TotalValue, TradeDate, TradeHour)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (str(UserID), order_type, symbol, trade_price, shares, total_value, trade_date, trade_hour))
    conn.commit()


# Retrieve user short trades from ShortTrades table
def get_user_short_trades(UserID):
    c.execute("SELECT * FROM ShortTrades WHERE UserID = ?", (str(UserID),))
    return c.fetchall()

# Insert a short trade into ShortTrades and Trades table
def insert_short_trade(UserID, symbol, trade_price, shares):
    trade_date = datetime.now().date()
    trade_hour = datetime.now().hour
    c.execute("INSERT INTO ShortTrades (UserID, Symbol, TradePrice, Shares) VALUES (?, ?, ?, ?)",
              (str(UserID), symbol, trade_price, shares))
    c.execute("INSERT INTO Trades (UserID, OrderType, Symbol, TradePrice, TradeDate, TradeHour) VALUES (?, 'Short', ?, ?, ?, ?)",
              (str(UserID), symbol, trade_price, trade_date, trade_hour))
    conn.commit()


# Retrieve short trades from ShortTrades table
def get_short_trades(UserID, symbol):
    c.execute("SELECT * FROM ShortTrades WHERE UserID = ? AND Symbol = ? AND Covered = 0 ORDER BY ShortDate, ShortHour",
              (str(UserID), symbol))
    return c.fetchall()

# Calculate the sum of shares for a given symbol where the short has not been covered
def calculate_short_interest(symbol):
    c.execute("""
        SELECT SUM(Shares) 
        FROM ShortTrades 
        WHERE Symbol = ? AND Covered = 0
    """, (symbol,))
    
    result = c.fetchone()
    
    return result[0] if result[0] else 0

# Insert a short trade into ShortTrades and Trades table and calculate short interest
def insert_short_trade(UserID, symbol, trade_price, shares):
    trade_date = datetime.now().date()
    trade_hour = datetime.now().hour
    total_value = trade_price * shares
    short_interest = calculate_short_interest(symbol)

    c.execute("INSERT INTO ShortTrades (UserID, Symbol, TradePrice, Shares, ShortDate, Interest) VALUES (?, ?, ?, ?, ?, ?)",
              (str(UserID), symbol, trade_price, shares, trade_date, short_interest))

    c.execute("INSERT INTO Trades (UserID, OrderType, Symbol, TradePrice, Shares, TotalValue, TradeDate, TradeHour, ShortInterest) VALUES (?, 'Short', ?, ?, ?, ?, ?, ?, ?)",
              (str(UserID), symbol, trade_price, shares, total_value, trade_date, trade_hour, short_interest))

    conn.commit()

# Cover a short trade in Trades and ShortTrades table
def cover_short_trade(UserID, symbol, trade_price, shares):
    trade_date = datetime.now().date()
    trade_hour = datetime.now().hour
    total_value = trade_price * shares

    c.execute("INSERT INTO Trades (UserID, OrderType, Symbol, TradePrice, Shares, TotalValue, TradeDate, TradeHour) VALUES (?, 'Cover', ?, ?, ?, ?, ?, ?)",
              (str(UserID), symbol, trade_price, shares, total_value, trade_date, trade_hour))

    short_trades = get_short_trades(UserID, symbol)
    shares_to_cover = shares

    for short_trade in short_trades:
        if shares_to_cover == 0:
            break

        short_trade_shares = short_trade[3]
        if short_trade_shares <= shares_to_cover:
            c.execute("UPDATE ShortTrades SET Shares = 0, Covered = 1 WHERE ShortTradeID = ?", (short_trade[0],))
            shares_to_cover -= short_trade_shares
        else:
            remaining_shares = short_trade_shares - shares_to_cover
            c.execute("UPDATE ShortTrades SET Shares = ? WHERE ShortTradeID = ?", (remaining_shares, short_trade[0]))
            shares_to_cover = 0

    if shares_to_cover > 0:
        print("Not all requested shares could be covered; there were not enough short trades")

    conn.commit()


# Get total of all shorts from ShortTrades table
def get_total_shorts(UserID):
    c.execute("""
        SELECT SUM(TradePrice * Shares)
        FROM ShortTrades
        WHERE UserID = ? AND Covered = 0
    """, (UserID,))
    result = c.fetchone()
    return result[0] if result else 0


# Update short trade in ShortTrades table
def update_short_trade(UserID, symbol, new_amount):
    c.execute("UPDATE ShortTrades SET Amount=? WHERE UserID=? AND Symbol=?", (new_amount, str(UserID), symbol))
    conn.commit()


# Get total of all buys from UserShares table
def get_total_buys(UserID):
    c.execute("""
        SELECT SUM(Shares * AvgPrice) 
        FROM UserShares
        WHERE UserID = ?
    """, (UserID,))
    result = c.fetchone()
    return result[0] if result else 0


# Retrieve all users from Users table
def get_all_users():
    c.execute("SELECT * FROM Users")
    return c.fetchall()


# Get user's trade history from Trades table
def get_trade_history(user_id):
    c.execute("SELECT * FROM Trades WHERE UserID = ? ORDER BY TradeDate DESC, TradeHour DESC LIMIT 25", (user_id,))
    return c.fetchall()


# Close database connection
def close_connection():
    conn.close()