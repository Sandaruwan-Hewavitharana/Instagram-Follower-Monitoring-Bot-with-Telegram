import requests
from telegram import Bot
import json
import time
import schedule

# Instagram Graph API and Telegram Bot Details
INSTAGRAM_ACCESS_TOKEN = "YOUR_INSTAGRAM_ACCESS_TOKEN"
INSTAGRAM_USER_ID = "YOUR_INSTAGRAM_USER_ID"  # Numeric ID of your account
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

# File to store previous followers
FOLLOWERS_FILE = "followers.json"


def get_followers():
    """Fetch the list of followers from Instagram API."""
    url = f"https://graph.instagram.com/{INSTAGRAM_USER_ID}/followers"
    params = {"access_token": INSTAGRAM_ACCESS_TOKEN}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        followers = [user["username"] for user in data.get("data", [])]
        return followers
    else:
        print(f"Error fetching followers: {response.json()}")
        return []


def load_previous_followers():
    """Load the previous list of followers from file."""
    try:
        with open(FOLLOWERS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_followers(followers):
    """Save the current list of followers to file."""
    with open(FOLLOWERS_FILE, "w") as file:
        json.dump(followers, file)


def notify_via_telegram(message):
    """Send a notification to Telegram."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def monitor_followers():
    """Monitor for new followers and unfollowers."""
    print("Checking followers...")

    current_followers = get_followers()
    previous_followers = load_previous_followers()

    # Determine new followers
    new_followers = list(set(current_followers) - set(previous_followers))
    if new_followers:
        notify_via_telegram(f"🎉 New Followers: {', '.join(new_followers)}")

    # Determine unfollowers
    unfollowers = list(set(previous_followers) - set(current_followers))
    if unfollowers:
        notify_via_telegram(f"⚠️ Unfollowers: {', '.join(unfollowers)}")

    # Save the updated list
    save_followers(current_followers)


# Schedule the monitoring every 10 minutes
schedule.every(10).minutes.do(monitor_followers)

print("Instagram Follower Monitoring Bot is running...")
while True:
    schedule.run_pending()
    time.sleep(1)
