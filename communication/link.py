import urllib2

IN_URL = 'https://piotr-dabkowski.appspot.com/rpi'
OUT_URL = 'https://piotr-dabkowski.appspot.com/rpo'

class Post:
    def __init__(self, url):
        self.url = url

    def get(self):
        return urllib2.urlopen(self.url).read()

    def send(self, data):
        urllib2.urlopen(self.url, data)