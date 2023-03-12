import requests
from bs4 import BeautifulSoup
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token="<SLACK_TOKEN>")
url = "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListingAll=yes&sid=1&ssid=0&smid=0"
last_circular = None
last_post_time = None
last_check_time = time.time()

ten_days = 10*24*60*60

while True:
    if time.time() - last_check_time >= 120:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        rows = soup.find_all("tr")
        new_circular = None
        new_link = None
        new_circular_type = None
        new_date = None
        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 3:
                new_date = cells[0].text.strip()
                new_circular_type = cells[1].text.strip()
                title_link = cells[2].find("a")
                new_circular = title_link.text.strip()
                new_link = title_link["href"]
                
                if last_circular is None or new_circular != last_circular:
                    break

        if new_circular:
            try:
                message = f"*New SEBI Circular*\n\nType: {new_circular_type}\n\nDate: {new_date}\n\nTitle: {new_circular}\n\nLink: {new_link}"
                response = client.chat_postMessage(channel="#sebi-updates", text=message)
                print(f"Posted message: {message}")
                
                last_circular = new_circular
                last_post_time = time.time()
            except SlackApiError as e:
                print(f"Error posting message: {e}")
        else:
            try:
                message = "No new circular found in the last 10 days."
                response = client.chat_postMessage(channel="#sebi-updates", text=message)
                print(f"Posted message: {message}")
            except SlackApiError as e:
                print(f"Error posting message: {e}")
            
        last_check_time = time.time()
        print("Last Check Time: ", last_check_time)
    
    time.sleep(120)
