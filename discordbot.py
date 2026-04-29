import discord
from discord.ext import commands
from discord import ui
from config import Config
import logging
import aiohttp
import traceback
from datetime import datetime, timezone

intents = discord.Intents.default()
intents.message_content = True

GUILD_ID = discord.Object(id = Config.DISCORD_SERVER)

handler = logging.FileHandler(filename = "logs/DiscordAPI.log", encoding = 'utf-8', mode = 'w')

class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        try:
            synced = await self.tree.sync(guild = GUILD_ID)
            print(f'Synced {len(synced)} commands to the guild {GUILD_ID}')

        except Exception as e:
            print(f'Error Syncing Commands: {e}')

    async def on_message(self, message):
        if message.author == message.author.bot:
            return
        if "fuck you bot" in message.content.lower():
            await message.channel.send(f'FUCK YOUUU TOO {(str(message.author)).upper()}')

        print(f'Message from {message.author}: {message.content}')


class ClipPaginator(ui.View):
    def __init__(self, clips: list, user: discord.User):
        super().__init__(timeout=60)  # buttons expire after 60 seconds
        self.clips = clips
        self.user  = user            # only the user who ran the command can paginate
        self.index = 0               # tracks current page

    def build_embed(self) -> discord.Embed:
        clip = self.clips[self.index]
        thumbnail_url = clip.get("thumbnail_url") or "https://static-cdn.jtvnw.net/ttv-static/404_preview-480x272.jpg"

        embed = discord.Embed(
            title=clip["title"],
            url=clip["url"],
            description=f"📅 Clipped on: {clip['created_at'][:10]}",
            color=discord.Color.purple()
        )
        embed.add_field(name="ClipID:", value=clip["id"])
        embed.set_image(url=thumbnail_url)
        embed.set_footer(text=f"{self.index + 1} / {len(self.clips)}")  # ← "4 / 7"
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only the original user can click the buttons
        if interaction.user != self.user:
            await interaction.response.send_message("These aren't your buttons!", ephemeral=True)
            return False
        return True

    @ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: ui.Button):
        self.index = (self.index - 1) % len(self.clips)  # wraps around at the start
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: ui.Button):
        self.index = (self.index + 1) % len(self.clips)  # wraps around at the end
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def on_timeout(self):
        # Disable buttons after 60 seconds so they don't just sit there forever
        for item in self.children:
            item.disabled = True


client = Client(command_prefix = '!', intents = intents)

@client.tree.command(name="listclips", description="grabs TwitchClips from Database", guild=GUILD_ID)
async def listClips(interaction: discord.Interaction):
    await interaction.response.defer()

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{str(Config.API_URL)}/clips?limit=6&offset=0') as response:
            data = await response.json()

    if not data['success'] or not data['clips']:
        await interaction.followup.send("No clips found.")
        return

    paginator = ClipPaginator(clips=data['clips'], user=interaction.user)
    await interaction.followup.send(embed=paginator.build_embed(), view=paginator)

@client.tree.command(name="saveclip", description="Saves a Twitch clip to the Database", guild=GUILD_ID)
async def saveClip(interaction: discord.Interaction, link: str):
    await interaction.response.defer()

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": Config.DISCORDBOT_API_KEY  
    }
    payload = {
        "link": link
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{Config.API_URL}/clips',
                headers=headers,
                json=payload
            ) as response:
                data = await response.json()

        if data.get("error") is not None:
            embed = discord.Embed(
                title="❌ Failed to Save Clip",
                description=f"Error: {data['error']}",
                color=discord.Color.red()
            )

        else:
            embed = discord.Embed(
                title="✅ Clip Saved!",
                description= f"[{data['clip_title']}]({link})",
                color=discord.Color.green()
            )
            embed.add_field(name="Clip ID", value=data['clip_id'], inline=False)
            embed.set_image(url=data['thumbnail_url'])
            embed.set_footer(text = f'Added by {interaction.user.display_name}')

        await interaction.followup.send(embed=embed)

    except Exception as e:
        print(f"ITS BORKED! Error: {e}")
        traceback.print_exc()
        await interaction.followup.send(f"ITS BORKED! Error: {e}")

@client.tree.command(name="delclip", description="Deletes a Twitch clip from the Database", guild=GUILD_ID)
async def delClip(interaction: discord.Interaction, id: str):
    await interaction.response.defer()
    headers = {
        "X-API-Key": Config.DISCORDBOT_API_KEY  
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f'{Config.API_URL}/clips/{id}',
                headers=headers
            ) as response:
                data = await response.json()

        if data.get("error") is not None:
            embed = discord.Embed(
                title="❌ Failed to Delete Clip",
                description=f"Error: {data['error']}",
                color=discord.Color.red()
            )

        else:
            embed = discord.Embed(
                title="✅ Clip Deleted from Database!",
                description= data['message'],
                color=discord.Color.dark_purple()
            )
            embed.set_footer(text = f'Deleted by {interaction.user.display_name}')

        await interaction.followup.send(embed=embed)

    except Exception as e:
        print(f"ITS BORKED! Error: {e}")
        traceback.print_exc()
        await interaction.followup.send(f"ITS BORKED! Error: {e}")

