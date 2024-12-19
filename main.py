
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

#role management
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.guild_messages = True
intents.message_content = True

# create instance
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def bet(ctx, amount: int, team: str):
    try:
        await ctx.send(f'{ctx.author} bet {amount} on {team}')
    
    except discord.HTTPException as e:
        await ctx.send(e)
        


bot.run(os.getenv('discord_token').strip())