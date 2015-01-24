from camo import CamO
from post import Post, OUT_URL, IN_URL
from out import OutPost
import time
print 'Imported'
op = OutPost(Post(OUT_URL), cam=CamO())
print 'Initialized'
try:
    time.sleep(10000)
except:
    pass
op.STOP = True
