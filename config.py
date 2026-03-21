import os
from dotenv import load_dotenv

load_dotenv()
class Config:

    API_URL       = os.getenv('API_URL')
    DISCORD_SERVER = os.getenv('DISCORD_SERVER')
    DISCORD_API_KEY = os.getenv('DISCORD_API_KEY')
    DISCORDBOT_API_KEY = os.getenv('DISCORDBOT_API_KEY')