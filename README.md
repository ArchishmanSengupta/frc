# Fintech Regulation Scrapper

- Fintech is a highly regulated domain and abiding by the rules and laws becomes extremely crucial. 
- This Slack Bot aims to bridge the gap between the fintech players and the govt to get automated responses.

This Slack Bot notifies the Slack channel whenever a new SEBI/RBI Circular is being posted on the SEBI/RBI portal.

## Scrapping Urls:
- [x] SEBI: https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListingAll=yes&sid=1&ssid=7&smid=0
- [x] RBI: https://www.rbi.org.in/scripts/bs_viewmastercirculars.aspx
- [ ] AMFI: Pending

## Process:
1. Install the bot
2. Setup AWS Lambda
3. Or setup Amazon [Event Bridge Scheduler](https://aws.amazon.com/blogs/compute/introducing-amazon-eventbridge-scheduler/)
4. Set up a cron-job every alternate days ~ 365/2 ~ 182 calls per year
5. Lambda charges = ```memory consumed price * time```
6. If EC2 instance is already running, host the scrapping script there and crontab on it


![image](https://user-images.githubusercontent.com/71402528/224565099-03152e0d-3ecd-49e9-9d9b-bce63aaf643e.png)
