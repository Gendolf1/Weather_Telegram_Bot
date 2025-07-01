from telegram import Update
from telegram.ext import(
ApplicationBuilder,
CommandHandler,
ContextTypes,
MessageHandler,
filters 
)
import requests
import logging

logging.basicConfig(
    filename='bot.log',  
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

with open('keys.txt') as file:
    lines = file.readlines()
    telegram_token = lines[0].strip() 
    weather_api_key = lines[1].strip() if len(lines) > 1 else None 
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши мне название города и я пришлю сводку погоды")


async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    try:
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}"
            f"&lang=ru&units=metric&appid={weather_api_key}"
        )
        data = response.json()
        
        if data['cod'] != 200:
            await update.message.reply_text("Город не найден. Попробуйте еще раз!")
            return
            
        weather_description = data['weather'][0]['description']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        
        await update.message.reply_text(
            f"Погода в {city}:\n"
            f"• {weather_description.capitalize()}\n"
            f"• Температура: {temp}°C (ощущается как {feels_like}°C)\n"
            f"• Влажность: {humidity}%\n"
            f"• Ветер: {wind_speed} м/с"
        )
    except Exception as e:
        logging.error(f"Ошибка при запросе погоды: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже!")


app = ApplicationBuilder().token(telegram_token).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather))

app.run_polling()