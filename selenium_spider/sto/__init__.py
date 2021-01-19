import json
import os

STO_ROOT = os.path.dirname(__file__)
credential_path = os.path.join(STO_ROOT, "credentials.json")
with open(credential_path, 'r') as f:
    credentials = json.load(f)

