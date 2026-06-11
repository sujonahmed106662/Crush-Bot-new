# 💕 Crush Proposal Bot

A production-ready Telegram Crush Proposal Bot built with **Aiogram 3.x**, **FastAPI**, **Firebase Firestore**, and a premium scrapbook-style website.

## Features

- 💝 Create unlimited crush proposal pages
- 🎨 Customize with emojis, music & backgrounds
- 📱 Premium scrapbook-style responsive website
- 😂 "No" button that runs away (desktop + mobile)
- 🎉 Confetti celebration on "Yes" click
- 📸 Auto-generated congratulations image (Pillow)
- 🔔 Telegram notifications when crush says YES
- 🔐 Admin panel with stats, broadcast, ban/unban

## Tech Stack

- **Bot**: Python, Aiogram 3.x
- **Web**: FastAPI, Jinja2, HTML/CSS/JS
- **Database**: Firebase Firestore
- **Image**: Pillow
- **Deploy**: Railway

## Project Structure

```
├── bot.py              # Telegram bot (Aiogram 3.x)
├── web.py              # FastAPI web server
├── database.py         # Firebase Firestore operations
├── firebase_config.py  # Firebase initialization
├── image_generator.py  # Pillow image generator
├── templates/
│   ├── home.html       # Landing page
│   ├── crush_page.html # Crush proposal page
│   └── admin.html      # Admin dashboard
├── static/
│   ├── css/crush.css   # Premium scrapbook styles
│   ├── js/crush.js     # Page interactions & animations
│   ├── images/         # Static images
│   └── music/          # Audio files
├── generated/          # Generated images
├── requirements.txt
└── Procfile            # Railway deployment
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram Bot Token from @BotFather |
| `ADMIN_ID` | Your Telegram User ID (for admin panel) |
| `FIREBASE_CREDENTIALS` | Firebase service account JSON (as string) |
| `RAILWAY_PUBLIC_DOMAIN` | Auto-set by Railway |

## Deployment on Railway

1. **Create a Firebase Project**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create a new project
   - Enable Firestore Database
   - Generate a service account key (JSON)

2. **Create a Telegram Bot**
   - Message @BotFather on Telegram
   - Use /newbot to create your bot
   - Copy the bot token

3. **Deploy to Railway**
   - Push this repo to GitHub
   - Connect to [Railway](https://railway.app)
   - Add environment variables:
     - `BOT_TOKEN` = your bot token
     - `ADMIN_ID` = your Telegram user ID
     - `FIREBASE_CREDENTIALS` = paste the entire Firebase JSON key as a single-line string

4. **Done!** Your bot is live.

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/help` | Show help message |
| `/create` | Create a new crush page |
| `/setemoji` | Set live emojis |
| `/setmusic` | Set background music |
| `/setbg` | Set background image |
| `/setmessage` | Change the message |
| `/mylinks` | View your links |
| `/delete` | Delete a link |
| `/stats` | Your statistics |
| `/admin` | Admin panel (admin only) |

## Admin Features

Access via `/admin` command in Telegram or visit `/admin` on the web:

- 📊 View bot statistics
- 📢 Broadcast messages
- 🚫 Ban/Unban users
- 🗑 Delete links
- 👤 User statistics lookup

## Firebase Collections

- `users` - Registered users
- `links` - Crush page links
- `views` - Page view records
- `yes_clicks` - Yes click records
- `settings` - Bot settings
- `banned_users` - Banned users
- `notifications` - Notification history

## License

MIT
