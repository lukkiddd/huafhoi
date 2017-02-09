import sys
from wit import Wit

access_token = "ELQM7CPEYW2YP6ODFKCCC7QLV6PE4WWZ"

def send(request, response):
    print(response['text'])

actions = {
    'send': send,
}

client = Wit(access_token=access_token, actions=actions)
client.interactive()