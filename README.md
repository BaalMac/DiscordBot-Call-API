# 🎮 Twitch Clip Discord Bot

A Discord bot that connects to a Twitch Clip REST API, letting your server save, browse, replace, delete, and track clips — all through Discord slash commands.

---

## ✨ Features

| Command | Description |
|---|---|
| `/listclips` | Browse saved clips with a paginated embed viewer |
| `/saveclip <link>` | Save a Twitch clip to the database |
| `/delclip <id>` | Delete a clip from the database by ID |
| `/swapclip <id> <link>` | Replace an existing clip with a new one |
| `/timesince` | See how long ago the most recent clip was saved |

- 🔘 **Interactive pagination** — navigate clips with ⬅️ ➡️ buttons (only the invoking user can paginate)
- 🖼️ **Rich embeds** — thumbnails, titles, timestamps, and color-coded success/error states
- 🔐 **Authenticated write operations** — save, delete, and swap are protected via API key header
- ⏱️ **Human-readable time** — `/timesince` breaks elapsed time from years down to seconds

---

## 🛠️ Tech Stack

- **Python 3.12**
- **discord.py** — bot framework & slash commands
- **aiohttp** — async HTTP client for REST API calls
- **discord.ui** — interactive button components
- **Docker** — containerized deployment

---

## 🚀 Setup

### Option A — Docker (Recommended)

This is the easiest way to get the bot running, especially if you're deploying alongside a backend API container.

**1. Clone the repo**

```bash
git clone https://github.com/BaalMac/DiscordBot-Call-API.git
cd DiscordBot-Call-API
```

**2. Set up your environment file**

```bash
cp .env.template .env
```

Then fill in your values in `.env`:

```env
API_URL=http://twitchbot-api:5000
DISCORD_SERVER=your_guild_id
DISCORD_API_KEY=your_discord_bot_token
DISCORDBOT_API_KEY=your_backend_api_key
```

> ⚠️ `API_URL` defaults to `http://twitchbot-api:5000` which assumes your backend API is running in the same Docker network under the service name `twitchbot-api`. Adjust this if your setup is different.

**3. Build the Docker image**

```bash
docker build -t discordbot-call-api .
```

**4. Run the container**

```bash
docker run -d \
  --name discordbot \
  --env-file .env \
  discordbot-call-api
```

**Running alongside a backend API? Use a shared Docker network:**

```bash
docker network create twitch-net

docker run -d --name discordbot --env-file .env --network twitch-net discordbot-call-api
```

---

### Option B — Run Locally (Python)

**1. Clone the repo**

```bash
git clone https://github.com/BaalMac/DiscordBot-Call-API.git
cd DiscordBot-Call-API
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure environment**

```bash
cp .env.template .env
```

Fill in `.env` with your values (see above).

**4. Run the bot**

```bash
python3 discordbot.py
```

Logs are written to `logs/DiscordAPI.log`.

---

## ⚙️ Environment Variables

| Variable | Description |
|---|---|
| `API_URL` | Base URL of your Twitch Clip backend API |
| `DISCORD_SERVER` | Your Discord guild (server) ID |
| `DISCORD_API_KEY` | Your Discord bot token |
| `DISCORDBOT_API_KEY` | API key for authenticated backend requests |

> Never commit your `.env` file — it's already in `.gitignore`.

---

## 🤖 Commands

### `/listclips`
Fetches the latest 6 clips and displays them in a paginated embed with ⬅️ ➡️ navigation. Buttons expire after 60 seconds and are locked to the user who ran the command.

### `/saveclip <link>`
Saves a Twitch clip URL to the database.
```
/saveclip link: https://www.twitch.tv/channel/clip/ClipID
```

### `/delclip <id>`
Deletes a clip by its Twitch clip ID.
```
/delclip id: FragileBlitheSeahorsePermaSmug-8KGBa6SdLZyfuGmg
```

### `/swapclip <id> <link>`
Replaces an existing clip with a new Twitch clip URL.
```
/swapclip id: OldClipID link: https://www.twitch.tv/channel/clip/NewClipID
```

### `/timesince`
Shows the most recently saved clip and how long ago it was clipped — broken down into years, months, weeks, days, hours, minutes, and seconds.

---

## 📁 Project Structure

```
DiscordBot-Call-API/
├── discordbot.py       # Main bot — commands, paginator, client
├── config.py           # Loads environment variables
├── Dockerfile          # Docker image definition
├── .dockerignore       # Files excluded from Docker build
├── .env.template       # Environment variable template
├── .gitignore
├── requirements.txt
├── logs/
│   └── DiscordAPI.log  # Auto-generated at runtime
└── README.md
```

---

## 🔌 API Endpoints Used

| Method | Endpoint | Auth Required |
|---|---|---|
| `GET` | `/clips?limit=N&offset=N` | No |
| `POST` | `/clips` | ✅ API Key |
| `DELETE` | `/clips/:id` | ✅ API Key |
| `PUT` | `/clips/:id` | ✅ API Key |

---

## 🔒 Security Notes

- Write/delete endpoints require the `X-API-Key` header
- Only the user who triggered a paginator can click its buttons
- Bot ignores messages from other bots and itself
- Secrets are loaded from `.env` — never hardcoded

---

## 📄 License

[MIT](./LICENSE)
