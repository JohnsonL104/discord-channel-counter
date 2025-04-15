# Discord Channel Counter

Discord Channel Counter is a Discord bot designed to analyze and validate specific channels used for counting items. Messages in the channel must follow the following format, where each line starts with a number followed by a period or space:

```
1. Some item
2. Other item
3 Another item
```

## Features

- **Count Messages**: Count messages in a specified channel, generate a graph of message activity over time, and provide statistics.
- **Validate Messages**: Validate the numbering of messages in a specified channel, ensuring proper formatting, sequential numbering, and no duplicates.
- **Customizable Skip Lines**: Define lines to skip during counting and validation using a `skip_lines.txt` file.

## Requirements

- Python 3.10 or higher
- Discord bot token
- The following Python packages (listed in `requirements.txt`):
  - `discord.py`
  - `matplotlib`
  - `pytz`

## Setup

1. Clone the repository or copy the project files to your local machine.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project directory and add the following environment variables:
   ```dotenv
   DISCORD_TOKEN=your_discord_bot_token
   COMMAND_CHANNEL=your_command_channel_name
   SKIP_LINES_FILE=skip_lines.txt
   ```
   Replace `your_discord_bot_token` with your bot's token and `your_command_channel_name` with the name of the channel where commands can be used.

4. Create a `skip_lines.txt` file in the project directory and add lines to skip during counting and validation. For example:
   ```plaintext
   Some line to skip in counting and validation
   Another line to skip in counting and validation
   ```

5. Run the bot:
   ```bash
   python bot.py
   ```

## Commands

### `!count <channel_name>`
Fetch all messages from the specified channel, count them, and generate a graph of message activity over time.

- **Arguments**:
  - `<channel_name>`: The name of the channel to analyze.
- **Example**:
  ```plaintext
  !count <channel_name>
  ```

### `!validate <channel_name>`
Validate the numbering of messages in the specified channel and report any issues.

- **Arguments**:
  - `<channel_name>`: The name of the channel to validate.
- **Example**:
  ```plaintext
  !validate <channel_name>
  ```

## Customization

### Skip Lines
You can customize the lines to skip during counting and validation by editing the `skip_lines.txt` file. Each line in the file represents a pattern to skip.

### Command Channel
The bot restricts the use of commands to a specific channel. You can configure this by setting the `COMMAND_CHANNEL` environment variable in the `.env` file.

## Docker Support

To containerize the bot, use the provided `Dockerfile`:

1. Build the Docker image:
   ```bash
   docker build -t discord-channel-counter .
   ```
2. Run the container:
   ```bash
   docker run -e DISCORD_TOKEN=your_discord_bot_token -e COMMAND_CHANNEL=your_command_channel_name -e SKIP_LINES_FILE=skip_lines.txt discord-channel-counter
   ```