import os
import time
import requests
from bs4 import BeautifulSoup
from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

WEBPAGE_URLS = [
    'https://www.mercari.com/search/?keyword=iphone&sortBy=2'
]
  # Replace with your URLs
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')  # Replace with your Discord Webhook URL

def notify_discord(message, url):
    data = {
        "content": f"{message} [Link to webpage]({url})"
    }
    result = requests.post(DISCORD_WEBHOOK_URL, json=data)

    if 200 <= result.status_code < 300:
        print(f"Notification sent, status {result.status_code}")
    else:
        print(f"Notification failed to send with status {result.status_code}")
        print(result.json())

def retrieve_listings(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(url)
    time.sleep(3)

    soup = BeautifulSoup(browser.page_source, "html.parser")

    search_results = soup.find("div", {"data-testid" : "SearchResults"}).find("div").find("div").find_all("div", recursive=False)

    listings = set()
    for search_result in search_results:
        _id = search_result.find("a").find("div")["data-productid"]
        listings.add(_id)
    
    browser.quit()
    return listings

class WebpageMonitor:
    def __init__(self, url):
        self.url = url
        self.previous_listings = None

    def monitor(self):
        while True:
            time.sleep(60) # Change this to the amount of time you want to wait between checks
            listings = retrieve_listings(self.url)

            if self.previous_listings and self.previous_listings != listings:
                print(f"Change detected at {self.url}!")
                print(f"Previous listings: {self.previous_listings}")
                print(f"Current listings: {listings}")
                notify_discord(f"Change detected at the webpage: {self.url}", self.url)

            self.previous_listings = listings

if __name__ == "__main__":
    threads = []

    for url in WEBPAGE_URLS:
        monitor = WebpageMonitor(url)
        thread = Thread(target=monitor.monitor)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
