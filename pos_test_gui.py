from threading import Thread
import time

from communication.link import Link
from communication.handlers.commander import OutCommander
from communication.handlers.info import InInfo
from communication.handlers.status import InStatus
from communication.in_handle import InPost
from communication.out_handle import OutPost

link = Link(quad=False)
# IN handlers
out_handlers = [OutCommander()]
# OUT handlers - they will be accessed directly so they need to have separate names
messenger = InInfo(None)
updater = InStatus(None)
in_handlers = [messenger, updater]
# Initialise posts, they will not be called directly.
in_post = InPost(link, handlers=in_handlers)
out_post = OutPost(link, handlers=out_handlers)
out = Thread(target=in_post._handle_loop)  # executes commands from master
inp = Thread(target=out_post._handle_loop)  # sends important parameters to the master
out.daemon = inp.daemon = True
out.start()
inp.start()
time.sleep(1000)
