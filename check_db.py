import os
from urllib.parse import urlparse

url = os.environ.get("DATABASE_URL")

if not url:
    print("DATABASE_URL is NOT set")
else:
    u = urlparse(url)
    print("Host:", u.hostname)
    print("Port:", u.port)
    print("Database:", u.path.lstrip("/"))