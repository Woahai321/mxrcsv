import csv
from http.server import BaseHTTPRequestHandler
from io import StringIO

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Check for the '/api/convert-file' route
        if self.path == '/api/convert-file':  # Match the correct path
            self.handle_convert_file()
        else:
            # Send 404 if the path doesn't exist
            self.send_error(404, 'Not Found')

    def handle_convert_file(self):
        try:
            # Read the content of the POST request (long string data)
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
        headers_found = False

        for line in lines:
            # Skip over the unnecessary sections
            if line.startswith("Time Tracking"):
                continue  # Ignore the "Time Tracking" line

            # Identify the header line when it's encountered
            if not headers_found and line.startswith("Started By"):
                headers_found = True  # Mark that headers have been found
                continue  # Move on to processing data rows after headers

            if line.startswith("Total"):
                continue  # Ignore "Total" line

            # If the header wasn't found yet, treat the line as a comment
            if not headers_found:
                current_comment = line.strip()  # Treat this as a comment
                continue

            # By now, headers are set, and current_comment has been found—process row data
            if current_comment:
                values = line.split(",")  # Split the line by commas, assuming CSV format
                if len(values) >= 6:  # Ensure that the line has enough columns
                    parsed_data.append({
                        'Employee Name': values[0].strip(),
                        'Pay Period Start Date': values[2].strip(),
                        'Pay Period End Date': values[3].strip(),
                        'Start Time': values[4].strip(),
                        'End Time': values[5].strip(),
                        'Comment': current_comment.strip()
                    })
                current_comment = None  # Reset comment after processing the row

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
                'Rippling Emp No': '',  # Leave empty as per your template
                'Employee Name': entry['Employee Name'],
                'Import ID': '',  # Leave empty as per your template
                'Start Time': entry['Start Time'],
                'End Time': entry['End Time'],
                'Pay Period Start Date': entry['Pay Period Start Date'],
                'Pay Period End Date': entry['Pay Period End Date'],
                'Job Code': '',  # Leave empty as per your template
                'Comment': entry['Comment'],
                'Break Type': '',  # Leave empty as per your template
                'Break Start Time': '',  # Leave empty as per your template
                'Break End Time': ''  # Leave empty as per your template
            })

        return output.getvalue()
