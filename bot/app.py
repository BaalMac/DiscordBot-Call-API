import discord
from discord import app_commands
from discord.ext import commands
from config import Config
from logger import logger
import logging
from twitch.clips import SaveClip, UpdateClip, RemoveClip, GetClips, UpdateVodData

# Bot Setup
handler = logging.FileHandler(filename = "logs/DiscordAPI.log", encoding = 'utf-8', mode = 'w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix = "/", intents = intents, help_command = None)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}') #Bot Name
    print(bot.user.id) #Bot ID

# Embed Helpers
def success_embed(title: str, fields: dict, user: discord.User) -> discord.Embed:
    embed = discord.Embed(title=title, color=0x1D9E75)  # Teal — success
    for label, value in fields.items():
        embed.add_field(name=label, value=value, inline=False)
    embed.set_footer(text=f'Requested by {user.name}')
    return embed

def error_embed(title: str, reason: str, user: discord.User) -> discord.Embed:
    embed = discord.Embed(title=title, color=0xE24B4A)  # Red — error
    embed.add_field(name='Reason', value=reason, inline=False)
    embed.set_footer(text=f'Requested by {user.name}')
    return embed

def warning_embed(title: str, fields: dict, user: discord.User) -> discord.Embed:
    embed = discord.Embed(title=title, color=0xEF9F27)  # Amber — warning
    for label, value in fields.items():
        embed.add_field(name=label, value=value, inline=False)
    embed.set_footer(text=f'Requested by {user.name}')
    return embed

# Role Checker Decorator
def require_roles():
    Roles = "ClipManager"
    async def predicate(interaction: discord.Interaction):
        role = discord.utils.get(interacton.user.roles, name = str(Roles))
        if role is None:
            await interaction.response.send_message(
                embed = error_embed(
                    "Permission denied",
                    f"U need the Role: {Roles} to use the command",
                    interaction.user
                ),
                ephemeral = True
            )
            return False
        return True
    return app_commands.check(predicate)

@bot.tree.command(name = 'save', description = 'Save a twitch clip to the database')
@app_commands.describe(link = "The Twitch Clip URL to save")
async def save(interaction: discord.Interaction, link: str):
    await interaction.response.defer()
    result = SaveClip(link)

    if not result['success']:
        await interaction.followup.send(
            embed = error_embed("Could not save Clip", result["error"], interaction.user)
        )
        return

    fields = {"Clip ID": result['clip_id'], 'URL': link }
    
    if result.get('vod_pending'):
        fields['Status'] = 'Saved ✓  |  VOD pending'
        await interaction.followup.send(
            embed=warning_embed('Clip saved', fields, interaction.user)
        )
    else:
        fields['Status'] = 'Saved ✓'
        await interaction.followup.send(
            embed=success_embed('Clip saved', fields, interaction.user)
        )


@bot.command
async def ping(ctx): # THIS WORKS HOLY
    fields = {"Clip ID": "PLEASE GOD WORK", 'Status': None, 'URL': "twitch.com/lucypyre" }
    fields['Status'] = 'Saved ✓  |  Jesus answered ur payers'
    await ctx.send(
            embed = success_embed("PONG!", {"God": "PLEASE GOD WORK", "URL": "onlyfans.com/GuysAWeeaboo", 'Status': fields}, ctx.author)
        )

@bot.group(invoke_without_command = True)
async def help(ctx):
    em = discord.Embed(title="Help Menu", description="Here are my commands:")
    em.add_field(name="Clips", value="save, update, remove, getlist")
    em.set_footer(text=f'Requested by {ctx.author}')
    await ctx.send(embed=em)


# Start the bot
def start_bot():
    logger.info('Starting Discord bot...')
    bot.run(Config.DISCORD_TOKEN, log_handler = handler, log_level=logging.DEBUG)