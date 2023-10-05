from datetime import datetime, timedelta
import gspread
from google.oauth2 import service_account
import requests
import pandas as pd
from decimal import Decimal, getcontext, ROUND_HALF_UP
import json  # Import the json module
import os  # Import the os module for environment variable access

# Constants
BASE_CURRENCY = 'HKD'
SPECIFIED_CURRENCIES = ['CHF', 'DKK', 'EUR', 'NOK', 'SEK', 'USD', 'CNY']
SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# Retrieve the API_KEY from the environment variable
API_KEY = os.environ.get('API_KEY')

if API_KEY is None:
    print("Error: API_KEY environment variable not set.")
    exit(1)


# Set the precision (number of decimal places) and rounding mode
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP

def fetch_exchange_rates(date_str):
    url = f"https://openexchangerates.org/api/historical/{date_str}.json?app_id={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {currency: Decimal(rate) for currency, rate in data.get('rates', {}).items()}
    else:
        raise Exception(f"Failed to fetch exchange rates for date {date_str}. Error: {response.text}")

def adjust_exchange_rates(exchange_rates, base_currency_rate, currencies):
    adjusted_rates = {}
    for currency_code in currencies:
        exchange_rate = exchange_rates.get(currency_code, None)
        if exchange_rate is not None:
            adjusted_rate = exchange_rate / base_currency_rate
            adjusted_rates[currency_code] = adjusted_rate
    return adjusted_rates

# ...

def main():
    # Retrieve the JSON content from the environment variable
    service_account_key_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')

    if service_account_key_json is None:
        print("Error: GOOGLE_SERVICE_ACCOUNT_KEY environment variable not set.")
        return

    # Parse the JSON content
    service_account_key = json.loads(service_account_key_json)

    # Authenticate with Google Sheets API using the parsed service account key
    credentials = service_account.Credentials.from_service_account_info(service_account_key, scopes=SCOPES)
    client = gspread.Client(auth=credentials)

    # Open the Google Sheet
    spreadsheet = client.open("spread_sheet")
    worksheet = spreadsheet.get_worksheet(0)  # Assuming the first sheet

    # Fetch the last date from the Google Sheet
    values = worksheet.get_all_values()
    if not values or values[0][0] != 'DATE':
        header_row = ['DATE', *SPECIFIED_CURRENCIES]
        worksheet.insert_row(header_row, 1)  # Add the header as the first row

    last_date_str = values[-1][0] if values and values[-1][0] != 'DATE' else datetime.now().strftime('%d/%m/%Y')

    # Calculate date range between the last date and today
    last_date = datetime.strptime(last_date_str, '%d/%m/%Y').date()
    today_date = datetime.now().date()

    # Only append today's date if it's greater than the last date
    date_range = pd.date_range(last_date + timedelta(days=1), today_date) if today_date > last_date else []

    print(date_range)

    # Clean data older than 120 days
    clean_date = datetime.now() - timedelta(days=400)
    clean_date_str = clean_date.strftime('%d/%m/%Y')
    if last_date_str < clean_date_str:
        print(f"Cleaning data older than {clean_date_str}")
        rows_to_delete = []
        for row_index, row in enumerate(values):
            if row[0] != 'DATE':
                row_date = datetime.strptime(row[0], '%d/%m/%Y').date()
                if row_date < clean_date.date():
                    rows_to_delete.append(row_index + 1)

    # Update exchange rates for each date in the date range
    for date in date_range:
        date_str = date.strftime('%Y-%m-%d')
        print(date_str)

        try:
            # Fetch the base currency rate for the current date
            base_currency_rates = fetch_exchange_rates(date_str)
            base_currency_rate = base_currency_rates.get(BASE_CURRENCY)
            print(base_currency_rate)

            if base_currency_rate is not None:
                # Adjust exchange rates for specified currencies and convert to float with the same precision
                adjusted_rates = {currency: float(rate.quantize(Decimal('0.00000000'))) for currency, rate in adjust_exchange_rates(base_currency_rates, base_currency_rate, SPECIFIED_CURRENCIES).items()}

                # Format the date
                formatted_date = date.strftime('%d/%m/%Y')

                # Prepare the data for Google Sheet update
                row_data = {'DATE': formatted_date, **adjusted_rates}

                # Update the Google Sheet
                worksheet.append_row(list(row_data.values()))
            else:
                print(f"Base currency rate for {BASE_CURRENCY} not found for date {date_str}.")
        except Exception as e:
            print(f"An error occurred for date {date_str}: {str(e)}")

    print("Exchange rates updated in Google Sheet.")

if __name__ == "__main__":
    main()
