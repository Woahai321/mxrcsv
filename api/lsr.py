import re
import time
from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
from googlesearch import search
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

def scrape_linkedin_data_using_selenium(linkedin_url):
    try:
        options = uc.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")

        # Specify Chrome binary location (use Vercel's path)
        options.binary_location = "/usr/bin/chromium-browser"

        driver = uc.Chrome(options=options)
        driver.get(linkedin_url)

        # Wait for any overlay to disappear
        try:
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'modal__overlay--visible')]"))
            )
            print("Overlay has disappeared!")
        except TimeoutException:
            print("No overlay found. Proceeding...")

        # Find the "Dismiss" button and force click using JavaScript (in case the click is blocked)
        try:
            dismiss_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Dismiss')]"))
            )
            driver.execute_script("arguments[0].click();", dismiss_button)
            print("Popup dismissed!")
        except TimeoutException:
            print("No dismiss button found.")

        # Wait for the main content to load
        time.sleep(3)

        # Extract company name
        data = {}
        try:
            company_name = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".top-card-layout__title"))
            ).text.strip()
        except TimeoutException:
            company_name = "Not Available"
        data["Found LinkedIn Company Name"] = company_name

        # Extract company information
        try:
            company_info_section = driver.find_element(By.CSS_SELECTOR, "p[data-test-id='about-us__description']").text.strip()
        except NoSuchElementException:
            company_info_section = "Not Available"
        data["Found LinkedIn Company Information"] = company_info_section

        # Extract the website link
        try:
            website_link = driver.find_element(By.XPATH, "//a[@data-test-id='about-us__website']").get_attribute("href")
        except NoSuchElementException:
            website_link = "Not Available"
        data["Found LinkedIn Website"] = website_link

        # Additional company information (Industry, Size, Headquarters, etc.)
        info_sections = {
            "Industry": "about-us__industry",
            "Company size": "about-us__size",
            "Headquarters": "about-us__headquarters",
            "Type": "about-us__organizationType",
            "Founded": "about-us__foundedOn",
            "Specialties": "about-us__specialties",
        }

        # Loop over each section to extract data
        for section, data_test_id in info_sections.items():
            try:
                data[section] = driver.find_element(By.XPATH, f"//div[@data-test-id='{data_test_id}']//dd").text.strip()
            except NoSuchElementException:
                data[section] = "Not Available"

        # Close the browser and return data
        driver.quit()
        return data

    except Exception as e:
        return {"error": f"An error occurred while scraping LinkedIn: {str(e)}"}

# HTTP server handler in serverless format (compatible with Vercel)
class handler(BaseHTTPRequestHandler):

    # Locate LinkedIn URL using a Google search
    def find_linkedin_url(self, company_name):
        query = f"{company_name} site:linkedin.com/company"
        for result in search(query, num_results=5):
            if 'linkedin.com/company' in result:
                return result
        return None

    # Handle POST requests
    def do_POST(self):
        # Read request body (company name)
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length).decode('utf-8')

        company_name = post_data.strip()  # Extract company name from request

        # Search for the company's LinkedIn URL via Google
        linkedin_url = self.find_linkedin_url(urllib.parse.quote(company_name))

        # If LinkedIn profile found, start scraping
        if linkedin_url:
            linked_in_data = scrape_linkedin_data_using_selenium(linkedin_url)
            response = {
                "company_name": company_name,
                "linkedin_url": linkedin_url,
                "data": linked_in_data
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        else:
            # Send 404 if LinkedIn profile is not found
            self.send_error(404, "LinkedIn profile not found for the company")

# Vercel will map HTTP requests here automatically. 
if __name__ == "__main__":
    import os
    PORT = int(os.getenv('PORT', 8000))
    from http.server import HTTPServer
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, handler)
    print(f"Serving HTTP API on port {PORT}")
    httpd.serve_forever()
