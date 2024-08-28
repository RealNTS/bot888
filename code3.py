import discord
from discord.ext import commands, tasks
import serial
import pandas as pd
from datetime import datetime, timedelta
import asyncio

TOKEN = 'your_bot_token'
CHANNEL_NAME = 'general'
EXCEL_PATH = r'C:\Users\Admin\Desktop\codad\temperature_humidity_log.xlsx'

ser = serial.Serial('COM3', 9600, timeout=1)
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

data_log = []

def calculate_thi(temperature, humidity):
    return (temperature * 1.8 + 32) - (0.55 - 0.0055 * humidity) * ((temperature * 1.8 + 32) - 14.5)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    
    global log_channel
    log_channel = None
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.name == CHANNEL_NAME:
                log_channel = channel
                break
        if log_channel:
            break

    if log_channel:
        print(f'Logging channel set to: {log_channel.name} ({log_channel.id})')
    else:
        print(f'Channel named {CHANNEL_NAME} not found.')

    periodic_measurement.start()

async def get_measurement():
    """Try to get a measurement from the serial port until successful."""
    while True:
        ser.reset_input_buffer()
        data = ser.readline().decode('utf-8').strip()
        if data:
            try:
                temperature, humidity = data.split(',')
                temperature = float(temperature.split(':')[1])
                humidity = float(humidity.split(':')[1])
                date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                thi = calculate_thi(temperature, humidity
                )
                return date_time, temperature, humidity, thi
            except Exception as e:
                print(f"Error processing data: {e}")
        await asyncio.sleep(0.5)

@client.command()
async def check(ctx):
    """Check command to manually measure and display data without saving."""
    try:
        date_time, temperature, humidity, thi = await get_measurement()
        await ctx.send(f'Temperature: {temperature}, Humidity: {humidity}, THI: {thi}, Date/Time: {date_time}')
    except Exception as e:
        await ctx.send(f"Error: {e}")

@client.command()
async def log(ctx):
    """Log command to manually measure, display, and save data."""
    try:
        date_time, temperature, humidity, thi = await get_measurement()
        await ctx.send(f'Temperature: {temperature}, Humidity: {humidity}, THI: {thi}, Date/Time: {date_time}')
        data_log.append([date_time, temperature, humidity, thi])
    except Exception as e:
        await ctx.send(f"Error: {e}")

@client.command()
async def ex(ctx):
    """Export the logged data to an Excel file."""
    if data_log:
        df = pd.DataFrame(data_log, columns=['Date/Time', 'Temperature', 'Humidity', 'THI'])
        df.to_excel(EXCEL_PATH, index=False)
        with open(EXCEL_PATH, 'rb') as f:
            await log_channel.send("Data saved to Excel file.", file=discord.File(f, EXCEL_PATH))
    else:
        await ctx.send("No data to export.")

@tasks.loop(seconds=1)
async def periodic_measurement():
    now = datetime.now()
    # List of measurement times
    next_measurement_times = [datetime.now().replace(hour=h, minute=0, second=0, microsecond=0) for h in [5, 8, 11, 14, 17, 20, 23]]

    for measure_time in next_measurement_times:
        if now > measure_time:
            continue

        wait_time = (measure_time - now).total_seconds()
        await asyncio.sleep(wait_time)

        try:
            date_time, temperature, humidity, thi = await get_measurement()

            await log_channel.send(f'Temperature: {temperature}, Humidity: {humidity}, THI: {thi}, Date/Time: {date_time}')
            data_log.append([date_time, temperature, humidity, thi])

            # At 23:00, export the data and clear the log
            if measure_time.hour == 23:
                df = pd.DataFrame(data_log, columns=['Date/Time', 'Temperature', 'Humidity', 'THI'])
                df.to_excel(EXCEL_PATH, index=False)

                with open(EXCEL_PATH, 'rb') as f:
                    await log_channel.send("Data saved to Excel file.", file=discord.File(f, EXCEL_PATH))
                data_log.clear()

        except Exception as e:
            print(f"Error during periodic measurement: {e}")

client.run(TOKEN)
