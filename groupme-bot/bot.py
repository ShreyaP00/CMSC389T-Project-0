import requests
import time
import json
import os
from dotenv import load_dotenv
import random

load_dotenv()

BOT_ID = os.getenv("BOT_ID")
GROUP_ID = os.getenv("GROUP_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
LAST_MESSAGE_ID_FILE = "last_message_id.txt"  # New line for the file path
LAST_MESSAGE_ID = None
PLAY_GAME = False


def save_last_msg_id(message_id):
    with open(LAST_MESSAGE_ID_FILE, "w") as file:
        file.write(str(message_id))


def load_last_msg_id():
    if os.path.exists(LAST_MESSAGE_ID_FILE):
        with open(LAST_MESSAGE_ID_FILE, "r") as file:
            return int(file.read().strip())
    return None


def send_message(text, attachments=None):
    """Send a message to the group using the bot."""
    post_url = "https://api.groupme.com/v3/bots/post"
    data = {"bot_id": BOT_ID, "text": text, "attachments": attachments or []}
    response = requests.post(post_url, json=data)
    return response.status_code == 202


def get_group_messages(since_id=None):
    """Retrieve recent messages from the group."""
    params = {"token": ACCESS_TOKEN}
    if since_id:
        params["since_id"] = since_id

    get_url = f"https://api.groupme.com/v3/groups/{GROUP_ID}/messages"
    response = requests.get(get_url, params=params)
    if response.status_code == 200:
        # this shows how to use the .get() method to get specifically the messages but there is more you can do (hint: sample.json)
        return response.json().get("response", {}).get("messages", [])
    return []


def process_message(message):
    """Process and respond to a message."""
    global LAST_MESSAGE_ID
    global PLAY_GAME
    text = message["text"].lower()
    sender_id = message["sender_id"]
    my_user_id = "105724506"
    my_id = "883832"


    #if the message is from itself or another bot, do not reply
    if sender_id == my_id or message["sender_type"] == "bot":
        return

    # i.e. responding to a specific message (note that this checks if "hello bot" is anywhere in the message, not just the beginning)
    if sender_id == my_user_id and "hello" in text:
        send_message("sup")

    elif sender_id == my_user_id and "hi" in text:
        send_message("hello")

    elif sender_id == my_user_id and "bye" in text:
        send_message(f"Bye!")
    
    elif "good morning" in text:
        sender_name = message.get("name", "Unknown")
        send_message(f"Good morning, {sender_name}!")
    
    elif "good night" in text:
        sender_name = message.get("name", "Unknown")
        send_message(f"Good night, {sender_name}!")

    # Play a Rock-Paper-Scissors game with the user
    elif sender_id == my_user_id and "play" in text:
        send_message("Okay! Let's play Rock-Paper-Scissors\n"
                     "Enter:\nr for rock\np for paper\ns for scissors: ")
        PLAY_GAME = True
    
    elif sender_id == my_user_id and PLAY_GAME and text in ['r', 'p', 's']: 
        user_entered = text
        choices = ['rock', 'paper', 'scissors']
        bot_choice = random.choice(choices)

        if user_entered == 'r':
            user_choice = 'rock'
        elif user_entered == 'p':
            user_choice = 'paper'
        elif user_entered == 's':
            user_choice = 'scissors'
            
        send_message(f"Your choice: {user_choice}\nMy choice: {bot_choice}")
        result = winner(user_choice, bot_choice)
        send_message(f"{result}")

        send_message("Would you like to continue? y/n")
        
    elif sender_id == my_user_id and PLAY_GAME and text in ['y', 'n']:
        if text == 'n':
            send_message("Let's play again some other time!")
            PLAY_GAME = False
        else:
            send_message("Great! Let's play another round.\n"
                         "Enter:\nr for rock\np for paper\ns for scissors")
    
    LAST_MESSAGE_ID = message["id"]
    save_last_msg_id(LAST_MESSAGE_ID)

# determine winner of the game
def winner(player, bot):
    if player == bot:
        return "We tied!"
        
    elif (player == 'rock' and bot == 'scissors') or \
         (player == 'paper' and bot == 'rock') or \
         (player == 'scissors' and bot == 'paper'):
         return "You win!"
    else:
        return "I win!"

def main():
    global LAST_MESSAGE_ID
    
    LAST_MESSAGE_ID = load_last_msg_id()

    # this is an infinite loop that will try to read (potentially) 
    # new messages every 5 seconds, but you can change this to run 
    # only once or whatever you want
    while True:
        messages = get_group_messages(LAST_MESSAGE_ID)
        for message in reversed(messages):
            process_message(message)
        time.sleep(5)


if __name__ == "__main__":
    main()
    