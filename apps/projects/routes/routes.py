from fastapi import APIRouter
from fastapi import status
from fastapi.responses import JSONResponse

from apps.projects.schemas import schemas
from apps.projects.commands import commands


router  = APIRouter(prefix = '/project')

@router.post(
	"/",
 	status_code = status.HTTP_201_CREATED,
 	response_model = schemas.ProjectResponse,
 )
def create_project(project: schemas.ProjectRequest) -> schemas.ProjectResponse:
	try:
		project = commands.command_create_project(project = project)
	except ValueError as e:
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_400_BAD_REQUEST
		)

	return project