# 🎬 Twitch Clip Discord Bot

A Discord bot that connects to a Twitch Clip API, allowing you to save, list, delete, replace, and track clips directly from your Discord server.

---

## 📋 Requirements

- Python 3.10+
- discord.py
- aiohttp
- A running Twitch Clip API (Flask backend)

Install dependencies:
```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
aiohttp==3.13.3
discord.py==2.7.1
python-dotenv==1.2.2
```

---

## ⚙️ Configuration

Create a `config.py` file or a `.env` file with the following values:

```env
DISCORD_API_KEY=your_discord_bot_token
DISCORD_SERVER=your_guild_id
DISCORDBOT_API_KEY=your_api_secret_key
API_URL=http://localhost:5000
```

> ⚠️ Never hardcode secrets directly in your code. Always load them from environment variables or a config file that is listed in `.gitignore`.

---

## 🚀 Running the Bot

```bash
python appTest.py
```

Logs are saved to `logs/DiscordAPI.log`.

---

## 🤖 Commands

### `/listclips`
Fetches the latest 6 clips from the database and displays them in a paginated embed.

**Usage:**
```
/listclips
```

**Features:**
- Displays clip title, thumbnail, clip date, and clip ID
- ⬅️ ➡️ buttons to navigate between clips
- Buttons expire after 60 seconds
- Only the user who called the command can navigate

---

### `/saveclip`
Saves a Twitch clip URL to the database.

**Usage:**
```
/saveclip link: https://www.twitch.tv/channel/clip/ClipID
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `link` | string | Full Twitch clip URL |

**Example:**
```
/saveclip link: https://www.twitch.tv/lucypyre/clip/ColorfulCrazySnoodBrokeBack
```

---

### `/delclip`
Deletes a clip from the database by its clip ID.

**Usage:**
```
/delclip id: ClipID
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | The clip ID to delete |

**Example:**
```
/delclip id: FragileBlitheSeahorsePermaSmug-8KGBa6SdLZyfuGmg
```

---

### `/swapclip`
Replaces an existing clip in the database with a new Twitch clip URL.

**Usage:**
```
/swapclip id: ExistingClipID link: https://www.twitch.tv/channel/clip/NewClipID
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | The clip ID to replace |
| `link` | string | The new Twitch clip URL to replace it with |

**Example:**
```
/swapclip id: OldClipID link: https://www.twitch.tv/lucypyre/clip/NewClipID
```

---

### `/timesince`
Shows the most recently clipped event and how long ago it was clipped, along with the exact timestamp.

**Usage:**
```
/timesince
```

**Displays:**
- Clip title and thumbnail
- Human readable time (e.g. `2 years, 3 months, 1 week, 4 days, 2 hours, 15 minutes, 30 seconds`)
- Exact save timestamp in UTC
- Clip ID

---

## 📁 Project Structure

```
DiscordBot/
├── appTest.py              # Main bot file (commands + paginator)
├── config.py               # Config loader
├── logs/
│   └── DiscordAPI.log      # Auto-generated log file
└── README.md
```

---

## 🔒 Security Notes

- All API requests are authenticated using the `X-API-Key` header
- Only the user who triggered a paginator can interact with its buttons
- Bot ignores messages from other bots and itself

---