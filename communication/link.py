import urllib2

IN_URL = 'https://piotr-dabkowski.appspot.com/rpi'
OUT_URL = 'https://piotr-dabkowski.appspot.com/rpo'


class Link:
    def __init__(self, quad=True):
        if quad:
            self.in_link = IN_URL
            self.out_link = OUT_URL
        else:
            self.in_link = OUT_URL
            self.out_link = IN_URL

    def get(self):
        try:
            return urllib2.urlopen(self.in_link).read()
        except:
            return False

    def send(self, data):
        try:
            urllib2.urlopen(self.out_link, data)
            return True
        except:
            return False
