import speech_recognition as sr
import pyttsx3
import openai
from textblob import TextBlob
import time
import homeassistant as ha
import pysmartthings
import wikipedia
import random
from googletrans import Translator
import requests
import json
import webbrowser
import pyjokes
import calendar
import datetime
import threading
import pytz
import functools
import os.path
import os
import emoji
import sounddevice as sd
from scipy.io.wavfile import write
from io import BytesIO
from PIL import Image


# initialize speech recognition and pyttsx3 engines
r = sr.Recognizer()
engine = pyttsx3.init()


# API keys and settings
openai.api_key = ""
voice = engine.getProperty('voices')[1]
engine.setProperty('voice', voice.id)
engine.setProperty('rate', 180)  # Adjusts the speaking rate, default is 200
engine.setProperty('volume', 1.0)  # Adjusts the speaking volume, default is 1.0

# create microphone object
microphone = sr.Microphone()

# Define a function to speak the given text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Define a function to generate a response with an image prompt using ChatGPT-3 and DALL-E AI
def generate_response(prompt):
    # Use ChatGPT-3 to generate a response
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.7,
    )
    # Get the text from the response
    text = response.choices[0].text.strip()
    
    # Use ChatGPT-3 to add emojis to the text
    emoji_response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Add emojis to this text: {text}",
        max_tokens=16,
        temperature=0.5,
    )
    emojis = emoji_response.choices[0].text.strip()
    text_with_emojis = text + " " + emojis

    # Speak the response
    speak(text_with_emojis)

    # Use DALL-E AI to generate an image with the prompt
    data = {
        "model": "image-alpha-001",
        "prompt": text_with_emojis,
        "num_images": 1,
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {dalle_api_key}"}
    response = requests.post(dalle_api_url, json=data, headers=headers)
    response.raise_for_status()

    # Get the image from the response
    image_url = response.json()["data"][0]["url"]
    image_response = requests.get(image_url)
    image_response.raise_for_status()

    # Display the image to the user
    image = Image.open(BytesIO(image_response.content))
    image.show()

    # Return the text response
    return text_with_emojis

# Add emojis to the response
def add_emojis(text):
    emoji_response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Add emojis to this text: {text}",
        max_tokens=16,
        temperature=0.5,
    )
    emojis = emoji_response.choices[0].text.strip()
    text_with_emojis = text + " " + emojis
    return text_with_emojis

def respond(input):
    responses = [
        "😀", "😃", "😄", "😁", "😆", "😊", "😋", "😎", "😍", "😘",
        "😜", "😝", "😛", "🤑", "🤗", "🤔", "🤐", "🤓", "😏", "😒",
        "😞", "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫", "😩",
        "😤", "😠", "😡", "😶", "😐", "😑", "🤒", "🤕", "😷", "🤢",
        "🤮", "😨", "😰", "😥", "😭", "😱", "😳", "😵", "🥶", "🥵",
        "🤯", "😴", "💩", "👻", "👽", "🤖", "💀", "👍", "👎", "👊",
        "✊", "🤛", "🤜", "🤞", "✌️", "🤘", "👌", "👈", "👉", "👆",
        "👇", "☝️", "👋", "🤚", "🖐️", "✋", "👏", "🙌", "👐", "💪",
        "🦾", "🦿", "🦵", "🦶", "👂", "🦻", "👃", "🧠", "🦷", "🦴",
        "👀", "👁️", "👅", "👄", "💋", "🩸", "💉", "💊", "🩹", "🧬",
        "🦠", "🧫", "🧪", "🌡️", "🌬️", "💨", "💦", "🌊", "🔥", "🌪️",
        "🌈", "☀️", "⛅", "☁️", "❄️", "🌧️", "💧", "🌹", "🌺", "🌸",
        "🌻", "🌼", "🌷", "🌱", "🌲", "🌳", "🌴", "🌵", "🌾", "🌿",
        "🍁", "🍂", "🍃", "🍇", "🍈", "🍉", "🍊", "🍋", "🍌", "🍍",
        "🥭", "🍎", "🍏", "🍐", "🍑", "🍒", "🍓", "🥝", "🍅", "🥑"
        "🚨", "🚒", "🚑", "🚓", "🚔", "🚑🏥", "🆘", "🆘🚨", "🆘🆘", "🚨🚑",
        "🚒👨‍🚒", "👩‍🚒🔥", "👮‍♂️👮‍♀️", "👩‍⚕️🩺", "👨‍⚕️🚑", "🚨🆘👮‍♂️", "🚓🚨👮‍♂️", "👩‍🚒👨‍🚒🚒", "🚑🏥💉", "🚨🚓🚑"
    ]

    gpt_response = openai.Completion.create(
        engine="davinci",
        prompt=input,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7,
    )
    response_text = gpt_response.choices[0].text.strip()

    # Choose a random emoji from the list
    chosen_emoji = random.choice(responses)
    
    # Combine the text and the emoji
    response_with_emoji = f"{response_text} {chosen_emoji}"
    
    return response_with_emoji


