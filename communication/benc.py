
def to_bytes(integer, n):
    dl8 = ''
    for e in xrange(n):
        dl8 = chr(integer%256) + dl8
        integer /= 256
    return dl8

def from_bytes(bytes):
    r = 0
    for e in bytes:
        r = 256*r + ord(e)
    return r