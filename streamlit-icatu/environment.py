

import os
from dotenv import load_dotenv

class environ:
    def __init__(self) -> None:
        for variavel in os.environ:
            setattr(self, variavel, os.environ[variavel])
load_dotenv()
env = environ()


