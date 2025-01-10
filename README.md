# DiscordSportsBot

A Discord bot that allows users to place bets on NBA games, check scores, view their balances, and more. The bot uses the `discord.py` library and the `BalldontlieAPI` for fetching NBA game data. It also incorporates a SQLite database to manage user balances and bets.

## Features

- **Betting System**: Users can place bets on the game of the day.
- **Balance Management**: Each user has a virtual balance to manage their bets.
- **Game of the Day**: A random NBA game is selected and announced each day.
- **Daily Bonuses**: Users receive a daily bonus to their balance.
- **Score Checking**: Users can check the scores of ongoing or completed games.
- **Automatic Winnings Distribution**: Winnings are calculated and distributed based on the game results.
- **Command Instructions**: The bot provides detailed instructions for using its commands.

## Commands

- `$instructions`: Get detailed instructions on how to use the bot.
- `$bet <amount> <team>`: Place a bet on a specified team for the game of the day.
- `$bets`: View your current bets.
- `$balance`: Check your current balance.
- `$score <team_name>`: Get the score and status of the game for a specified team.
- `$hard_reset`: Reset all bets and balances.

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ryantoby40/DiscordSportsBot.git
   ```
2. **Install Dependencies**:
   ```bash
   pip install discord.py apscheduler python-dotenv sqlite3 balldontlie
   ```
3. **Set Up Environment Variables**:
   Create a `.env` file in the root directory with the following variables:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   discord_channel=your_channel_id
   ```

4. **Run the Bot**:
   ```bash
   python bot.py
   ```

## Scheduler Jobs

- **Send Random Game**: Sends a random NBA game to the designated channel at 10:00 AM.
- **Add Daily Bonus**: Adds a daily bonus of 25 units to each user's balance at 12:00 AM.
- **Distribute Winnings**: Distributes the winnings at 11:59 PM.
- **Close Bets**: Closes betting for the day at 5:00 PM.
- **Open Bets**: Reopens betting at 1:00 AM.

## Technologies Used

- `discord.py`: For interacting with the Discord API.
- `apscheduler`: For scheduling recurring tasks.
- `sqlite3`: For managing user data and bets.
- `BalldontlieAPI`: For fetching NBA game data.

---

**Note**: Replace placeholders like `your-repo`, `your_discord_bot_token`, and `your_channel_id` with actual values.
