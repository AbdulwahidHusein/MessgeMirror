# This reposittory Contains Two main Projects 



# Message Forwarder and Settlment Telegram Bot

This Project contains a Message Forwarder Telegram bot built using FastAPI. The bot allows administrators to create pairs of Telegram groups, enabling seamless message forwarding between them.

## Features

- **Pairing Groups**: Administrators can add pairs of groups for message forwarding.
- **Deleting Pairs**: Easily remove group pairs when they are no longer needed.
- **Viewing Pairs**: View existing group pairs to manage the forwarding settings effectively.
- **User whitelisting**: whitelist users to prevent their message from sent across group pairs.
- **Removing Users from whitelist**: Easily manage the whitelist and allow previously blocked users.
- **Message Forwarding**: Automatically forward messages from one group to the paired group.

## Technology Stack

This project utilizes:
- **FastAPI**: A modern, fast web framework for building APIs with Python 3.6+ based on standard Python type hints.
- **Telegram Webhook**: For handling incoming messages and updates from Telegram.

## Getting Started

### Prerequisites

- Python 3.7+
- Docker (optional)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. **Install Dependencies**:
   You can install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file based on the `.env.example` provided in the repository. Make sure to fill in the necessary variables, such as your Telegram bot token and database configuration.

4. **Run the Application**:
   You have two options to run the application:

   - **Using Uvicorn**:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port 8000 --reload
     ```
   - **Using Docker (optional)**:
     If you prefer to run the bot in a Docker container, use the following command:
     ```bash
     docker run -d -p 8000:8000 --env-file .env your-image-name
     ```

## Usage

Once the bot is running, you can interact with it via Telegram. Use the following commands to manage group pairs and user whitelisting:

- **Add Pair**: Add a new pair of groups.
- **Remove Pair**: Remove a group pair.
- **Get Pairs**: List existing group pairs.
- **Add to whitelist**: whitelist a user from sending messages.
- **Remove From whitelist**: Remove a user from the whitelist.
- **Get whitelist** : Get list of whitelisted users.
-  **Settings** : Get Settings
- ## under settigns
- **enable mirroring** : Enables mirroring
- **Disable mirroring**: Disables mirroring
- **Get Admins**: Get List of Admins
- **Delete Old Messages** : Deletes old messages saved to the database. This is useful for cleaning up the database since messages in the database are only used if there is a reply to them. This allows us to easily refer back to the original message. However, as time passes, a message becomes less likely to receive a reply, making it more suitable for deletion.


# Settlment Verification Bot

