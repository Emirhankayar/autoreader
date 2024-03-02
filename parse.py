import re
import os
import csv
from fuzzywuzzy import fuzz
from datetime import datetime


def get_item(text):
    print("GETTING ITEM NAME AND PRICE...\n")
    # Stop processing at "SUBTOTALE"
    text = text.split("SUBTOTALE", 1)[0]

    # Regular expression pattern for item and price
    pattern = r"([A-Z0-9.]+)\s*([\d]+[.,][\d]+[A-Z]?)"
    matches = re.findall(pattern, text)

    valid_prices = {}
    for match in matches:
        item = match[0]
        price = match[1]

        # Check if price is valid
        try:
            # Replace comma with dot for decimal numbers
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
    ]

    # for item in items:
    # print(f"Item: {item['name']}, Price: {item['price']}")

    return items


def get_total(text):
    print("GETTING TOTAL PRICE...\n")
    # Words to match
    words = ["SUBTOTALE", "TOTALECOMPLESSIVO", "IMPORTOPAGATO"]

    pattern = r"([A-Z]+)\s*([\d]+[.,][\d]+)"

    matches = re.findall(pattern, text)
    valid_totals = {}
    for match in matches:
        word = match[0]
        price = match[1]

        # Check if word matches one of the target words
        for target in words:
            if fuzz.ratio(word, target) > 80:
                # Check if price is valid
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

    # Get the total with the most valid price
    total = max(valid_totals, key=valid_totals.get)

    # print(f"TotalFoundIn: {total}, TotalPrice: {valid_totals[total]}")

    return total, valid_totals[total]


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

    # Ensure the output directory exists
    os.makedirs("output", exist_ok=True)

    # products.csv
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


def parse_text(text):
    items = get_item(text)
    total_word, total_price = get_total(text)
    date = get_date(text)
    for item in items:
        write_csv(item["name"], item["price"], None, date)
    print("WRITING TO CSV...\n")
    write_csv(None, None, total_price, date)
