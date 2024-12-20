
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from datetime import datetime
import random
from balldontlie import BalldontlieAPI
import sqlite3

load_dotenv()

#role management
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.guild_messages = True
intents.message_content = True

# create instance
bot = commands.Bot(command_prefix='$', intents=intents)

# set up db
conn = sqlite3.connect('nba.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                user_name TEXT,
                balance INTEGER DEFAULT 1000
            )''')
c.execute('''CREATE TABLE IF NOT EXISTS bets (
                user_id INTEGER,
                amount INTEGER,
                team TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )''')
conn.commit()

# global variable to store game of the day
game_of_the_day = None
bets_open = True

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await send_random_game()

def fetch_NBA_game():
    date = datetime.now().strftime('%Y-%m-%d')
    api = BalldontlieAPI(api_key="bc95f994-c1e1-4bd8-8b0c-0e6f08b7db53")
    games = api.nba.games.list(dates=[date])
    todays_games = [game for game in games.data if game.date == date]
    return todays_games

async def send_random_game():
    global game_of_the_day
    try:
        channel = bot.get_channel(int(os.getenv('discord_channel').strip()))
        todays_games = fetch_NBA_game()
        if todays_games != []:
            game_of_the_day = random.choice(todays_games)
            game_info = f"{game_of_the_day.visitor_team['name']} @ {game_of_the_day.home_team['name']} as game of the day"
            await channel.send(f'Game Info: {game_info}')
        else:
            await channel.send('No games today')
    except discord.HTTPException as e:
        await channel.send(f'Error: {e}')

@bot.command()
async def instructions(ctx):
    instructions_text = (
        "**Instructions:**\n\n"
        "**1. Betting:**\n"
        "- **Command:** `$bet <amount> <team>`\n"
        "- **Description:** Place a bet on a team for the game of the day. You can only bet on one game per day.\n"
        "- **Example:** `$bet 100 Lakers`\n\n"
        "**2. View Bets:**\n"
        "- **Command:** `$bets`\n"
        "- **Description:** View your current bets.\n"
        "- **Example:** `$bets`\n\n"
        "**3. Check Balance:**\n"
        "- **Command:** `$balance`\n"
        "- **Description:** Check your current balance.\n"
        "- **Example:** `$balance`\n\n"
        "**4. Game Score:**\n"
        "- **Command:** `$score <team_name>`\n"
        "- **Description:** Get the score, opposing team, and status of the game for a specified team.\n"
        "- **Example:** `$score Lakers`\n\n"
        "**Daily Schedule:**\n"
        "- **Send Random Game:** 10:00 AM\n"
        "- **Add Daily Bonus:** 12:00 AM\n"
        "- **Distribute Winnings:** 11:59 PM\n"
        "- **Close Bets:** 5:00 PM\n"
    )
    await ctx.send(instructions_text)

@bot.command()
async def bet(ctx, amount: int, team: str):
    if not bets_open:
        await ctx.send('Betting is closed for today.')
        return
    
    if game_of_the_day is None:
        await ctx.send('No games today')
        return
    if team.lower() not in [game_of_the_day.home_team['name'].lower(), game_of_the_day.visitor_team['name'].lower()]:
        await ctx.send(f'You can only bet on {game_of_the_day.home_team["name"]} or {game_of_the_day.visitor_team["name"]}.')
        return
    user_id = ctx.author.id
    username = ctx.author.display_name

    try:
        c.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        user =c.fetchone()
        if user is None:
            c.execute('INSERT INTO users (user_id, user_name, balance) VALUES (?, ?, ?)', (user_id, username, 1000))
            conn.commit()
            user = (1000,)
        balance = user[0]
        if amount > balance:
            await ctx.send(f'You do not have enough balance to place this bet. Your balance is {balance}')
            return
    except discord.HTTPException as e:
        await ctx.send(e)
    
    try:
        new_balance = balance - amount
        c.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id))
        c.execute('INSERT INTO bets (user_id, amount, team) VALUES (?, ?, ?)', (user_id, amount, team))
        conn.commit()
        await ctx.send(f'{ctx.author.display_name} bet {amount} on {team}. Your new balance is {new_balance}.')
    except discord.HTTPException as e:
        await ctx.send(e)


@bot.command()
async def bets(ctx):
    try:
        user_id = ctx.author.id
        c.execute("SELECT amount, team FROM bets WHERE user_id = ?", (user_id,))
        user_bets = c.fetchall()
        if user_bets:
            bet_list = '\n'.join([f"{amount} on {team}" for amount, team in user_bets])
            await ctx.send(f'Your bets:\n{bet_list}')
        else:
            await ctx.send('You have no bets')

    except discord.HTTPException as e:
        await ctx.send(e)

@bot.command()
async def balance(ctx):
    try:
        user_id = ctx.author.id
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        user_balance = c.fetchone()
        if user_balance:
            await ctx.send(f'Your current balance is {user_balance[0]}.')
        else:
            await ctx.send('You do not have an account yet.')
    except discord.HTTPException as e:
        await ctx.send(e)

@bot.command()
async def score(ctx, team_name: str):
    todays_games = fetch_NBA_game()
    for game in todays_games:
        if team_name.lower() in [game.home_team['name'].lower(), game.visitor_team['name'].lower()]:
            home_team = game.home_team['name']
            visitor_team = game.visitor_team['name']
            home_score = game.home_team_score
            visitor_score = game.visitor_team_score
            status = game.status
            if team_name.lower() == home_team.lower():
                opposing_team = visitor_team
                team_score = home_score
                opposing_score = visitor_score
            else:
                opposing_team = home_team
                team_score = visitor_score
                opposing_score = home_score
            await ctx.send(f"{team_name} {team_score} VS {opposing_team} {opposing_score}, Status: {status}")
            return
    await ctx.send(f"No game found for team: {team_name}")

@bot.command()
async def hard_reset(ctx):
    c.execute("DELETE FROM bets")
    c.execute("UPDATE users SET balance = 1000")
    conn.commit()
    await ctx.send('Bets and balances have been reset.')

def add_daily_bonus():
    c.execute('UPDATE users SET balance = balance + 25')
    conn.commit()

def distribute_winnings():
    if game_of_the_day is None:
        return

    # Determine the winning team
    if game_of_the_day.home_team_score > game_of_the_day.visitor_team_score:
        winning_team = game_of_the_day.home_team['name']
    else:
        winning_team = game_of_the_day.visitor_team['name']

    # Calculate the total pool and the total winning bets
    c.execute("SELECT SUM(amount) FROM bets")
    total_pool = c.fetchone()[0] or 0

    c.execute("SELECT SUM(amount) FROM bets WHERE team = ?", (winning_team,))
    total_winning_bets = c.fetchone()[0] or 0

    if total_winning_bets == 0:
        return

    # Distribute the pool to the winning bets
    c.execute("SELECT user_id, amount FROM bets WHERE team = ?", (winning_team,))
    winning_bets = c.fetchall()

    for user_id, amount in winning_bets:
        proportion = amount / total_winning_bets
        winnings = proportion * total_pool
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (winnings, user_id))
    conn.commit()
    c.execute("DELETE FROM bets")
    conn.commit()

def close_bets():
    global bets_open
    bets_open = False

def open_bets():
    global bets_open
    bets_open = True

# scheduler 
scheduler = AsyncIOScheduler()
scheduler.add_job(send_random_game, 'cron', hour=10, minute=0)
scheduler.add_job(add_daily_bonus, 'cron', hour=0, minute=0)
scheduler.add_job(distribute_winnings, 'cron', hour=23, minute=59)
scheduler.add_job(close_bets, 'cron', hour=17, minute=0)
scheduler.add_job(open_bets, 'cron', hour=1, minute=0)


async def main():
    scheduler.start()
    await bot.start(os.getenv('DISCORD_TOKEN').strip())

asyncio.run(main())