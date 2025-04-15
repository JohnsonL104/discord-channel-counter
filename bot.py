import discord
from discord.ext import commands
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
from pytz import timezone  # Import timezone for EST


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_CHANNEL = os.getenv("COMMAND_CHANNEL")
SKIP_LINES_FILE = os.getenv("SKIP_LINES_FILE")

# Load SKIP_LINES from skip_lines.txt
if os.path.exists(SKIP_LINES_FILE):
    with open(SKIP_LINES_FILE, "r", encoding="utf-8") as file:
        SKIP_LINES = [line.strip() for line in file if line.strip()]
else:
    SKIP_LINES = []  # Default to an empty list if the file does not exist

# Initialize the bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.command(name="count")
async def count(ctx, channel_name: str):
    """Fetch all messages from the specified channel, count them, and generate a graph."""
    command_channel = os.getenv("COMMAND_CHANNEL")
    if ctx.channel.name != command_channel:
        await ctx.send(f"This command can only be used in the #{command_channel} channel.")
        return

    target_channel = discord.utils.get(ctx.guild.channels, name=channel_name)
    if not target_channel:
        await ctx.send(f"Channel #{channel_name} not found.")
        return

    est = timezone("US/Eastern")  # Define the EST timezone
    dates = []
    count = 0  # Initialize count for the first two messages

    # Parse the first two messages for counts
    async for message in target_channel.history(limit=None, oldest_first=False):
        content_lines = message.content.splitlines()
        count = 0  # Initialize count for the first two messages

        for line in content_lines:
            if not any(skip_line.lower() in line.lower() for skip_line in SKIP_LINES):
                count += 1
        
        dates.extend([message.created_at.astimezone(est)] * count)

    if not dates:
        await ctx.send(f"No messages found in #{channel_name}.")
        return

    # Generate the graph
    dates.sort()
    plt.figure(figsize=(10, 6))

    # Create a line chart by grouping messages by day
    daily_counts = {}
    for date in dates:
        day = date.date()
        daily_counts[day] = daily_counts.get(day, 0) + 1

    # Ensure every day in the range is included, including today, even if the count is zero
    start_date = dates[0].date()
    end_date = max(dates[-1].date(), datetime.now(est).date())  # Include today
    all_days = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    counts = [daily_counts.get(day, 0) for day in all_days]

    plt.plot(all_days, counts, color='red', linestyle='-')  # Red line, no dots
    plt.title(f"Messages Over Time in #{channel_name} (EST)")
    plt.xlabel("Date (EST)")
    plt.ylabel("Number of Messages")
    plt.grid(True)
    plt.tight_layout()

    # Save the graph to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    # Calculate statistics
    now = datetime.now(est)  # Use EST timezone for `now`
    last_24h = sum(1 for date in dates if date > now - timedelta(days=1))
    last_week = sum(1 for date in dates if date > now - timedelta(weeks=1))
    last_month = sum(1 for date in dates if date > now - timedelta(days=30))
    total_messages = len(dates)

    # Send the graph and statistics
    file = discord.File(buffer, filename="messages_graph.png")
    await ctx.send(
        f"Messages in the last 24 hours: {last_24h}\n"
        f"Messages in the last week: {last_week}\n"
        f"Messages in the last month: {last_month}\n"
        f"Messages over all time: {total_messages}\n",
        file=file
    )

@bot.command(name="validate")
async def validate(ctx, channel_name: str):
    """Validate the numbering of messages in the specified channel and report any issues."""
    
    if ctx.channel.name != COMMAND_CHANNEL:
        await ctx.send(f"This command can only be used in the #{COMMAND_CHANNEL} channel.")
        return

    target_channel = discord.utils.get(ctx.guild.channels, name=channel_name)
    if not target_channel:
        await ctx.send(f"Channel #{channel_name} not found.")
        return

    est = timezone("US/Eastern")  # Define the EST timezone
    expected_number = 1  # Start with the first expected number
    issues = []  # Collect issues for reporting
    seen_numbers = set()  # Track seen numbers to detect duplicates

    async for message in target_channel.history(limit=None, oldest_first=True):
        content_lines = message.content.splitlines()
        for line in content_lines:
            if not any(skip_line.lower() in line.lower() for skip_line in SKIP_LINES):
                # Extract the number at the start of the line until the first non-integer character
                number_str = ""
                for char in line.strip():
                    if char.isdigit():
                        number_str += char
                    else:
                        break
                if number_str:
                    number = int(number_str)

                    if number in seen_numbers:
                        # Record the issue if the number is a duplicate
                        issues.append(
                            f"User: {message.author}, Content: '{line}', Date: {message.created_at.astimezone(est)} - "
                            f"Duplicate number {number}"
                        )
                    else:
                        seen_numbers.add(number)

                    if not line.startswith(f"{number}.") and not line.startswith(f"{number} "):
                        # Record the issue if the line does not start with "{number}." or "{number} "
                        issues.append(
                            f"User: {message.author}, Content: '{line}', Date: {message.created_at.astimezone(est)} - "
                            f"Line does not start with '{number}.' or '{number} '"
                        )
                    elif number != expected_number:
                        # Record the issue if the number is not in order
                        issues.append(
                            f"User: {message.author}, Content: '{line}', Date: {message.created_at.astimezone(est)} - "
                            f"Expected {expected_number}, but found {number}"
                        )
                    expected_number = number + 1  # Increment the expected number

    if issues:
        # Send the issues back to the user
        await ctx.send("The following issues were found with the numbering:")
        for issue in issues:
            await ctx.send(issue)
    else:
        await ctx.send(f"All numbers are in order, properly formatted, and without duplicates in #{channel_name}.")

# Run the bot
bot.run(DISCORD_TOKEN)
