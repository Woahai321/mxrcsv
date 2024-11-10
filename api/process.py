import csv
from io import StringIO
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
        # Step 1: Clean unnecessary commas and empty lines
        # Remove lines that are only commas or empty
        cleaned_data = re.sub(r'^,+\n?', '', raw_data, flags=re.MULTILINE)
        cleaned_data = re.sub(r'^\n', '', cleaned_data, flags=re.MULTILINE)

        # Remove rows like "Total" because of duplication
        cleaned_data = re.sub(r'^Total.*\n?', '', cleaned_data, flags=re.MULTILINE)

        # Step 2: Initialize CSV output
        csv_output = StringIO()
        csv_writer = csv.writer(csv_output)
        csv_writer.writerow(["Task Name", "Started By", "Ended By", "Start Date", "End Date", "Start Time", "End Time", "Duration"])

        lines = cleaned_data.splitlines()
        current_task = None

        # Step 3: Parse lines and fill out the CSV rows
        for line in lines:
            line = line.strip()
            
            # Check if line is a task name line (no commas means it's a title)
            if ',' not in line:
                current_task = line  # Update the current task name
            elif re.match(r'.*,.*,.*,.*,.*,.*,.*', line):  # This is a data row
                # Prepend task name only to data rows
                if current_task:
                    csv_writer.writerow([current_task] + line.split(','))
        
        return csv_output.getvalue()

