# Telegram Bots Repository

This repository contains two main projects: the **Message Forwarder Bot** and the **Settlement Verification Bot**.

## Message Forwarder Bot

This project includes a Telegram bot built with FastAPI, designed to forward messages between paired Telegram groups. The bot allows administrators to create, manage, and delete group pairs, facilitating seamless message forwarding.

### Features

- **Pairing Groups**: Administrators can set up pairs of groups for message forwarding.
- **Deleting Pairs**: Remove group pairs when they are no longer needed.
- **Viewing Pairs**: See a list of existing group pairs to manage forwarding settings easily.
- **User Whitelisting**: Whitelist specific users to exclude their messages from being forwarded across group pairs.
- **Removing Users from Whitelist**: Manage the whitelist to allow previously blocked users.
- **Automatic Message Forwarding**: Forwards messages automatically from one group to its paired group.

### Technology Stack

- **FastAPI**: A modern, fast web framework for building APIs with Python 3.6+ using standard type hints.
- **Telegram Webhook**: Handles incoming messages and updates from Telegram.

### Getting Started

#### Prerequisites

- Python 3.7+
- Docker (optional)

#### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/AbdulwahidHusein/MessgeMirror.git
   cd MessgeMirror
   ```


2. **Create a Virtual Environment**:
   - Run `python -m venv venv` to create a virtual environment.
   - Activate it:
     - On macOS/Linux: `source venv/bin/activate`
     - On Windows: `venv\Scripts\activate`

2. **Install Dependencies**:
   - Run `pip install -r requirements.txt` to install all required packages.

3. **Configure Environment Variables**:
   - Create a `.env` file by copying `.env.example` in the repository.
   - Fill in required values, such as the Telegram bot token and database configurations.

4. **Start the FastAPI Server**:
   - Run `uvicorn app:app --reload` to start the server with hot-reloading enabled.

5. **Run the Application**:
   You have two options to run the application:
   
   - **Using Uvicorn**:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port 8000 --reload
     ```
   - **Using Docker (optional)**:
     Run the bot in a Docker container with:
     ```bash
     docker run -d -p 8000:8000 --env-file .env abdusdocker/message_mirror
     ```

### Usage

After starting the bot, you can manage group pairs and user whitelisting through the following commands:

- **Add Pair**: Create a new group pair.
- **Remove Pair**: Delete an existing group pair.
- **Get Pairs**: View current group pairs.
- **Add to Whitelist**: Exclude a user from message forwarding.
- **Remove from Whitelist**: Remove a user from the whitelist.
- **Get Whitelist**: View all whitelisted users.

#### Settings Commands

- **Enable Mirroring**: Enables mirroring of messages across pairs.
- **Disable Mirroring**: Disables message mirroring.
- **Get Admins**: Lists bot administrators.
- **Delete Old Messages**: Deletes old messages from the database, cleaning up unreferenced data over time.

## Settlement Verification Bot

This bot is designed for settlement verification across groups. It verifies settlement requests sent between paired groups (Group A and Group B) to ensure consistency.

## How to setup 
Follow similar procedure as the mirror bot for setup
### Functionality

The bot checks that a settlement request in Group B matches an existing request in Group A. Based on this verification, the bot replies accordingly:

- **Verified**: The request is confirmed as matching.
- **Already Verified**: The request exists but has already been confirmed.
- **Not Confirmed**: The request exists, but the sender in Group A is not whitelisted.
- **Not Verified**: No matching request found in Group A.

### Management Commands

The bot provides a set of commands for management:

- **Add Group Pair**: Adds a new group pair. The bot lists the groups it is a member of for easy selection.
- **Remove Group Pair**: Deletes an existing group pair.
- **Get Group Pairs**: Lists current group pairs.
- **Add User to Whitelist**: Adds a user to the whitelist.
- **Remove User from Whitelist**: Removes a user from the whitelist.
- **Check Whitelisted Users**: Lists whitelisted users.
- **Settings**: Access bot settings and configuration options.

