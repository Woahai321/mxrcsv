import csv
import io
from http.server import BaseHTTPRequestHandler
from io import StringIO

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/convert-file':
            self.handle_convert_file()
        else:
            self.send_error(404, 'Not Found')

    def handle_convert_file(self):
        try:
            # Read the content of the POST request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')

            # Parse the long string data
            parsed_data = self.parse_string_data(post_data)

            # Convert the parsed data to the required template
            template_data = self.convert_to_template(parsed_data)

            # Send the response
            self.send_response(200)
            self.send_header('Content-type', 'text/csv')
            self.end_headers()
            self.wfile.write(template_data.encode('utf-8'))

        except Exception as e:
            self.send_error(400, str(e))

    def parse_string_data(self, data):
        # Split the data into lines
        lines = data.splitlines()

        # Initialize variables to store parsed data
        parsed_data = []
        current_comment = None

        for line in lines:
            if line.startswith("Time Tracking"):
                continue  # Ignore the "Time Tracking" line

            if line.startswith("Started By"):
                headers = line.split()
                continue

            if line.startswith("Total"):
                continue  # Ignore the "Total" line

            if not headers:
                current_comment = line
                continue

            if current_comment:
                values = line.split()
                parsed_data.append({
                    'Employee Name': values[0],
                    'Pay Period Start Date': values[2],
                    'Pay Period End Date': values[3],
                    'Start Time': values[4],
                    'End Time': values[5],
                    'Comment': current_comment
                })
                current_comment = None

        return parsed_data

    def convert_to_template(self, data):
        # Define the template headers
        template_headers = [
            'Rippling Emp No', 'Employee Name', 'Import ID', 'Start Time', 'End Time',
            'Pay Period Start Date', 'Pay Period End Date', 'Job Code', 'Comment',
            'Break Type', 'Break Start Time', 'Break End Time'
        ]

        # Convert the parsed data to CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=template_headers)
        writer.writeheader()

        for entry in data:
            writer.writerow({
                'Rippling Emp No': '',
                'Employee Name': entry['Employee Name'],
                'Import ID': '',
                'Start Time': entry['Start Time'],
                'End Time': entry['End Time'],
                'Pay Period Start Date': entry['Pay Period Start Date'],
                'Pay Period End Date': entry['Pay Period End Date'],
                'Job Code': '',
                'Comment': entry['Comment'],
                'Break Type': '',
                'Break Start Time': '',
                'Break End Time': ''
            })

        return output.getvalue()