@client.tree.command(name="swapclip", description="Replaces a clipID from the database with a twitch clip", guild=GUILD_ID)
async def swapclip(interaction: discord.Interaction, id: str, link: str):
    await interaction.response.defer()
    headers = {
        "X-API-Key": Config.DISCORDBOT_API_KEY  
    }
    payload = {
        "link": link
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f'{Config.API_URL}/clips/{id}',
                headers=headers,
                json=payload
            ) as response:
                data = await response.json()

        if data.get("error") is not None:
            embed = discord.Embed(
                title="❌ Failed to Replace Clip",
                description=f"Error: {data['error']}",
                color=discord.Color.red()
            )

        else:
            embed = discord.Embed(
                title="✅ Clip has been replaced!",
                description= f"ClipID: {id} has been replaced by ClipID: {data['clip_id']}",
                color=discord.Color(0xFF69B4)
            )
            embed.set_footer(text = f'Deleted by {interaction.user.display_name}')

        await interaction.followup.send(embed=embed)
    except Exception as e:
        print(f"ITS BORKED! Error: {e}")
        traceback.print_exc()
        await interaction.followup.send(f"ITS BORKED! Error: {e}")

@client.tree.command(name="updatevod", description="Backfills missing VOD data for all clips", guild=GUILD_ID)
async def updateVod(interaction: discord.Interaction):
    await interaction.response.defer()

    headers = {
        "X-API-Key": Config.DISCORDBOT_API_KEY
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{Config.API_URL}/clips/vod/update',
                headers=headers
            ) as response:
                data = await response.json()

                if not data.get("success"):
                    embed = discord.Embed(
                        title="❌ VOD Update Failed",
                        description=f"Error: {data.get('error', 'Unknown error')}",
                        color=discord.Color.red()
                    )
                else:
                    embed = discord.Embed(
                        title="✅ VOD Data Updated!",
                        description=data.get("message", "All VOD data has been backfilled."),
                        color=discord.Color.teal()
                    )
                    embed.set_footer(text=f"Requested by {interaction.user.display_name}")

                await interaction.followup.send(embed=embed)

    except Exception as e:
        print(f"ITS BORKED! Error: {e}")
        traceback.print_exc()
        await interaction.followup.send(f"ITS BORKED! Error: {e}")

@client.tree.command(name="timesince", description="Time since Last clip", guild=GUILD_ID)
async def timesince(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{str(Config.API_URL)}/clips?limit=1&offset=0') as response:
                data = await response.json()

        if not data['success'] or not data['clips']:
            await interaction.followup.send("No clips found.")
            return                              # ← exits here if no clips

        clip     = data['clips'][0]             # ← outside the if block now
        saved_at = datetime.fromisoformat(clip['created_at'])
        now      = datetime.now(timezone.utc)

        if saved_at.tzinfo is None:
            saved_at = saved_at.replace(tzinfo=timezone.utc)

        diff       = now - saved_at
        total_secs = int(diff.total_seconds())

        years   = diff.days // 365
        months  = (diff.days % 365) // 30
        weeks   = (diff.days % 365 % 30) // 7
        days    = diff.days % 365 % 30 % 7
        hours   = (total_secs % 86400) // 3600
        minutes = (total_secs % 3600)  // 60
        seconds = total_secs % 60

        parts = []
        if years:   parts.append(f"{years} year{'s' if years != 1 else ''}")
        if months:  parts.append(f"{months} month{'s' if months != 1 else ''}")
        if weeks:   parts.append(f"{weeks} week{'s' if weeks != 1 else ''}")
        if days:    parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours:   parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes: parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds: parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

        human_readable = ", ".join(parts)
        exact_time     = saved_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        thumbnail_url  = clip.get("thumbnail_url") or "https://static-cdn.jtvnw.net/ttv-static/404_preview-480x272.jpg"

        embed = discord.Embed(
            title="TIME SINCE THE EVENT HAPPENED",
            url=clip["url"],
            description=f"📅 Clipped on: {clip['created_at'][:10]}",
            color=discord.Color(0xFFEDBC)
        )
        embed.set_image(url=thumbnail_url)                                          # ← same level as embed
        embed.add_field(name="⏱️ It has been",   value=human_readable, inline=False)
        embed.add_field(name="🕐 Exact save time", value=exact_time,   inline=False)
        embed.add_field(name="Clip ID",            value=clip["id"],    inline=False)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        await interaction.followup.send(embed=embed)

    except Exception as e:
        print(f"ITS BORKED! Error: {e}")
        traceback.print_exc()
        await interaction.followup.send(f"ITS BORKED! Error: {e}")

client.run(Config.DISCORD_API_KEY, log_handler = handler, log_level=logging.DEBUG)