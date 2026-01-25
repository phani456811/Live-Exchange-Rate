from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import os

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static",
)

# Enhanced fallback data with more countries
FALLBACK_CURRENCIES = [
    {"name": "United States", "currency_code": "USD", "rate": 1.0, "flag_url": "https://flagcdn.com/us.svg"},
    {"name": "European Union", "currency_code": "EUR", "rate": 0.92, "flag_url": "https://flagcdn.com/eu.svg"},
    {"name": "United Kingdom", "currency_code": "GBP", "rate": 0.79, "flag_url": "https://flagcdn.com/gb.svg"},
    {"name": "Japan", "currency_code": "JPY", "rate": 148.50, "flag_url": "https://flagcdn.com/jp.svg"},
    {"name": "India", "currency_code": "INR", "rate": 83.25, "flag_url": "https://flagcdn.com/in.svg"},
    {"name": "Canada", "currency_code": "CAD", "rate": 1.35, "flag_url": "https://flagcdn.com/ca.svg"},
    {"name": "Australia", "currency_code": "AUD", "rate": 1.52, "flag_url": "https://flagcdn.com/au.svg"},
    {"name": "Switzerland", "currency_code": "CHF", "rate": 0.88, "flag_url": "https://flagcdn.com/ch.svg"},
    {"name": "China", "currency_code": "CNY", "rate": 7.18, "flag_url": "https://flagcdn.com/cn.svg"},
    {"name": "Mexico", "currency_code": "MXN", "rate": 17.25, "flag_url": "https://flagcdn.com/mx.svg"},
    {"name": "United Arab Emirates", "currency_code": "AED", "rate": 3.67, "flag_url": "https://flagcdn.com/ae.svg"},
    {"name": "Saudi Arabia", "currency_code": "SAR", "rate": 3.75, "flag_url": "https://flagcdn.com/sa.svg"},
    {"name": "Singapore", "currency_code": "SGD", "rate": 1.34, "flag_url": "https://flagcdn.com/sg.svg"},
    {"name": "Hong Kong", "currency_code": "HKD", "rate": 7.82, "flag_url": "https://flagcdn.com/hk.svg"},
    {"name": "South Korea", "currency_code": "KRW", "rate": 1320.0, "flag_url": "https://flagcdn.com/kr.svg"},
    {"name": "Brazil", "currency_code": "BRL", "rate": 4.95, "flag_url": "https://flagcdn.com/br.svg"},
    {"name": "Russia", "currency_code": "RUB", "rate": 92.5, "flag_url": "https://flagcdn.com/ru.svg"},
    {"name": "South Africa", "currency_code": "ZAR", "rate": 18.75, "flag_url": "https://flagcdn.com/za.svg"},
    {"name": "New Zealand", "currency_code": "NZD", "rate": 1.63, "flag_url": "https://flagcdn.com/nz.svg"},
    {"name": "Turkey", "currency_code": "TRY", "rate": 30.15, "flag_url": "https://flagcdn.com/tr.svg"},
]

POPULAR_CURRENCIES = [
    ("USD", "US Dollar"),
    ("EUR", "Euro"),
    ("GBP", "British Pound"),
    ("JPY", "Japanese Yen"),
    ("INR", "Indian Rupee"),
    ("CAD", "Canadian Dollar"),
    ("AUD", "Australian Dollar"),
    ("CHF", "Swiss Franc"),
    ("CNY", "Chinese Yuan"),
    ("AED", "UAE Dirham"),
    ("SGD", "Singapore Dollar"),
    ("NZD", "New Zealand Dollar"),
    ("SEK", "Swedish Krona"),
    ("NOK", "Norwegian Krone"),
    ("DKK", "Danish Krone"),
    ("ZAR", "South African Rand"),
    ("BRL", "Brazilian Real"),
    ("RUB", "Russian Ruble"),
    ("KRW", "South Korean Won"),
    ("MXN", "Mexican Peso"),
    ("TRY", "Turkish Lira"),
    ("THB", "Thai Baht"),
    ("IDR", "Indonesian Rupiah"),
    ("MYR", "Malaysian Ringgit"),
    ("PHP", "Philippine Peso"),
    ("SAR", "Saudi Riyal"),
    ("HKD", "Hong Kong Dollar"),
]

