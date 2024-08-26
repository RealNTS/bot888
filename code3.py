import discord
from discord.ext import commands, tasks
import serial
import pandas as pd
from datetime import datetime
import asyncio

TOKEN = 'your_bot_token'
CHANNEL_NAME = 'general'

ser = serial.Serial('COM3', 9600, timeout=1)  # Added timeout for better handling of reads
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
    while True:
        ser.reset_input_buffer()  # Clear any existing data in the input buffer
        data = ser.readline().decode('utf-8').strip()
        if data:
            break
        await asyncio.sleep(1)

    temperature, humidity = data.split(',')
    temperature = float(temperature.split(':')[1])
    humidity = float(humidity.split(':')[1])
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    thi = calculate_thi(temperature, humidity)

    return date_time, temperature, humidity, thi

@client.command()
async def check(ctx):
    try:
        date_time, temperature, humidity, thi = await get_measurement()
        await ctx.send(f'Temperature: {temperature}, Humidity: {humidity}, THI: {thi}, Date/Time: {date_time}')
    except Exception as e:
        await ctx.send(f"Error: {e}")

@client.command()
async def log(ctx):
    try:
        date_time, temperature, humidity, thi = await get_measurement()
        await ctx.send(f'Temperature: {temperature}, Humidity: {humidity}, THI: {thi}, Date/Time: {date_time}')
        data_log.append([date_time, temperature, humidity, thi])
    except Exception as e:
        await ctx.send(f"Error: {e}")

@client.command()
async def ex(ctx):
    if data_log:
        df = pd.DataFrame(data_log, columns=['Date/Time', 'Temperature', 'Humidity', 'THI'])
        file_path = r'C:\Users\Admin\Desktop\codad\temperature_humidity_log.xlsx'
        df.to_excel(file_path, index=False)
        with open(file_path, 'rb') as f:
            await log_channel.send("Data saved to Excel file.", file=discord.File(f, file_path))
    else:
        await ctx.send("No data to export.")

@tasks.loop(minutes=1)
async def periodic_measurement():
    now = datetime.now()
    if now.hour in [5, 8, 11, 14, 17, 20, 23] and now.minute == 0:
        try:
            date_time, temperature, humidity, thi = await get_measurement()

            await log_channel.send(f'Temperature: {temperature}, Humidity: {humidity}, THI: {thi}, Date/Time: {date_time}')
            data_log.append([date_time, temperature, humidity, thi])

            if now.hour == 23:
                df = pd.DataFrame(data_log, columns=['Date/Time', 'Temperature', 'Humidity', 'THI'])
                file_path = r'C:\Users\Admin\Desktop\codad\temperature_humidity_log.xlsx'
                df.to_excel(file_path, index=False)

                # Send the Excel file
                with open(file_path, 'rb') as f:
                    await log_channel.send("Data saved to Excel file.", file=discord.File(f, file_path))
                data_log.clear()

        except Exception as e:
            print(f"Error during periodic measurement: {e}")

client.run(TOKEN)
