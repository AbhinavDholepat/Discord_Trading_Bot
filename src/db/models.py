import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('data/trading_game.db')
c = conn.cursor()

# Create Users table
c.execute("""
CREATE TABLE IF NOT EXISTS Users (
    UserID TEXT PRIMARY KEY,
    Balance REAL
)
""")

# Create Trades table
c.execute("""
CREATE TABLE IF NOT EXISTS Trades (
    TradeID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID TEXT,
    OrderType TEXT,
    Symbol TEXT,
    TradePrice REAL,
    Shares REAL,
    TotalValue REAL,
    TradeDate DATE,
    TradeHour INTEGER,
    ShortInterest REAL,
    FOREIGN KEY(UserID) REFERENCES Users(UserID)
)
""")


# Create ShortTrades table
c.execute("""
CREATE TABLE IF NOT EXISTS ShortTrades (
    ShortTradeID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID TEXT,
    Symbol TEXT,
    Shares REAL,
    TradePrice REAL,
    ShortDate DATE,
    ShortHour INTEGER,
    Interest REAL,
    Covered INTEGER DEFAULT 0,
    FOREIGN KEY(UserID) REFERENCES Users(UserID)
)
""")



# Create Bank table
c.execute("""
CREATE TABLE IF NOT EXISTS Bank (
    BankID INTEGER PRIMARY KEY AUTOINCREMENT,
    Symbol TEXT,
    Shares INTEGER,
    InterestRate REAL
)
""")

# Create UserShares table
c.execute("""
CREATE TABLE IF NOT EXISTS UserShares (
    UserID TEXT,
    Symbol TEXT,
    Shares INTEGER,
    AvgPrice REAL,
    FOREIGN KEY(UserID) REFERENCES Users(UserID)
)
""")

# Commit the changes and close the connection
conn.commit()
