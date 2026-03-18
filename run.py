from logger import logger
from bot.app import start_bot

if __name__ == '__main__':
    logger.info('Starting up...')
    start_bot()
    logger.info('Discord Bot initialized successfully')