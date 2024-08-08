# Discord Server Management Bot

This is a Discord bot designed to help manage servers. It includes features such as a small Wordle game, message tracking, voice channel activity tracking, and support for temporary voice channels. The project is managed using Poetry for dependency management and environment handling.

## Features

- **Server Management**: General tools to help manage Discord servers.
- **Wordle Game**: A fun mini-game where users can play Wordle within the Discord server.
- **Message Tracker**: Keeps track of the number of messages sent by users.
- **Voice Channel Tracker**: Tracks the time users spend in voice channels and handles temporary voice channels.
- **And many more features!

## Requirements

- Python 3.10 or higher
- Poetry

## Installation

1. **Clone the repository**:

    ```bash
    git clone <your-repo-url>
    cd your-repo-directory
    ```

2. **Install Poetry**:

    If you don't have Poetry installed, you can install it by following the instructions on the [Poetry installation page](https://python-poetry.org/docs/#installation).

    Example installation command:

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. **Install dependencies**:

    ```bash
    poetry install
    ```

4. **Set up environment variables**:

    Create a `.env` file in the root of your project and add the following environment variables:

    ```txt
    TOKEN="your-discord-bot-token" (as a string!)
    ```

## Running the Bot

1. **Activate the virtual environment**:

    ```bash
    poetry shell
    ```

2. **Run the bot**:

    ```bash
    poetry run python -m main.py
    ```

## Project Structure

```txt
LEGENDARYBOT/
├── pyproject.toml
├── poetry.lock
├── .env
├── README.txt
├── main.py
├── logs/
│   ├── info.log
├── modules/
│   ├── __init__.py
│   ├── WordleGame.py
│   ├── LevelSystem.py
│   ├── GuildLogging.py
│   ├── TemporaryVoiceChannel.py
│   └── ...
├── tests/
│   ├── __init__.py
│   └── ...
├── utils/
│   ├── __init__.py
│   └── ...
└── constants/
    └── __init__.py

The modules entail anything that is a cog, ergo a part (module) that discord can use. Like commands or events. 
Utils is a directory where internal logic is kept, so that the commands in the modules stay nice clean and compact. Furthermore this allows for the functionalities to be used again.
Tests can be found in the tests directory.
main.py is where the bot is run from.
In the constants directory I try to keep everything that is not supposed to be changed, like ENUMS and filepaths (TODO!) and the emojis for the wordle mini game.