# Define a function to transcribe speech using OpenAI's Speech to Text API
def recognize_speech():
    try:
        # use the microphone as the audio source
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)

        # recognize speech using OpenAI's Speech to Text API
        response = openai.Completion.create(
            engine="davinci",
            prompt=f"Transcribe the following audio: {audio.get_wav_data()}",
            max_tokens=2048,
            n=1,
            stop=None,
            temperature=0.5,
        )

        if response.choices[0].text:
            text = response.choices[0].text.strip()
            print(f"You said: {text}")
            return text.lower()
        else:
            print("OpenAI Speech Recognition could not understand audio")
            return ""

    except sr.UnknownValueError:
        print("OpenAI Speech Recognition could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from OpenAI Speech Recognition service; {e}")
        return ""




# Use OpenAI API to generate a caption for the image
caption_prompt = f"Describe the image in one sentence: {image_url}"
caption_response = openai.Completion.create(
    engine="davinci",
    prompt=caption_prompt,
    max_tokens=32,
    temperature=0.5,
)
caption = caption_response.choices[0].text.strip()

# function to set the wake phrase
def set_wake_word():
    wake_word = None
    while not wake_word:
        speak("Please say your desired wake phrase.")
        audio = recognize_speech()
        try:
            print("You said: ", audio)
            speak(f"Setting your wake phrase to {audio}")
            wake_word = audio.lower()
        except:
            speak("Sorry, I didn't understand that. Please try again.")
    return wake_word


# function to get user's name
def get_name(wake_word, recognizer):
    name = None
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)  # adjust the recognizer sensitivity to ambient noise
        while not name:
            audio = recognizer.listen(source)
            try:
                # check if wake word is detected before capturing user's name
                text = recognizer.recognize_google(audio)
                if wake_word.lower() in text.lower():
                    speak("What's your name?")
                    audio = recognizer.listen(source)
                    name = recognizer.recognize_google(audio)
                    speak(f"Nice to meet you, {name}.")
                else:
                    time.sleep(1)  # wait for 1 second before checking again
            except sr.UnknownValueError:
                speak("Sorry, I didn't understand that. Please try again.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
    return name


# function for customizing settings
def customize():
    speak("How many minutes do you want to wait before sleeping?")
    audio = recognize_speech()
    try:
        minutes = int(audio)
        speak(f"Setting sleep timer to {minutes} minutes.")
    except ValueError:
        speak("Sorry, I didn't understand that. Please try again.")
        

# set the wake phrase
wake_word = set_wake_word()

# get the user's name
recognizer = sr.Recognizer()
name = get_name(wake_word, recognizer)

# customize settings
speak("Do you want to customize any settings?")
audio = recognize_speech()
if "yes" in audio.lower():
    customize()



model_path = "models/345m"

secrets = {
    "cc52d7e9-26d8-44f4-9302-dbd416eed7e6": "your_api_key_here"
}

# Fetching DoorDash API Keys
api_key = secrets[""]


# OpenAI GPT-3 model
model_engine = "davinci"  # or "curie", "babbage", etc. depending on the model you're using



# Get restaurant details from DoorDash API
def get_restaurant_details(location, cuisine):
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "query": location,
        "type": "ADDRESS",
    }
    response = requests.get("https://api.doordash.com/v2/addresses", headers=headers, params=params)
    address_json = json.loads(response.text)
    latitude = address_json['addresses'][0]['latitude']
    longitude = address_json['addresses'][0]['longitude']
    params = {
        "lat": latitude,
        "lng": longitude,
        "query": cuisine,
    }
    response = requests.get("https://api.doordash.com/v2/restaurant-locations/", headers=headers, params=params)
    restaurant_json = json.loads(response.text)
    return restaurant_json

