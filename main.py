import os
import sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE)
sys.path.append(os.path.join(BASE, "apps"))

from fastapi import FastAPI
from apps.users.routes import router as router_users
from apps import engine
from apps import Model


app = FastAPI()

Model.metadata.create_all(engine)

app.include_router(router_users)

