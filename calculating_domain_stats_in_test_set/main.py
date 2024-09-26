import os
import json
import csv
from collections import Counter, defaultdict

# Initialize data structures
dialogue_services = {}  # Map dialogue_id to set of services
service_dialogues = defaultdict(set)  # Map service to set of dialogue_ids

# Directory containing the JSON files
directory = './test_files/'

# Loop over all files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                # Ensure the data is a list
                if isinstance(data, list):
                    for obj in data:
                        # Get dialogue_id and services
                        dialogue_id = obj.get('dialogue_id')
                        services = obj.get('services', [])
                        if dialogue_id:
                            # Map dialogue_id to its services
                            dialogue_services[dialogue_id] = set(services)
                            # Map services to dialogue_ids
                            for service in services:
                                service_dialogues[service].add(dialogue_id)
                else:
                    print(f"Warning: The file {filename} does not contain a list at the top level.")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from file {filename}: {e}")

# Compute total number of dialogues containing each service
total_service_counts = {service: len(dialogue_ids) for service, dialogue_ids in service_dialogues.items()}

# Read the CSV file and collect IDs
csv_ids = []
with open('totranslate.csv', 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        id_value = row.get('\ufeffID [IGNORE]', '').strip()
        if id_value:
            csv_ids.append(id_value)

# Initialize Counter for services in CSV IDs
service_counts_in_csv = Counter()
missing_ids = set()

# For each ID in csv_ids, get the services and count them
for dialogue_id in csv_ids:
    services = dialogue_services.get(dialogue_id)
    if services:
        service_counts_in_csv.update(services)
    else:
        missing_ids.add(dialogue_id)

# Output the results
print("1. Number of dialogues containing each service (Total):")
for service, count in total_service_counts.items():
    print(f"{service}: {count}")
print("Total number of dialogues:", sum(total_service_counts.values()))

print("\n2. Number of rows in 'totranslate.csv' that refer to an ID containing each service:")
for service, count in service_counts_in_csv.items():
    print(f"{service}: {count}")
print("Total number of rows in 'totranslate.csv':", len(csv_ids))


# Optionally, report any IDs in CSV not found in JSON data
if missing_ids:
    print("\nWarning: The following IDs from 'totranslate.csv' were not found in the JSON data:")
    for missing_id in missing_ids:
        print(missing_id)
