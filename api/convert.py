import csv
import io
import zipfile
from http.server import BaseHTTPRequestHandler
import cgi
import openpyxl

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse the multipart form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']}
            )

            # Extract the file content
            file_item = form['file']
            if file_item.file:
                binary_data = file_item.file.read()

                # Parse the binary data
                parsed_data = self.parse_binary_data(binary_data)

                # Convert the parsed data to CSV
                csv_data = self.convert_to_csv(parsed_data)

                # Send the response
                self.send_response(200)
                self.send_header('Content-type', 'text/csv')
                self.end_headers()
                self.wfile.write(csv_data.encode('utf-8'))
            else:
                self.send_error(400, 'No file uploaded')

        except Exception as e:
            self.send_error(400, str(e))

    def parse_binary_data(self, binary_data):
        # Check if the binary data is a ZIP file (Excel files are often ZIP archives)
        if binary_data[:2] == b'PK':
            return self.parse_excel_data(binary_data)
        else:
            return self.parse_csv_data(binary_data)

    def parse_excel_data(self, binary_data):
        # Extract the Excel file from the ZIP archive
        with zipfile.ZipFile(io.BytesIO(binary_data)) as zf:
            with zf.open('xl/worksheets/sheet1.xml') as f:
                # Load the Excel workbook
                workbook = openpyxl.load_workbook(io.BytesIO(binary_data))
                sheet = workbook.active
                return self.convert_excel_to_csv(sheet)

    def parse_csv_data(self, binary_data):
        # Convert binary data to string and parse as CSV
        csv_data = binary_data.decode('utf-8', errors='ignore')
        return csv_data

    def convert_excel_to_csv(self, sheet):
        # Convert the Excel sheet to CSV
        output = io.StringIO()
        writer = csv.writer(output)
        for row in sheet.iter_rows(values_only=True):
            writer.writerow(row)
        return output.getvalue()

    def convert_to_csv(self, data):
        # Convert the parsed data to CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Define the desired CSV headers
        headers = [
            "Rippling Emp No", "Employee Name", "Import ID", "Start Time", "End Time",
            "Pay Period Start Date", "Pay Period End Date", "Job Code", "Comment",
            "Break Type", "Break Start Time", "Break End Time"
        ]
        writer.writerow(headers)

        # Parse the input data and map to the desired CSV format
        lines = data.splitlines()
        header_found = False
        for line in lines:
            if line.startswith("Started By"):
                header_found = True
                continue
            if line.startswith("Total"):
                header_found = False
                continue
            if line.strip() == "":
                continue

            if header_found:
                parts = line.split('\t')
                if len(parts) == 7:
                    started_by, ended_by, start_date, end_date, start_time, end_time, duration = parts
                    writer.writerow([
                        "", started_by, "", start_time, end_time, start_date, end_date, "", "", "", "", ""
                    ])

        return output.getvalue()
