from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views import View
from django.utils.decorators import method_decorator
from django import forms
from .models import Send
import telebot, requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

API = 'https://restcountries.com/v3.1/all?fields=name,flags'
TOKEN = '6596894056:AAFwScLkMoTPzCwB1yNMZENqsR1KGTzgkL4'

bot = telebot.TeleBot(TOKEN)

class WebhookView(View):
    @method_decorator(csrf_exempt)
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        json_str = request.body.decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return JsonResponse({'status': 'ok'})

class SendForm(forms.ModelForm):
    class Meta:
        model = Send
        fields = ['title', 'img']

def send_email_message(email, subject, message):
    from_email = 'mamadaminov001@gmail.com'
    password = 'BlackHatHacker'

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    server.sendmail(from_email, email, msg.as_string())
    server.quit()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Botga xush kelibsiz!\nIltimos malumot olmoqchi bo'lgan mamlakatingizni kiriting:")

@bot.message_handler(func=lambda message: True)
def handle_country_info(message):
    country_name = message.text
    country_info = get_country_info(country_name)

    if country_info:
        bot.send_message(message.chat.id, f"Mamalakat:{country_name}\n{country_info}\n Siz shu malumotni emailga yubormoqchimisi?")

@bot.message_handler(func=lambda message: message.text.endswith('@gmail.com'))
def send_country_info_email(message):
    email_address = message.text
    country_info = get_country_info(message.text[:-10])
    if country_info:
        send_email_message(email_address, "Mamalakat haqidagi malumot", country_info)

def get_country_info(country_name):
    response = requests.get(API)
    if response.status_code == 200:
        countries = response.json()
        for country in countries:
            if country.get('name', '') == country_name:
                country_info = f"Name: {country_name}\nFlag: {country.get('flags', '')}"
                return country_info
    return "Mamalakat haqida malumot topilmadi!"

bot.remove_webhook()
bot.set_webhook(url='https://b94e-94-141-68-35.ngrok-free.app/webhook/')
