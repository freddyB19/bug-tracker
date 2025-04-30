import os
import sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE)
sys.path.append(os.path.join(BASE, "apps"))

from fastapi import status
from fastapi import FastAPI
from fastapi import Request
from fastapi.exceptions import RequestValidationError

from fastapi.responses import JSONResponse

from pydantic import ValidationError

from apps import Model
from apps import engine

from apps.users.routes import router as router_users
from apps.tickets.routes import router as router_ticket
from apps.projects.routes import router as router_project

app = FastAPI()

@app.exception_handler(RequestValidationError)
def validation_error_exception_handler(request: Request, exc: RequestValidationError):
	error = exc.errors()[0]

	content = {}

	if error["type"] == "value_error":
		detail = f"Input error: {error['input']}"
		content.update({"detail": detail})

	message = error['msg'].replace("Value error,", "").strip()
	content.update({"message": message})
	
	return JSONResponse(
		 status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
		 content = content
	)

Model.metadata.create_all(engine)

app.include_router(router_users)
app.include_router(router_ticket)
app.include_router(router_project)


