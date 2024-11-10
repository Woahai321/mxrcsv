from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def clean_and_convert_to_csv(data):
    # Remove unnecessary lines: empty ones or full of commas
    data_cleaned = re.sub(r'^,+\n?', '', data, flags=re.MULTILINE)
    data_cleaned = re.sub(r'^\n', '', data_cleaned, flags=re.MULTILINE)

    # Remove rows starting with "Total" because we don't need them
    data_cleaned = re.sub(r'^Total.*\n?', '', data_cleaned, flags=re.MULTILINE)

    # Initialize final CSV data list
    csv_data = ["Task Name,Started By,Ended By,Start Date,End Date,Start Time,End Time,Duration"]

    # Parse task names, headers, and data rows
    lines = data_cleaned.splitlines()
    current_task = None

    for line in lines:
        # If the line has no commas, assume it's a task title
        if ',' not in line:
            current_task = line.strip()
        # If the line looks like a data row, prepend the task name and add to result
        elif re.match(r'.*,.*,.*,.*,.*,.*,.*', line):  # Data row
            csv_data.append(f"{current_task},{line.strip()}")

    # Return cleaned CSV data as a single string
    return "\n".join(csv_data)

@app.route('/process', methods=['POST'])
def process_data():
    # Get the raw data (assuming it's sent in plain text format)
    raw_data = request.get_data(as_text=True)

    # Process and clean the data
    cleaned_csv = clean_and_convert_to_csv(raw_data)

    # Return the cleaned CSV as plain text response
    return cleaned_csv, 200, {'Content-Type': 'text/csv'}
