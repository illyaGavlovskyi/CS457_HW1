import csv
import requests
from bs4 import BeautifulSoup

FINALS_URL = "https://www.unr.edu/admissions/records/academic-calendar/finals-schedule"
INPUT_FILE = "class_schedule.csv"
OUTPUT_FILE = "finals_schedule.csv"

DAY_GROUPS = ["M", "T", "W", "R", "F", "MW", "TR", "MWF", "MTWR", "MTWRF"]

# Fetch and parse the webpage
r = requests.get(FINALS_URL)
soup = BeautifulSoup(r.text, 'html.parser')

# Find all tables containing finals schedule
finals_data = {}
for table in soup.find_all('table', class_='footable'):
    day = table.find_previous('h2').text.strip()
    for row in table.find('tbody').find_all('tr'):
        cols = row.find_all('td')
        class_time = cols[0].text.strip()
        class_days = cols[1].text.strip()
        final_time = cols[2].text.strip()
        finals_data[(class_time, class_days)] = (day, final_time)

# Function to combine days for a class, mapping Th to R and ensuring TR order
def combine_days(class_name, data):
    days_dict = {}
    for row in data:
        if row['Class'] == class_name:
            day = row['Days']
            days_dict[day] = row['Time']
    if not days_dict:
        return None, None
    # Sort days to ensure T comes before R for TR pattern
    days = ''.join(days_dict.keys())
    time = next(iter(days_dict.values()))  # Use the first time for consistency
    return time, days

# Read user classes from CSV, group by class, and combine days
class_finals = []
with open(INPUT_FILE, 'r') as file:
    reader = csv.DictReader(file)
    all_rows = list(reader)  # Read all rows into a list
    unique_classes = set(row['Class'] for row in all_rows)
    # print(unique_classes)
    for class_name in unique_classes:
        class_rows = [row for row in all_rows if row['Class'] == class_name]
        class_time, combined_days = combine_days(class_name, class_rows)
        if class_time and combined_days:
            # Normalize time format
            class_time = class_time.lower().replace('pm', ' p.m.').replace('am', ' a.m.')
            key = (class_time, combined_days)
            print(f"{key} ---- {finals_data}")
            if key in finals_data:
                day, final_time = finals_data[key]
                class_finals.append((class_name, class_time, combined_days, day, final_time))
                print(f"Class {class_name} at {class_time} on {combined_days} has final on {day} at {final_time}")
            else:
                print(f"No final time found for {class_name} at {class_time} on {combined_days}")
        else:
            print(f"No valid schedule found for {class_name}")

# Save to output CSV only for the user's classes
with open(OUTPUT_FILE, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Class", "Class Time", "Class Days", "Final Day", "Final Time"])
    for class_name, class_time, class_days, day, final_time in class_finals:
        writer.writerow([class_name, class_time, class_days, day, final_time])