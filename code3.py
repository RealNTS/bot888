import discord
import serial
import pandas as pd
from datetime import datetime

# Discord bot setup
TOKEN = 'MTI2MjgxOTgxMDk4MzY3Mzg1Ng.GgZOkz.bLZuqvakRQG4o2_AID7gJoHfkIUC8sLlgTrhWg'

# Define intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content events

client = discord.Client(intents=intents)

# Arduino setup
ser = serial.Serial('COM7', 9600)  # Update 'COM4' to your Arduino port

# Data collection variables
data_entries = []

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    global data_entries
    
    if message.content.startswith('!log'):
        data = ser.readline().decode('utf-8').strip()
        if data:
            # Split the data assuming the format "Humidity: 45.00 %\tTemperature: 25.00 *C"
            parts = data.split('\t')
            humidity = parts[0].split(':')[1].strip().replace('%', '')
            temperature = parts[1].split(':')[1].strip().replace('*C', '')
            date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Current date and time
            
            # Log data to Discord channel
            log_channel = client.get_channel(1262820421917479016)  # Replace with your channel ID
            await log_channel.send(f'Temperature: {temperature}, Humidity: {humidity}, Date/Time: {date_time}')
            
            # Append data to data_entries
            data_entries.append([temperature, humidity, date_time])
            
            # Check if we have collected 10 entries
            if len(data_entries) >= 10:
                create_excel_file(data_entries)
                data_entries = []  # Reset data_entries after creating Excel file

def create_excel_file(data):
    # Create a DataFrame
    df = pd.DataFrame(data, columns=['Temperature', 'Humidity', 'Date/Time'])
    
    # Save to Excel file
    file_name = f'data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'  # Example: data_20240101_120000.xlsx
    df.to_excel(file_name, index=False)
    print(f'Excel file "{file_name}" created successfully.')

client.run(TOKEN)
