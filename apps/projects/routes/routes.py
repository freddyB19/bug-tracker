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


@router.get(
	"/{id}",
 	status_code = status.HTTP_200_OK,
 	response_model = schemas.ProjectResponse,
 )
def get_project(id: int) -> schemas.ProjectResponse:
	try:
		project = commands.command_get_project(project_id = id)
	except ValueError as e:
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_404_NOT_FOUND
		)

	return project


@router.put(
	"/{id}/title",
 	status_code = status.HTTP_200_OK,
 	response_model = schemas.ProjectSimpleResponse,
 )
def update_title(id: int, project: schemas.ProjectTitle) -> schemas.ProjectSimpleResponse:
	try:
		project = commands.command_update_title_project(project_id = id, infoUpdate = project)
	except ValueError as e:
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_404_NOT_FOUND
		)

	return project
