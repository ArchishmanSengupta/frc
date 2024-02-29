import requests
from bs4 import BeautifulSoup
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_token = os.getenv("SLACK_TOKEN")

# Create WebClient instance
client = WebClient(token=slack_token)

sebi_url = "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListingAll=yes&sid=1&ssid=7&smid=0"
rbi_url = "https://www.rbi.org.in/scripts/bs_viewmastercirculars.aspx"
last_sebi_circular = None
last_rbi_circular = None
last_post_time = None
last_check_time = time.time()

while True:
    if time.time() - last_check_time >= 3:
        # Scrape SEBI website
        response = requests.get(sebi_url)
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

                if last_sebi_circular is None or new_circular != last_sebi_circular:
                    break

        if new_circular:
            try:
                message = f"*New SEBI Circular*\n\nType: {new_circular_type}\n\nDate: {new_date}\n\nTitle: {new_circular}\n\nLink: {new_link}"
                response = client.chat_postMessage(channel="#sebi-updates", text=message)
                print(f"Posted message: {message}")
                last_sebi_circular = new_circular
                last_post_time = time.time()
            except SlackApiError as e:
                print(f"Error posting message: {e}")

        # Scrape RBI website
        rbi_response = requests.get(rbi_url)
        rbi_soup = BeautifulSoup(rbi_response.content, "html.parser")
        rbi_rows = rbi_soup.find_all("tr")
        for row in rbi_rows:
            cells = row.find_all("td")
            if len(cells) == 2:
                new_rbi_date = cells[0].text.strip()
                title_link = cells[0].find("a")
                if title_link:
                    new_rbi_circular = title_link.text.strip()
                    pdf_link_cell = cells[1]
                    pdf_link = pdf_link_cell.find("a")["href"]
                    new_rbi_link = pdf_link
                    try:
                        rbi_message = f"*New RBI Circular*\n\nDate: {new_rbi_date}\n\nTitle: {new_rbi_circular}\n\nLink: {new_rbi_link}"
                        response = client.chat_postMessage(channel="#sebi-updates", text=rbi_message)
                        print(f"Posted RBI message: {rbi_message}")
                        last_rbi_circular = new_rbi_circular
                        last_post_time = time.time()
                    except SlackApiError as e:
                        print(f"Error posting RBI message: {e}")

        # Check for updates every 3 seconds
        last_check_time = time.time()
        print("Last Check Time: ", last_check_time)

    time.sleep(1)
