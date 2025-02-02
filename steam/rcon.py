from rcon.source import Client
import os

ADMIN_PASSWORD = os.environ.get('RCON_ADMIN_PASSWORD', 'RCON_DISABLED')

class NoExceptClient:
    def __init__(self, *args, disabled=False, **kwargs):
        self.client = Client(*args, **kwargs)
        self.valid = False

    def run(self, *args, **kwargs):
        if self.valid:
            return self.client.run(*args, enforce_id=False, **kwargs)
        else:
            return ""
    
    def __enter__(self):
        try:
            self.client.__enter__()
            self.valid = True
        except Exception as e:
            print("Failed to start RCON client:", e)
        return self

    def __exit__(self, *args):
        if self.valid:
            self.client.__exit__(*args)

def rcon():
    return NoExceptClient('localhost', 25575, disabled=(ADMIN_PASSWORD == 'RCON_DISABLED'), passwd=ADMIN_PASSWORD)

