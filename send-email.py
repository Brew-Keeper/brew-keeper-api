import requests
import os

key = os.environ['MAILGUN_KEY']
sandbox = 'sandbox014f80db3f0b441e94e5a6faff21f392.mailgun.org'
recipient = 'example@example.com'
html = """\
           Would you like to reset your password?
           Here is the http://www.python.org link you wanted.
"""
request_url = 'https://api.mailgun.net/v3/{}/messages'.format(sandbox)
request = requests.post(request_url, auth=('api', key), data={
    'from': 'Mailgun Sandbox <postmaster@sandbox014f80db3f0b441e94e5a6faff21f392.mailgun.org>',
    'to': recipient,
    'subject': 'Hello',
    'text': html
})

print('Status: {}'.format(request.status_code))
print('Body:   {}'.format(request.text))