# Get restaurant menu from DoorDash API
def get_restaurant_menu(restaurant_id):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(f"https://api.doordash.com/v2/restaurant/{restaurant_id}/menu", headers=headers)
    menu_json = json.loads(response.text)
    return menu_json

# Get user input
def get_user_input():
    prompt = "What food would you like to order from DoorDash?"
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=60,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

# Order food from DoorDash
def start_ordering_food():
    # Get user input
    print("What food would you like to order from DoorDash?")
    response = openai.Completion.create(
        engine=model_engine,
        prompt="",
        max_tokens=60,
        n=1,
        stop=None,
        temperature=0.7,
    )
    user_order = response.choices[0].text.strip()

    # Get location input
    print("What is your location?")
    location = input()

    # Get cuisine input
    print("What type of cuisine do you want to order?")
    cuisine = input()

    # Order food
    order_food(location, cuisine, user_order)


def order_food(location, cuisine, user_order):
    restaurant_details = get_restaurant_details(location, cuisine)
    if not restaurant_details:
        print("Sorry, no restaurants found!")
        return
    restaurant_id = restaurant_details['locations'][0]['id']
    restaurant_menu = get_restaurant_menu(restaurant_id)
    if not restaurant_menu:
        print("Sorry, the restaurant does not have any menus!")
        return
    print("Menu for the restaurant is:")
    for menu in restaurant_menu:
        print(menu['name'])
    print(f"You want to order {user_order}")
    # Place the order here
    print("Order has been placed successfully!")



# adjust the recognizer sensitivity to ambient noise and record audio from the microphone
def record_audio():
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        recognizer.energy_threshold = 500
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8
        recognizer.phrase_threshold = 0.4
        recognizer.non_speaking_duration = 0.4
        recognizer.operation_timeout = None
        recognizer.samplerate = 48000
        recognizer.chunksize = 2048
        audio = recognizer.listen(source, phrase_time_limit=10)
    return audio

def sleep_timer(minutes=15):
    time.sleep(minutes * 60)
    customize()

def sleep(seconds=1):
    time.sleep(seconds)

# Greeting message
def greet():
    messages = [
        "Hello! I'm your personal chatbot. How can I assist you today?",
        "Hi there! What can I help you with?",
        "Hey, how can I assist you today?",
        "Greetings! What can I do for you?",
    ]
    message = random.choice(messages)
    print(message)
    speak(message)

# Error handling
def handle_error():
    messages = [
        "Sorry, I couldn't understand you. Could you please rephrase your request?",
        "I didn't quite get that. Could you please repeat it?",
        "I'm sorry, I didn't understand. Could you try again?",
        "I didn't catch that. Could you please rephrase your request?",
    ]
    message = random.choice(messages)
    print(message)
    speak(message)


# Goodbye message
def goodbye():
    messages = [
        "Goodbye! Have a nice day.",
        "Bye for now!",
        "See you later!",
        "Farewell, have a great day!",
    ]
    message = random.choice(messages)
    print(message)
    speak(message)

# Turn on/off switch
def control_switch(platform, entity_id, status):
    if status == "on":
        ha.call_service(platform, "turn_on", {"entity_id": entity_id})
        messages = [
            "Okay, turning on switch.",
            "Switch is now turned on.",
            "Turning on switch, please wait.",
            "Switch activated.",
        ]
        message = random.choice(messages)
        print(message)
        speak(message)
    elif status == "off":
        ha.call_service(platform, "turn_off", {"entity_id": entity_id})
        messages = [
            "Okay, turning off switch.",
            "Switch is now turned off.",
            "Turning off switch, please wait.",
            "Switch deactivated.",
        ]
        message = random.choice(messages)
        print(message)
        speak(message)


