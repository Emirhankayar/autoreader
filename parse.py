import re
import os
import csv
from fuzzywuzzy import fuzz
from datetime import datetime
from collections import Counter


def get_item(text):
    print("GETTING ITEM NAME AND PRICE...\n")
    # Stop words
    stop_words = [
        "SUBTOTALE",
        "TOTALECOMPLESSIVO",
        "DICUIIVA",
        "PAGAMENTOELETTRONICO",
        "IMPORTOPAGATO",
    ]

    for stop_word in stop_words:
        if stop_word in text:
            text = text.split(stop_word, 1)[0]
            break

    pattern = r"([A-Z0-9.]+)\s*([\d]+[.,][\d]+[A-Z]?)"
    matches = re.findall(pattern, text)

    valid_prices = {}
    for match in matches:
        item = match[0]
        price = match[1]

        if all(char == "X" or not char.isalpha() for char in item):
            continue

        try:
            price = price.rstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ").replace(",", ".")
            decimal_places = len(price.split(".")[1]) if "." in price else 0
            price = float(price)
        except ValueError:
            price = None
            decimal_places = 0

        if item in valid_prices and decimal_places == 2:
            valid_prices[item] = price
        elif item not in valid_prices:
            valid_prices[item] = price

    items = [
        {"name": item, "price": valid_prices[item]}
        for match in matches
        for item, price in [match]
        if not all(char == "X" or not char.isalpha() for char in item)
    ]

    # for item in items:
    # print(f"Item: {item['name']}, Price: {item['price']}")
    return items


def get_total(text):
    print("GETTING TOTAL PRICE...\n")

    words = [
        "SUBTOTALE",
        "TOTALECOMPLESSIVO",
        "IMPORTOPAGATO",
        "PAGAMENTOELETTRONICO",
        "ELETTRONICO",
    ]

    pattern = r"([A-Z]+)\s*([\d]+[.,][\d]+)"

    matches = re.findall(pattern, text)
    valid_totals = {}
    price_counts = Counter()
    for match in matches:
        word = match[0]
        price = match[1]

        for target in words:
            if fuzz.ratio(word, target) > 80:

                try:
                    price = price.replace(",", ".")
                    decimal_places = len(price.split(".")[1]) if "." in price else 0
                    price = float(price)
                except ValueError:
                    price = None
                    decimal_places = 0

                # If word already exists,
                # Update the price only if the new price has two decimal places
                if word in valid_totals and decimal_places == 2:
                    valid_totals[word] = price
                elif word not in valid_totals:
                    valid_totals[word] = price

                if price is not None:
                    price_counts[price] += 1

    total = max(valid_totals, key=valid_totals.get)

    most_frequent_price = max(price_counts, key=price_counts.get)

    # print(f"TotalFoundIn: {total}, TotalPrice: {valid_totals[total]}")

    return total, most_frequent_price


def get_date(text):
    print("GETTING DATE AND TIME...\n")
    pattern = r"(\d{2}/\d{2}/\d{2}\d{2}:\d{2})"
    match = re.search(pattern, text)

    if match:
        date_str = match.group(1)
        date = datetime.strptime(date_str, "%d/%m/%y%H:%M")

        date_str = date.strftime("%d/%m/%y %H:%M")
        # print(f"Date: {date_str}")
        return date

    print("No date and time found")
    return None


def write_csv(item, price, total, date):

    os.makedirs("output", exist_ok=True)

    if item is not None and price is not None:
        with open("output/products.csv", "a", newline="") as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["item", "price", "date"])
            writer.writerow([item, price, date])

    if total is not None:
        with open("output/total.csv", "a", newline="") as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["total", "date"])
            writer.writerow([total, date])


def parse_image(text):
    items = get_item(text)
    total_word, total_price = get_total(text)
    date = get_date(text)
    for item in items:
        write_csv(item["name"], item["price"], None, date)
    print("WRITING TO CSV...\n")
    write_csv(None, None, total_price, date)