MONEY_TRANSFER_APPS = [
    {"id": "wise", "name": "Wise", "rating": 4.8, "fee": "0.3-1%", "speed": "1-2 days"},
    {"id": "paypal", "name": "PayPal", "rating": 4.3, "fee": "2.5-4%", "speed": "Instant"},
    {"id": "remitly", "name": "Remitly", "rating": 4.5, "fee": "0.5-2%", "speed": "1 day"},
    {"id": "westernunion", "name": "Western Union", "rating": 4.0, "fee": "3-5%", "speed": "Instant"},
]

def get_live_exchange_rates(base_currency="USD"):
    """Get live exchange rates from a free API."""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("rates", {})
        return None
    except Exception as e:
        print(f"Error fetching live rates: {e}")
        return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_currencies")
def get_currencies():
    try:
        live_rates = get_live_exchange_rates("USD")
        if live_rates:
            countries_response = requests.get(
                "https://restcountries.com/v3.1/all?fields=name,currencies,flags",
                timeout=10,
            )
            if countries_response.status_code == 200:
                countries_data = countries_response.json()
                currency_list = []

                for country in countries_data:
                    currencies = country.get("currencies", {})
                    if not currencies:
                        continue

                    currency_code = list(currencies.keys())[0].upper()
                    rate = live_rates.get(currency_code)

                    if rate and currency_code != "USD":
                        currency_list.append(
                            {
                                "name": country.get("name", {}).get("common", "Unknown"),
                                "currency_code": currency_code,
                                "rate": rate,
                                "flag_url": country.get("flags", {}).get("svg", ""),
                            }
                        )

                currency_list.sort(key=lambda x: x["name"])
                return jsonify(
                    {
                        "success": True,
                        "countries": currency_list,
                        "source": "live_api",
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )

        return jsonify(
            {
                "success": True,
                "countries": FALLBACK_CURRENCIES,
                "source": "fallback",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    except Exception as e:
        print(f"Live API error: {e}. Using fallback data.")
        return jsonify(
            {
                "success": True,
                "countries": FALLBACK_CURRENCIES,
                "source": "fallback",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

@app.route("/compare_currencies")
def compare_currencies():
    try:
        from_currency = request.args.get("from", "usd").upper()
        to_currency = request.args.get("to", "eur").upper()
        amount = float(request.args.get("amount", 100))

        live_rates = get_live_exchange_rates(from_currency)

        if live_rates and to_currency in live_rates:
            rate = live_rates[to_currency]
            rate_source = "live"
        else:
            reverse_rates = get_live_exchange_rates(to_currency)
            if reverse_rates and from_currency in reverse_rates:
                rate = 1 / reverse_rates[from_currency]
                rate_source = "live_reverse"
            else:
                demo_rates = {
                    "USD": {"EUR": 0.92, "GBP": 0.79, "JPY": 148.50, "INR": 83.25},
                    "EUR": {"USD": 1.09, "GBP": 0.86},
                    "GBP": {"USD": 1.27, "EUR": 1.16},
                    "JPY": {"USD": 0.0067, "EUR": 0.0062},
                    "INR": {"USD": 0.012, "EUR": 0.011},
                }
                rate = demo_rates.get(from_currency, {}).get(to_currency, 1.0)
                rate_source = "demo"

        converted_amount = amount * rate

        fee_multipliers = {
            "wise": 0.995,
            "remitly": 0.985,
            "paypal": 0.97,
            "westernunion": 0.95,
        }

        transfer_apps = []
        for a in MONEY_TRANSFER_APPS:
            app_copy = a.copy()
            app_copy["estimated_amount"] = converted_amount * fee_multipliers.get(a["id"], 0.95)
            transfer_apps.append(app_copy)

        transfer_apps.sort(key=lambda x: x["estimated_amount"], reverse=True)

        return jsonify(
            {
                "success": True,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "amount": amount,
                "exchange_rate": rate,
                "converted_amount": converted_amount,
                "transfer_apps": transfer_apps,
                "rate_source": rate_source,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/get_popular_currencies")
def get_popular_currencies():
    return jsonify({"success": True, "currencies": POPULAR_CURRENCIES})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # IMPORTANT for Docker/EC2: host must be 0.0.0.0
    app.run(host="0.0.0.0", port=port)

API_KEY = os.getenv("EXCHANGE_API_KEY")

if not API_KEY:
    raise ValueError("API key not found")