# Sentiment analysis
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0.5:
        print("You sound very positive!")
        speak("You sound very positive!")
    elif sentiment > 0:
        print("You sound negative.")
        speak("You sound negative.")
    else:
        print("You sound neutral.")
        speak("You sound neutral.")

# Device authorization
def authorize_device(device):
    if device == "wemo":
        print("Please sign in to your WeMo account.")
        # code to sign in to WeMo account
    elif device == "lifx":
        print("No authorization required for LIFX devices.")
    else:
        print("Device not supported.")

# Natural language processing with natural language generation
def process_text(text):
    prompt = "You: " + text + "\nAI:"
    response = generate_response(prompt)
    return response


# Define a function to recognize the user's voice
def recognize_user():
    with sr.Microphone() as source:
        print("Please say your name.")
        audio = recognizer.listen(source)
        try:
            name = recognizer.recognize_google(audio)
            print(f"Hello, {name}!")
            return name
        except sr.UnknownValueError:
            print("I'm sorry, I didn't catch your name.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

# Define a function to personalize responses based on the user's name
def personalize_response(text, name):
    if name:
        return text.replace("you", name)
    else:
        return text


# Weather forecasting function
def get_weather(city):
    api_key = "7f98e9d2056b8cdd04f561fdc0e5ac0f"
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(base_url)
    data = json.loads(response.text)
    temperature = data["main"]["temp"]
    weather_description = data["weather"][0]["description"]
    message = f"The temperature in {city} is {temperature} Kelvin and the weather is {weather_description}."
    print(message)
    speak(message)

# News update function
def get_news():
    api_key = "74d04a62892c4cf09503bd06e015a300"
    base_url = f"http://newsapi.org/v2/top-headlines?country=us&apiKey=74d04a62892c4cf09503bd06e015a300"
    response = requests.get(base_url)
    data = json.loads(response.text)
    articles = data["articles"]
    for article in articles:
        title = article["title"]
        description = article["description"]
        message = f"{title}: {description}."
        print(message)
        speak(message)

#Reminder
def set_reminder(time_str, message):
    try:
        reminder_time = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        reminder_time = pytz.utc.localize(reminder_time)
    except ValueError:
        return "Invalid time format! Please provide time in the format: yyyy-mm-dd HH:MM:SS"

    now = datetime.datetime.now(pytz.utc)
    if reminder_time < now:
        return "Invalid time! Please provide a future time."

    time_diff = (reminder_time - now).total_seconds()
    reminder_timer = threading.Timer(time_diff, remind, args=[message])
    reminder_timer.start()

    return "Reminder set for {}.".format(time_str)

def remind(message):
    print("Reminder:", message)

# Weather forecasting

def get_weather_forecast(location):
    api_key = "7f98e9d2056b8cdd04f561fdc0e5ac0f"
    url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(location, api_key)
    response = requests.get(url)
    weather_data = response.json()
    current_temp = round(weather_data["main"]["temp"] - 273.15, 1)
    condition = weather_data["weather"][0]["description"]
    return "The current temperature in {} is {} degrees Celsius and the weather condition is {}.".format(location, current_temp, condition)

#Calender
def get_calendar_events(date):
    events = []
    now = datetime.datetime.now()
    if date.month == now.month:
        cal = calendar.monthcalendar(now.year, now.month)
        week_number = (date.day-1)//7
        weekday_number = date.weekday()
        day_number = cal[week_number][weekday_number]
        for event in calendar.monthcalendar(now.year, now.month):
            if event[weekday_number] == day_number:
                events.append(" ".join(str(day) for day in event if day != 0))
        if not events:
            return "No events found for {}.".format(date.strftime("%B %d, %Y"))
        else:
            return "Events for {}: {}".format(date.strftime("%B %d, %Y"), ", ".join(events))
    else:
        return "Invalid date! Please provide a date in the current month."

# Sleep Patterns
def add_sleep_data(start_time, end_time):
    start = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    sleep_time = (end - start).total_seconds() / 3600
    # Save sleep data to a database or file
    return "You slept for {} hours.".format(round(sleep_time, 1))

def suggest_sleep_improvements():
    # Analyze sleep data and suggest improvements
    return "Based on your sleep patterns, you should try going to bed earlier and avoid using electronic devices before sleeping."

# Joke function
def tell_joke():
    joke = pyjokes.get_joke()
    print(joke)
    speak(joke)

# Define a function to handle user preferences
def set_user_preferences():
    print("Let's set up your chatbot preferences.")
    # Ask the user for their preferred language
    language = input("What is your preferred language? ")
    # Ask the user for their preferred tone of voice
    tone = input("What is your preferred tone of voice? ")
    # Ask the user for their preferred topics
    topics = input("What topics are you interested in? ")
    # Store the user's preferences in a dictionary
    preferences = {
        "language": language,
        "tone": tone,
        "topics": topics
    }
    # Print a confirmation message
    print("Thank you! Your preferences have been saved.")
    return preferences

# Define a function to handle interactions with the chatbot
def chatbot():
    # Initialize the user's preferences to None
    preferences = None
    # Loop until the user sets their preferences
    while not preferences:
        try:
            preferences = set_user_preferences()
        except Exception as e:
            # Handle errors with a helpful message
            print(f"Error setting preferences: {e}. Please try again.")
    # Use the user's preferences to customize the chatbot's responses
    print(f"Hello! Welcome to the chatbot. Your preferred language is {preferences['language']}, your preferred tone of voice is {preferences['tone']}, and you're interested in {preferences['topics']}. How can I assist you today?")

# Task Management
tasks = {}

def create_task(name, assignee):
    tasks[name] = assignee
    print(f"{name} task created and assigned to {assignee}.")

def update_task(name, assignee):
    if name in tasks:
        tasks[name] = assignee
        print(f"{name} task updated and assigned to {assignee}.")
    else:
        print(f"{name} task not found.")

def delete_task(name):
    if name in tasks:
        del tasks[name]
        print(f"{name} task deleted.")
    else:
        print(f"{name} task not found.")

def list_tasks():
    for task in tasks:
        print(f"{task}: {tasks[task]}")

#News And Updates
news = []

def add_news(title, content):
    news.append((title, content))
    print(f"{title} added to news.")

def delete_news(title):
    for item in news:
        if item[0] == title:
            news.remove(item)
            print(f"{title} deleted from news.")
            return
    print(f"{title} not found in news.")

def list_news():
    for item in news:
        print(item[0] + ": " + item[1])


# Main loop
def main():
    greet()

    # Start sleep mode
    speak("Sleep mode activated. I am now listening for the wake phrase.")
    while True:
        audio = recognize_speech()
        if wake_word in audio:
            speak("How can I assist you?")
            break

     # set the wake word
    wake_word = set_wake_word()

    # get the user's name
    recognizer = sr.Recognizer()
    name = get_name(wake_word, recognizer)

    # start the conversation with ChatGPT3
    print(f"Hello, {name}! How can I assist you today?")

    while True:
        # Listen for user input
        text = recognize_speech()
        if not text:
            continue
        if "exit" in text.lower() or "goodbye" in text.lower():
            goodbye()
            break
        elif "personality" in text.lower() or "customize" in text.lower():
            customize_personality()
        elif "weather" in text.lower() or "forecast" in text.lower():
            city = "your_city_here"
            get_weather(city)
        elif "news" in text.lower() or "update" in text.lower():
            get_news()
        elif "joke" in text.lower() or "funny" in text.lower():
            tell_joke()
        elif "music" in text.lower() or "play" in text.lower():
            play_music()
        elif "order food" in text.lower():
            start_ordering_food()
        else:
            response = process_text(text)
            if response:
                print("I think you said: ", response)
                speak(response)
                analyze_sentiment(text)


if __name__ == '__main__':
    wake_word = "hey"
    while True:
        audio = recognize_speech()
        if wake_word.lower() in audio:
            name = get_name(wake_word)
            if name:
                print(f"Hello, {name}!")
                sleep_timer()
    main()

         
