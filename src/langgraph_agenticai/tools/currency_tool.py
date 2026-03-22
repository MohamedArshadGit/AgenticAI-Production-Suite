import requests
from langchain.tools import tool

@tool
def currency_converter(amount:float,from_currency:str,to_currency:str)-> str:
    """
    Convert an amount from one currency to another using live exchange rates.
    Use this when the user asks about currency conversion or exchange rates.
    Examples: 'Convert 100 USD to GBP', 'How much is 50 euros in dollars?',
    'What is 1000 INR in pounds?'

    Args:
        amount       : Amount to convert e.g. 100.0
        from_currency: Source currency code e.g. 'USD', 'EUR', 'GBP', 'INR'
        to_currency  : Target currency code e.g. 'GBP', 'USD', 'EUR', 'INR'
    """
    try:
        # free API — no key needed
        # base currency is from_currency, we get all rates back
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"

        response =requests.get(url,timeout=5)
        data =response.json()
        rates =data.get('rates',{})
        to_currency_upper =to_currency.upper()
        if to_currency_upper not in rates:
            return f"Error: Currency '{to_currency}' not found. Use standard codes like USD, GBP, EUR, INR."
        
        # get the exchange rate for target currency
        rate =rates[to_currency_upper]

        #calculate converted amount 
        converted =amount*rate 

        return (
            f"{amount}{from_currency.upper()}"
            f"Converted:{converted} {to_currency_upper}"
            f"1{from_currency.upper()} equals to {rate}{to_currency_upper}"
        )


    except requests.exceptions.Timeout:
        return "Error: Currency request timed out. Check your internet connection."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to currency service."
    except Exception as e:
        return f"Error: {str(e)}"


