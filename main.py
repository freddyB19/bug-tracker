import os
import sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE)
sys.path.append(os.path.join(BASE, "apps"))

from fastapi import FastAPI
from apps.users.routes import router as router_users

app = FastAPI()
app.include_router(router_users)