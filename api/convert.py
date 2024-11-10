from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
from io import StringIO

class handler(BaseHTTPRequestHandler):
    # Handle POST requests
    def do_POST(self):
        # Set the response headers to JSON
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()

        # Read and parse the request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        body = json.loads(post_data.decode('utf-8'))

        # Validate input data
        if body is None or "data" not in body:
            error_response = json.dumps({"error": "Invalid input or missing 'data' field."})
            self.wfile.write(error_response.encode('utf-8'))
            return
        
        data = body.get("data", [])
        # Ensure each item has 'name' and 'age'
        for item in data:
            if "name" not in item or "age" not in item:
                error_response = json.dumps({"error": "Each item must have 'name' and 'age'."})
                self.wfile.write(error_response.encode('utf-8'))
                return

        # Convert data into a CSV format using pandas
        df = pd.DataFrame(data)
        csv_output = StringIO()
        df.to_csv(csv_output, index=False)
        
        # Return the CSV as part of the JSON response
        success_response = json.dumps({"csv": csv_output.getvalue()})
        self.wfile.write(success_response.encode('utf-8'))
