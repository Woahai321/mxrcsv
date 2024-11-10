import csv
from http.server import BaseHTTPRequestHandler
from io import StringIO
import cgi
import re

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            # Parse the multipart form data (if applicable) or raw text body
            content_type, _ = cgi.parse_header(self.headers['Content-Type'])

            if content_type == 'text/plain':
                # Read and parse the raw string data from the request body
                content_length = int(self.headers['Content-Length'])
                raw_data = self.rfile.read(content_length).decode('utf-8')

                # Process the raw text data
                cleaned_data = self.parse_and_clean_data(raw_data)

                # Return the cleaned CSV as response
                self.send_response(200)
                self.send_header('Content-type', 'text/csv')
                self.end_headers()
                self.wfile.write(cleaned_data.encode('utf-8'))

            else:
                self.send_error(400, 'Unsupported Content-Type. Expected text/plain.')

        except Exception as e:
            self.send_error(400, str(e))

    def parse_and_clean_data(self, raw_data):
        """
        Convert raw string data to a cleaned CSV format.
        """
        # Step 1: Clean the data (remove unwanted commas/lines)
        # Remove unnecessary lines: empty ones or full of commas
        cleaned_data = re.sub(r'^,+\n?', '', raw_data, flags=re.MULTILINE)
        cleaned_data = re.sub(r'^\n', '', cleaned_data, flags=re.MULTILINE)

        # Remove rows starting with "Total" because we don't need them
        cleaned_data = re.sub(r'^Total.*\n?', '', cleaned_data, flags=re.MULTILINE)

        # Initialize the final CSV data -- first the headers
        csv_output = StringIO()
        csv_writer = csv.writer(csv_output)
        csv_writer.writerow(["Task Name", "Started By", "Ended By", "Start Date", "End Date", "Start Time", "End Time", "Duration"])

        lines = cleaned_data.splitlines()
        current_task = None

        # Step 2: Parse lines and fill the CSV rows
        for line in lines:
            # If the line doesn't contain commas, treat it as a task name
            if ',' not in line:
                current_task = line.strip()
            # If the line looks like a data row based on having comma-separated values
            elif re.match(r'.*,.*,.*,.*,.*,.*,.*', line):  # Match rows with CSV structure
                csv_writer.writerow([current_task] + line.split(','))

        # Return the final CSV as a string
        return csv_output.getvalue()

