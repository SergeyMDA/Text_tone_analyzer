import requests

from Microservices import Packer

data = Packer.pack({'text': input('text: ')})
default_port = 5000

response = requests.get(f'http://localhost:{default_port}/document/split/trigrams',
                        params={'content': data}).content.decode('utf-8')

unigrams = Packer.unpack(response)['response']['trigrams']
print(unigrams)
