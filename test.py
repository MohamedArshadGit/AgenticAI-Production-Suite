# tests/test_tools_quick.py
# Quick test to verify all 5 tools work correctly before wiring into agent

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.langgraph_agenticai.tools.location_tool import get_location
from src.langgraph_agenticai.tools.datetime_tool import get_datetime
from src.langgraph_agenticai.tools.calculator_tool import calculator
from src.langgraph_agenticai.tools.search_tool import search_web
from src.langgraph_agenticai.tools.weather_tool import get_weather
print("=" * 60)
print("TOOL TESTS")
print("=" * 60)

# ─────────────────────────────────────────
# TEST 1 — Location Tool
# ─────────────────────────────────────────
print("\n📍 TEST 1: Location Tool")
print("-" * 40)
result = get_location.invoke({})  # @tool functions use .invoke()
print(result)

# ─────────────────────────────────────────
# TEST 2 — Datetime Tool
# ─────────────────────────────────────────
print("\n🕐 TEST 2: Datetime Tool (UTC)")
print("-" * 40)
result = get_datetime.invoke({"timezone": "UTC"})
print(result)

print("\n🕐 TEST 2b: Datetime Tool (London)")
print("-" * 40)
result = get_datetime.invoke({"timezone": "Europe/London"})
print(result)

print("\n🕐 TEST 2c: Datetime Tool (invalid timezone)")
print("-" * 40)
result = get_datetime.invoke({"timezone": "Invalid/Zone"})
print(result)

# ─────────────────────────────────────────
# TEST 3 — Calculator Tool
# ─────────────────────────────────────────
print("\n🧮 TEST 3: Calculator Tool")
print("-" * 40)
result = calculator.invoke({"expression": "10 + 10"})
print(result)

result = calculator.invoke({"expression": "sqrt(16)"})
print(result)

result = calculator.invoke({"expression": "2**8"})
print(result)

result = calculator.invoke({"expression": "invalid!@#"})
print(result)

# ─────────────────────────────────────────
# TEST 4 — Search Tool
# ─────────────────────────────────────────
print("\n🔍 TEST 4: Search Tool")
print("-" * 40)
result = search_web.invoke({"query": "Latest AI news 2026", "max_results": 2})
print(result)

print("\n" + "=" * 60)
print("ALL TESTS DONE")
print("=" * 60)

from src.langgraph_agenticai.tools.currency_tool import currency_converter

print("\n💱 TEST 7: Currency Tool")
print("-" * 40)
result = currency_converter.invoke({"amount": 100, "from_currency": "USD", "to_currency": "GBP"})
print(result)

result = currency_converter.invoke({"amount": 50, "from_currency": "EUR", "to_currency": "INR"})
print(result)

result = currency_converter.invoke({"amount": 1000, "from_currency": "GBP", "to_currency": "INR"})
print(result)

result = currency_converter.invoke({"amount": 100, "from_currency": "INVALID", "to_currency": "GBP"})
print(result)