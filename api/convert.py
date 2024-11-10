# api/convert.py
import json
import pandas as pd
from io import StringIO

def handler(request):
    try:
        # Parse the POST request data
        body = request.get_json(silent=True)

        # Assume input is a list of dictionaries (rows of data)
        data = body.get("data", [])
        df = pd.DataFrame(data)

        # Convert dataframe to csv without headers and indexes
        csv_output = StringIO()
        df.to_csv(csv_output, index=False)

        # Return the CSV content as the response
        return (json.dumps({"csv": csv_output.getvalue()}), 200, {"Content-Type": "application/json"})
    except Exception as e:
        return (json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"})
