import re
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from googlesearch import search
from bs4 import BeautifulSoup
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):

    # Function to extract LinkedIn URL for a company
    def find_linkedin_url(self, company_name):
        query = f"{company_name} site:linkedin.com/company"
        for result in search(query, num_results=5):
            if 'linkedin.com/company' in result:
                return result  # First relevant LinkedIn company URL
        return None

    # Function to scrape LinkedIn page for company information
    def scrape_linkedin_data(self, linkedin_url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        }
        response = requests.get(linkedin_url, headers=headers)
        if response.status_code != 200:
            return None  # No data fetched

        soup = BeautifulSoup(response.text, 'html.parser')

        # Parsing out specific company information
        data = {}

        try:
            # Extracting Company Details; these selectors are based on LinkedIn's structure
            data["Found LinkedIn Company Name"] = soup.find("h1", {"class": "top-card-layout__title"}).get_text(strip=True)

            data["Found LinkedIn Company Information"] = soup.find("p", {"class": "description"}).get_text(strip=True)
            
            # Followers count
            followers_text = soup.find(text=re.compile(r"\d+ followers"))
            data["Found LinkedIn Followers"] = followers_text.strip() if followers_text else "N/A"

            # 'About Us' Section
            about_us_section = soup.find("section", {"class": "about-us"})
            data["Found LinkedIn About Us"] = about_us_section.get_text(strip=True) if about_us_section else "N/A"

            # Website, some times wrapped in a class like 'link-without-visited-state'
            try:
                data["Found LinkedIn Website"] = soup.find("a", {"class": "link-without-visited-state"}).get("href")
            except AttributeError:
                data["Found LinkedIn Website"] = "N/A"

            # Extracting other company details like headquarters, industry, type, etc.
            location_elem = soup.find("span", string="Headquarters")
            if location_elem:
                data["Found LinkedIn Location"] = location_elem.find_next("span").get_text(strip=True)
            else:
                data["Found LinkedIn Location"] = "Location not available"

            industry_elem = soup.find("span", string="Industry")
            if industry_elem:
                data["Industry"] = industry_elem.find_next("span").get_text(strip=True)
            else:
                data["Industry"] = "Industry not available"

            size_elem = soup.find("span", string="Company size")
            data["Company Size"] = size_elem.find_next("span").get_text(strip=True) if size_elem else "Company size not available"

            headquarters_elem = soup.find("span", string="Headquarters")
            data["Headquarters"] = headquarters_elem.find_next("span").get_text(strip=True) if headquarters_elem else "Headquarters not available"

            type_elem = soup.find("span", string="Type")
            data["Type"] = type_elem.find_next("span").get_text(strip=True) if type_elem else "Type not available"

            founded_elem = soup.find("span", string="Founded")
            data["Founded"] = founded_elem.find_next("span").get_text(strip=True) if founded_elem else "Founded year not available"

            # Specialties may be located in a different section
            specialties_elem = soup.find("span", string=re.compile(r"Specialties"))
            data["Specialties"] = specialties_elem.find_next("span").get_text(strip=True) if specialties_elem else "No specialties available"
        
            # Multiple locations might be provided
            locations_elem = soup.find_all("span", string=re.compile(r"Location"))
            data["Locations"] = [loc.find_next("span").get_text(strip=True) for loc in locations_elem] if locations_elem else "No locations available"

        except Exception as e:
            data["error"] = f"Failed to parse LinkedIn page. Error: {str(e)}"

        return data

    # Handle POST requests for API calls
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        # Expect the input to be a company name (in plain text)
        company_name = post_data.strip()

        # URL encode the company name for use in search queries
        company_name_encoded = urllib.parse.quote(company_name)

        # Step 1: Find LinkedIn URL for the company using Google search
        linkedin_url = self.find_linkedin_url(company_name_encoded)

        if linkedin_url:
            # Step 2: Scrape LinkedIn URL to extract relevant company information
            linkedin_data = self.scrape_linkedin_data(linkedin_url)

            if linkedin_data:
                response = {
                    "company_name": company_name,
                    "linkedin_url": linkedin_url,
                    "data": linkedin_data
                }
                # Return the response with company data
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_error(500, "Failed to fetch or parse LinkedIn data")
        else:
            self.send_error(404, "LinkedIn profile not found for the company")

# Run the server
if __name__ == "__main__":
    PORT = 8000
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, handler)
    print(f"Serving HTTP API on port {PORT}.")
    httpd.serve_forever()
