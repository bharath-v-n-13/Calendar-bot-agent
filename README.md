# 📅 Calendar Bot Agent

A smart personal productivity assistant for Telegram that integrates directly with your Google Calendar, powered by the cutting-edge **Gemini 2.5 Flash** AI model. 

This agent uses Natural Language Processing to manage your calendar events without lifting a finger. Just send a message on Telegram like "Add lunch with Ajay at 12pm tomorrow," and it will seamlessly interact with the Google Calendar API to schedule the event for you.

## ✨ Features
* **Smart Event Scheduling**: Add tasks or events to your Google Calendar using natural language.
* **Event Lookup**: Ask to see your upcoming tasks, or search across *all* your subscribed calendars to answer questions like *"When is Diwali?"* or *"Show me upcoming festivals."*
* **Delete Events**: Delete events easily via Telegram chat (e.g., *"Delete the meeting with client"*).
* **Save Quick Notes**: Ask the bot to save quick text snippets in memory.
* **Time Check**: Instantly recall the current date and time (in UTC standard).

---

## 🚀 Setup & Installation

### 1. Prerequisites
You will need Python installed on your system along with the dependencies listed in `requirements.txt`.

```bash
git clone https://github.com/bharath-v-n-13/Calendar-bot-agent.git
cd Calendar-bot-agent
pip install -r requirements.txt
```

### 2. Environment Variables (.env)
You must create a `.env` file in the root directory. This contains your secret keys that allow your bot to run on Telegram and use the Gemini engine.

Create `.env` and configure it like this:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```
> *Keep this file safe and never commit it to public repositories.*

### 3. Google Calendar API Setup (`credentials.json`)
The bot talks to the real Google Calendar API securely via OAuth2 desktop app authentication.
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a Project -> Go to **APIs & Services > Library** and Enable the **Google Calendar API**.
3. Go to **OAuth consent screen** and set it up (add your email to "Test Users" if the app is in Testing mode).
4. Go to **Credentials**, click **Create Credentials** -> **OAuth client ID**, select **Desktop app**.
5. Download the JSON file and save it in the root folder of this project named exactly: `credentials.json`

### 4. Authenticate Google Calendar
Before running the bot for the first time, you must authorize it to access your specific calendar:
```bash
python auth.py
```
A browser window will open. Select your Google account, bypass the "Unverified App" warning (since you are the developer), and click **Allow**. This generates a completely secure `token.json` file on your computer.

### 5. Start the Agent
Once you have `.env`, `credentials.json`, and `token.json`, you can spin up the bot! 

```bash
python main.py
```

Message your Bot on Telegram and say: **"Show my tasks!"** or **"Schedule a dentist appointment next Friday at 11am!"**