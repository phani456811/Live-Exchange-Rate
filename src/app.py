from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import os

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

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
    {"name": "Turkey", "currency_code": "TRY", "rate": 30.15, "flag_url": "https://flagcdn.com/tr.svg"}
]

# Popular currencies for easy access
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
    ("HKD", "Hong Kong Dollar")
]

MONEY_TRANSFER_APPS = [
    {"id": "wise", "name": "Wise", "rating": 4.8, "fee": "0.3-1%", "speed": "1-2 days"},
    {"id": "paypal", "name": "PayPal", "rating": 4.3, "fee": "2.5-4%", "speed": "Instant"},
    {"id": "remitly", "name": "Remitly", "rating": 4.5, "fee": "0.5-2%", "speed": "1 day"},
    {"id": "westernunion", "name": "Western Union", "rating": 4.0, "fee": "3-5%", "speed": "Instant"}
]

def get_live_exchange_rates(base_currency='USD'):
    """Get REAL live exchange rates from a free API"""
    try:
        # Using ExchangeRate-API which is free and reliable
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('rates', {})
        else:
            print(f"API returned status: {response.status_code}")
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
        print("🔄 Attempting to fetch REAL live currency data...")
        
        # Get REAL live exchange rates
        live_rates = get_live_exchange_rates('USD')
        
        if live_rates:
            # Try to get countries data
            countries_response = requests.get(
                "https://restcountries.com/v3.1/all?fields=name,currencies,flags", 
                timeout=10
            )
            
            if countries_response.status_code == 200:
                countries_data = countries_response.json()
                currency_list = []
                
                for country in countries_data:  # Remove limit to get all countries
                    currencies = country.get('currencies', {})
                    if not currencies:
                        continue
                        
                    # Get the first currency for this country
                    currency_code = list(currencies.keys())[0].upper()
                    rate = live_rates.get(currency_code)
                    
                    if rate and currency_code != 'USD':  # Skip USD itself
                        currency_list.append({
                            "name": country.get('name', {}).get('common', 'Unknown'),
                            "currency_code": currency_code,
                            "rate": rate,
                            "flag_url": country.get('flags', {}).get('svg', '')
                        })
                
                # Sort by country name
                currency_list.sort(key=lambda x: x['name'])
                
                print(f"✅ Successfully loaded {len(currency_list)} currencies with LIVE rates")
                return jsonify({
                    "success": True,
                    "countries": currency_list,
                    "source": "live_api",
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        # If we reach here, use enhanced fallback data
        print("⚠️ Using enhanced fallback data with more countries")
        return jsonify({
            "success": True,
            "countries": FALLBACK_CURRENCIES,
            "source": "fallback",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
            
    except Exception as e:
        print(f"❌ Live API Error: {e}. Using fallback data.")
        # Use fallback data if API fails
        return jsonify({
            "success": True,
            "countries": FALLBACK_CURRENCIES,
            "source": "fallback",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

@app.route("/compare_currencies")
def compare_currencies():
    try:
        from_currency = request.args.get('from', 'usd').upper()
        to_currency = request.args.get('to', 'eur').upper()
        amount = float(request.args.get('amount', 100))
        
        print(f"🔄 Comparing {amount} {from_currency} to {to_currency}")
        
        # Get REAL live exchange rate for this specific pair
        live_rates = get_live_exchange_rates(from_currency)
        
        if live_rates and to_currency in live_rates:
            rate = live_rates[to_currency]
            print(f"✅ Live rate found: 1 {from_currency} = {rate} {to_currency}")
        else:
            # Fallback: try the reverse rate
            reverse_rates = get_live_exchange_rates(to_currency)
            if reverse_rates and from_currency in reverse_rates:
                rate = 1 / reverse_rates[from_currency]
                print(f"✅ Using reverse rate: 1 {from_currency} = {rate} {to_currency}")
            else:
                # Enhanced demo rates with more currencies
                demo_rates = {
                    'USD': {'EUR': 0.92, 'GBP': 0.79, 'JPY': 148.50, 'INR': 83.25, 'CAD': 1.35, 'AUD': 1.52, 
                           'CHF': 0.88, 'CNY': 7.18, 'AED': 3.67, 'SGD': 1.34, 'HKD': 7.82, 'KRW': 1320.0,
                           'BRL': 4.95, 'RUB': 92.5, 'ZAR': 18.75, 'NZD': 1.63, 'TRY': 30.15, 'SAR': 3.75},
                    'EUR': {'USD': 1.09, 'GBP': 0.86, 'JPY': 161.50, 'INR': 90.50, 'CHF': 0.96, 'CAD': 1.47},
                    'GBP': {'USD': 1.27, 'EUR': 1.16, 'JPY': 188.00, 'INR': 105.25, 'AUD': 1.92, 'CAD': 1.71},
                    'JPY': {'USD': 0.0067, 'EUR': 0.0062, 'GBP': 0.0053, 'INR': 0.56, 'CNY': 0.048},
                    'INR': {'USD': 0.012, 'EUR': 0.011, 'GBP': 0.0095, 'JPY': 1.79, 'AED': 0.044}
                }
                if from_currency in demo_rates and to_currency in demo_rates[from_currency]:
                    rate = demo_rates[from_currency][to_currency]
                    print(f"⚠️ Using demo rate: 1 {from_currency} = {rate} {to_currency}")
                else:
                    rate = 1.0  # Default fallback
                    print(f"❌ No rate found, using default: 1.0")
        
        converted_amount = amount * rate
        
        # Calculate transfer app estimates (with small differences)
        transfer_apps = []
        for app in MONEY_TRANSFER_APPS:
            app_copy = app.copy()
            # Simulate different fees for each app (based on real-world averages)
            fee_multipliers = {
                "wise": 0.995,     # 0.5% fee - best rates
                "remitly": 0.985,  # 1.5% fee
                "paypal": 0.97,    # 3% fee
                "westernunion": 0.95  # 5% fee
            }
            app_copy["estimated_amount"] = converted_amount * fee_multipliers.get(app["id"], 0.95)
            transfer_apps.append(app_copy)
        
        # Sort by best value (highest estimated amount)
        transfer_apps.sort(key=lambda x: x["estimated_amount"], reverse=True)
        
        return jsonify({
            "success": True,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "amount": amount,
            "exchange_rate": rate,
            "converted_amount": converted_amount,
            "transfer_apps": transfer_apps,
            "rate_source": "live" if live_rates and to_currency in live_rates else "demo"
        })
        
    except Exception as e:
        print(f"❌ Comparison error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route("/get_popular_currencies")
def get_popular_currencies():
    """Return list of popular currencies for dropdown"""
    return jsonify({
        "success": True,
        "currencies": POPULAR_CURRENCIES
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)