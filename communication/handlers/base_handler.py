
class InHandler:
    """Handle method called on incoming traffic marked with this ID"""
    ID = None

    def handle(self, req):
        pass


class OutHandler:
    """Call its methods to automatically trigger response in recipient."""
    ID = None
    out = None

    def set_post(self, post):
        self.out = post

    def send(self, req):
        if self.out:
            self.out.add(req, self.ID)

