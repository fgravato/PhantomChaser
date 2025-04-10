# PhantomChaser
<p align="center">
  <img src="https://github.com/fgravato/PhantomChaser/blob/main/banner.png?raw=true" alt="phantom-chaser-logo"/>
</p>

# Discord Bot for Kicking Admin Impersonators

This Discord bot is designed to automatically kick members who are impersonating the server owner or admins in Discord servers. It identifies potential impersonators by comparing their usernames, nicknames, and profile pictures with the server's administrators using regular expressions and image similarity. Made by Sehaj (dxstiny) and Aman (r3sist).

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- A Discord account with permission to add bots to servers
- A Discord bot token (see below)

### Step 1: Clone the Repository

```bash
git clone git@github.com:fgravato/PhantomChaser.git
cd PhantomChaser
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

If the requirements.txt file is not available, install the required packages manually:

```bash
pip install discord.py python-dotenv requests Pillow imagehash python-Levenshtein
```

### Step 3: Set Up Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Under the "TOKEN" section, click "Copy" to copy your bot token
5. Create a file named `.env` in the root directory of the project
6. Add the following line to the `.env` file:
   ```
   bot_token=YOUR_BOT_TOKEN_HERE
   ```
   Replace `YOUR_BOT_TOKEN_HERE` with the token you copied

### Step 4: Invite the Bot to Your Server

1. In the Discord Developer Portal, go to the "OAuth2" tab
2. In the "OAuth2 URL Generator" section, select the "bot" scope
3. Select the following permissions:
   - Kick Members
   - Manage Channels
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
4. Copy the generated URL and open it in your browser
5. Select the server you want to add the bot to and click "Authorize"

Alternatively, you can use this URL to invite the bot to your server (if it's already hosted): [Invite](https://discord.com/api/oauth2/authorize?client_id=1104343553875914793&permissions=402655382&scope=bot) (Note: This link may need to be updated for the new bot)

### Step 5: Run the Bot

```bash
python bot.py
```

The bot should now be running and will output "Bot connected as [bot name]" when successfully connected to Discord.

### Step 6: Server Setup

1. **Invite the Bot**: Use the provided URL to invite the bot to your Discord server. Make sure to give access to every permission the bot requires.
2. **Set Up Bot Permissions**: After inviting the bot, ensure that the bot has a role with sufficient permissions to kick members.
3. **Set Role Hierarchy**: The bot's role should have higher hierarchy than the roles of potential impersonators, meaning most members. Go to server settings --> roles --> drag the role of the bot "PhantomChaser" to the top below admin role. (drag above by clicking the left button as shown below)

![Role Hierarchy Setup](https://github.com/r3sist-uniq/ImposterSecurityBot/assets/72573738/462e2332-7875-4d68-9e03-4434b6d74c1f)

### Configuration

The bot now supports server-specific configuration to customize the impersonation detection sensitivity. Administrators can use the following commands:

- `!config view` - View current configuration settings
- `!config set levenshtein <value>` - Set the Levenshtein distance threshold (1-5)
  - This controls how similar usernames need to be to trigger detection
  - Lower values (e.g., 1-2) = Stricter matching (fewer false positives)
  - Higher values (e.g., 3-5) = Looser matching (catches more potential impersonators)
- `!config set similarity <value>` - Set the image similarity threshold (0.5-1.0)
  - This controls how similar profile pictures need to be to trigger detection
  - Higher values (e.g., 0.9-1.0) = Stricter matching (profile pictures must be very similar)
  - Lower values (e.g., 0.5-0.7) = Looser matching (more profile pictures will be considered similar)
- `!config reset` - Reset to default configuration values

Example usage:
```
!config view
!config set levenshtein 2
!config set similarity 0.85
```

## How it works

### Impersonator Detection

The bot periodically (every 10 seconds) checks all the guilds (servers) it is a member of for potential impersonators. It compares the usernames and nicknames of each member with all administrators' information using:

1. Regular expressions for exact pattern matching
2. Levenshtein distance for measuring string similarity
3. Image hashing for profile picture comparison

### Tiered Response System

The bot uses a tiered approach to handle potential impersonators:

1. **Automatic Kick**: For exact matches or close matches with similar profile pictures
2. **High Alert**: For close matches but different profile pictures
3. **Low Alert**: For somewhat similar names

Alerts are sent to dedicated channels:
- `impersonation-alerts`: For notifications about kicked impersonators
- `impersonation-assist`: For alerts about suspicious users that require admin review

### Configuration

Server administrators can customize the detection sensitivity using the following commands:

- `!config view` - View current configuration
- `!config set levenshtein <value>` - Set Levenshtein distance threshold (1-5)
  - Lower values = stricter matching (fewer false positives but might miss some impersonators)
  - Higher values = looser matching (catches more potential impersonators but may have more false positives)
- `!config set similarity <value>` - Set image similarity threshold (0.5-1.0)
  - Higher values = stricter matching (profile pictures must be more similar to trigger)
- `!config reset` - Reset to default configuration

### Algorithms

We use the following algorithms to detect impersonation:

- [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance): Measures the difference between two strings (usernames/nicknames)
- [Hamming Distance](https://en.wikipedia.org/wiki/Hamming_distance): Used with image hashing to compare profile pictures
- Regular expressions: For exact pattern matching of usernames with special characters

## Alert Channels

The bot creates and uses two channels for alerts:

1. **impersonation-alerts**: Contains notifications about users who were automatically kicked for impersonation
2. **impersonation-assist**: Contains alerts about suspicious users that require admin review

These channels are created automatically with appropriate permissions when needed.

## Examples

### Example 1: Exact Username Match

If a user joins with exactly the same username as an admin (or with special characters inserted), they will be automatically kicked and an alert will be sent to the `impersonation-alerts` channel.

### Example 2: Similar Username

If a user joins with a username that is similar to an admin (based on Levenshtein distance), the bot will:
- Kick them if their profile picture is also similar to the admin's
- Send a high alert if their username is very similar but profile picture is different
- Send a low alert if their username is somewhat similar

### Example 3: Configuring Sensitivity

If you're getting too many false positives:
```
!config set levenshtein 1
!config set similarity 0.95
```

If you want to catch more potential impersonators:
```
!config set levenshtein 3
!config set similarity 0.8
```

## Support and Issues

If you encounter any issues or need support, feel free to contact the developer of the bot or open an issue in the bot's repository.

## Contribute

If you want to improve the bot's functioning, please create a pull request.

## Disclaimer

This bot is provided as-is without any warranty. The developer of the bot is not responsible for any misuse or damage caused by the bot. Use it responsibly and in accordance with Discord's terms of service.
