# api/convert.py
import json
import pandas as pd
from io import StringIO

def handler(request):
    try:
        # Try to parse the incoming JSON object from the request body
        body = request.get_json(silent=True)
        
        # Check if the request body contains data, if not return a 400 error
        if body is None or "data" not in body:
            return (json.dumps({"error": "Invalid input format or missing 'data' field."}), 400, {"Content-Type": "application/json"})
        
        # Validate that all items in the 'data' list contain 'name' and 'age' keys
        data = body.get("data", [])
        for item in data:
            if "name" not in item or "age" not in item:
                return (json.dumps({"error": "Each data item must have 'name' and 'age' fields."}), 400, {"Content-Type": "application/json"})

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(data)

        # Prepare the CSV as a string in memory (like a file)
        csv_output = StringIO()
        df.to_csv(csv_output, index=False)  # Convert DataFrame to CSV format
        
        # Return the CSV as a string within the response
        return (json.dumps({"csv": csv_output.getvalue()}), 200, {"Content-Type": "application/json"})

    except Exception as e:
        # Catch and log any other exceptions, return a 500 error with relevant info
        return (json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"})
