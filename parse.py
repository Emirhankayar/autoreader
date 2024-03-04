import re
import os
import csv
from fuzzywuzzy import fuzz
from datetime import datetime
from collections import Counter


def get_item(text):
    # print("GETTING ITEM NAME AND PRICE...\n")
    # Stop words
    stop_words = [
        "SUBTOTALE",
        "TOTALE COMPLESSIVO",
        "DI CUI IVA",
        "PAGAMENTO ELETTRONICO",
        "IMPORTO PAGATO",
    ]

    for stop_word in stop_words:
        if stop_word in text:
            text = text.split(stop_word, 1)[0]
            break

    lines = text.split("\n")
    items = []
    for line in lines:
        # Ignore lines that contain the word "SCADENZA"
        if "SCADENZA" in line or "Sconto" in line:
            continue
        # Split the line at the first uppercase character
        line = re.split(r"(?=[A-Z])", line, 1)[-1]
        words = line.split()
        item = []
        price = None
        for word in words:
            if re.match(r"[\d]+[.,][\d]+[A-Z€]?", word):
                # Ignore lines where the price has a "-" sign in front of it
                if word.startswith("-"):
                    price = None
                    break
                price = word.rstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ€").replace(",", ".")
                break
            else:
                item.append(word)

        item = " ".join(item)
        # Ignore lines where the item name contains only the letter "X" (possibly with numbers and special characters)
        if re.match(r"^[^a-zA-Z]*X[^a-zA-Z]*$", item):
            continue
        # Ignore lines that do not match the pattern
        if item and price:
            items.append({"name": item, "price": price})

    return items


def get_total(text):
    # print("GETTING TOTAL PRICE...\n")

    words = [
        "SUBTOTALE",
        "TOTALE COMPLESSIVO",
        "IMPORTO PAGATO",
        "PAGAMENTO ELETTRONICO",
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

    if valid_totals:
        total = max(valid_totals, key=valid_totals.get)
    else:
        print("No total price found")
        return None, None

    most_frequent_price = max(price_counts, key=price_counts.get)

    # print(f"TotalFoundIn: {total}, TotalPrice: {valid_totals[total]}")

    return total, most_frequent_price


def get_date(text):
    # print("GETTING DATE AND TIME...\n")
    pattern = r"(\d{2}/\d{2}/\d{2}\s+\d{2}:\d{2})"
    match = re.search(pattern, text)

    if match:
        date_str = match.group(1)
        try:
            date = datetime.strptime(date_str, "%d/%m/%y %H:%M")
            date_str = date.strftime("%d/%m/%y %H:%M")
            return date
        except ValueError:
            print("Date string does not match the expected format")

    print("No date and time found")
    return None


def get_method(text):
    # print("GETTING PAYMENT METHOD...\n")
    method_credit = False
    method_cash = False

    # Check for "PAGAMENTO ELETTRONICO"
    if "PAGAMENTO ELETTRONICO" in text:
        method_credit = True
    else:
        # Check for "PAGAMENTO CONTANTE"
        if "PAGAMENTO CONTANTE" in text:
            method_cash = True

    return method_credit, method_cash


def write_item_csv(item, price, date):
    os.makedirs("output", exist_ok=True)

    item = "NULL" if item is None else item
    price = "NULL" if price is None else price
    date = "NULL" if date is None else date

    with open("output/products.csv", "a", newline="") as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(["item", "price", "date"])
        writer.writerow([item, price, date])


def write_total_csv(total, date, method_credit, method_cash):
    os.makedirs("output", exist_ok=True)

    total = "NULL" if total is None else total
    date = "NULL" if date is None else date
    method_credit = "False" if not method_credit else "True"
    method_cash = "False" if not method_cash else "True"

    with open("output/total.csv", "a", newline="") as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(["total", "date", "method_credit", "method_cash"])
        writer.writerow([total, date, method_credit, method_cash])


def parse_image(text):
    items = get_item(text)
    total_word, total_price = get_total(text)
    date = get_date(text)
    method_credit, method_cash = get_method(text)
    for item in items:
        write_item_csv(item["name"], item["price"], date)
    # print("WRITING TO CSV...\n")
    if total_price is not None:
        write_total_csv(total_price, date, method_credit, method_cash)
