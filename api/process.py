import csv
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import StringIO
import re
import cgi

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            # Check if content type is plain text as expected
            content_type, _ = cgi.parse_header(self.headers['Content-Type'])

            if content_type == 'text/plain':
                # Read the data sent in the POST request body
                content_length = int(self.headers['Content-Length'])
                raw_data = self.rfile.read(content_length).decode('utf-8')

                # Clean and parse the raw input data
                cleaned_data = self.parse_and_clean_data(raw_data)

                # Send response status
                self.send_response(200)
                self.send_header('Content-type', 'text/csv')
                self.end_headers()

                # Write the cleaned CSV to the response
                self.wfile.write(cleaned_data.encode('utf-8'))

            else:
                # If Content-Type is not plain text, send a 400 error
                self.send_error(400, 'Unsupported Content-Type. Expected text/plain.')
        except Exception as e:
            self.send_error(500, str(e))

    def parse_and_clean_data(self, raw_data):
        """
        Clean and process the input data into CSV format based on the desired column mappings.
        """
        # Initialize an in-memory CSV output
        csv_output = StringIO()
        csv_writer = csv.writer(csv_output)

        # Write the CSV header based on the desired fields
        csv_writer.writerow(["Comment", "Employee Name", "Pay Period Start Date", "Pay Period End Date", "Start Time", "End Time"])

        # Task processing state
        current_comment = None  # To track the current task/comment name

        # Split the raw data into lines by line break (`\n`)
        lines = raw_data.splitlines()

        # Regex expressions for valid data row structure
        data_row_pattern = re.compile(r'^[^,]+,[^,]+,[^,]+,[^,]+,[^,]+,[^,]+,[^,]+$')
        header_pattern = re.compile(r'^Started By,Ended By,Start Date,End Date,Start Time,End Time,Duration$')

       # print("### RAW DATA ###")
        #print(raw_data)
       # print("### SPLIT LINES ###")

        for line in lines:
            line = line.strip()

            # Skip unnecessary lines like 'Time Tracking', empty lines, or known "Total" lines
            if not line or line.startswith(',') or line.startswith('Time Tracking') or line.startswith('Total'):
                #print(f"Skipping line: '{line}' (empty, Time Tracking, or redundant)")
                continue

            # Skip internal header rows found inside the data
            if header_pattern.match(line):
                #print(f"Skipping header line inside data: '{line}'")
                continue

            #print(f"Processing line: '{line}'")

            # If the line matches the data row pattern (valid comma-separated row)
            if data_row_pattern.match(line):
                task_data = line.split(',')

                # Validate that we have a comment associated with the task data
                if current_comment:
                    # Employee Row Mapping
                    employee_name = task_data[0]  # 'Started By'
                    pay_period_start = task_data[2]  # 'Start Date'
                    pay_period_end = task_data[3]  # 'End Date'
                    start_time = task_data[4]  # 'Start Time'
                    end_time = task_data[5]  # 'End Time'
                    
                    # Write the mapped row to CSV
                    csv_writer.writerow([current_comment, employee_name, pay_period_start, pay_period_end, start_time, end_time])
                    #print(f"Writing CSV row: {current_comment}, {employee_name}, {pay_period_start}, {pay_period_end}, {start_time}, {end_time}")
                else:
                    print(f"Warning: No comment found for data row, please debug.")
                    #print(f"Warning: No comment found for data row: {line}")
            else:
                # Treat this line as a new "comment" or task name
                current_comment = line.split(',')[0].strip()  # Extract the first part before the first comma as the comment/task name
                #print(f"Found comment: {current_comment}")

        # Return the CSV data as string
        return csv_output.getvalue()

# Run the server
if __name__ == "__main__":
    PORT = 8000
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, handler)
    print(f"Serving HTTP API on port {PORT}.")
    httpd.serve_forever()
