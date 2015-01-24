from guif import Video
from cami import CamI
from post import Post, OUT_URL, IN_URL
from inp import InPost
import time

display = Video((640, 480))
cam = CamI(display)
ip = InPost(Post(OUT_URL), handlers=[cam])


try:
    time.sleep(10000)
except:
    pass
ip.STOP = True