
# config.py - Configuration settings for the bot

import os

# Telegram API Token 
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8117518436:AAHiKIqQ-LbI7bgmgwQK0NxjowW1X-tabq8")

# Admin User IDs
ADMIN_USER_IDS = [6605649658]

# Target sites for checking
TARGET_SITES = {
    "braintree": {"url": "braintree.com", "success_rate": 60},
    "stripe": {"url": "stripe.com", "success_rate": 40},
    "paypal": {"url": "paypal.com", "success_rate": 30},
    "adyen": {"url": "adyen.com", "success_rate": 35},
    "worldpay": {"url": "worldpay.com", "success_rate": 25}
}
