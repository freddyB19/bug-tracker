from typing import List
from typing_extensions import Annotated

from fastapi import status
from fastapi import Depends
from fastapi import Request
from fastapi import APIRouter
from fastapi import Query

from fastapi.responses import JSONResponse

from apps.projects.schemas import schemas
from apps.projects.commands import commands
from apps.users.commands import commands as c_users

from apps.utils.pagination import pagination as pg
from apps.utils.token.token import validate_authorization

router  = APIRouter(prefix = '/project')

STATUS_CODE_ERRORS = {
	400: status.HTTP_400_BAD_REQUEST,
	401: status.HTTP_401_UNAUTHORIZED,
	404: status.HTTP_404_NOT_FOUND,
}


@router.post(
	"/",
 	status_code = status.HTTP_201_CREATED,
 	response_model = schemas.ProjectResponse,
 )
def create_project(project: schemas.ProjectRequest, token: str = Depends(validate_authorization)) -> schemas.ProjectResponse:
	try:
		project = commands.command_create_project(project = project)
	except ValueError as e:
		message, status_code = e.args
		
		return JSONResponse(
			content = {"message": message},
			status_code = STATUS_CODE_ERRORS[status_code]
		)

	return project


@router.get(
	"/{id}",
 	status_code = status.HTTP_200_OK,
 	response_model = schemas.ProjectFullResponse,
 )
def get_project(id: int, token: str = Depends(validate_authorization)) -> schemas.ProjectFullResponse:
	try:
		project = commands.command_get_project(project_id = id)
	except ValueError as e:
		message, status_code = e.args

		return JSONResponse(
			content = {"message": message},
			status_code = STATUS_CODE_ERRORS[status_code]
		)

	return project


@router.put(
	"/{id}",
	status_code = status.HTTP_200_OK,
	response_model = schemas.ProjectSimpleResponse
)
def update_project(id: int, project: schemas.ProjectUpdate, token: str = Depends(validate_authorization)) -> schemas.ProjectSimpleResponse:
	try:
		project = commands.command_update_project(
			project_id = id,
			infoUpdate = project
		)
	except ValueError as e:
		message, status_code = e.args

		return JSONResponse(
			content = {"message": message},
			status_code = STATUS_CODE_ERRORS[status_code]
		)

	return project


@router.delete(
	"/{id}",
	status_code = status.HTTP_204_NO_CONTENT,
)
def delete_project(id: int, token: str = Depends(validate_authorization)) -> JSONResponse:
	try:
		commands.command_delete_project(
			project_id = id,
		)
	except ValueError as e:
		message, status_code = e.args

		return JSONResponse(
			content = {"message": message},
			status_code = STATUS_CODE_ERRORS[status_code]
		)


#TODO:
# Cambiar la ruta url de este endpoint
@router.get(
	"/list/user",
	status_code = status.HTTP_200_OK,
	response_model = schemas.ProjectsByUser
)
def get_project_by_user(request: Request, query: Annotated[schemas.ProjectsPagination, Query()],token: str = Depends(validate_authorization)) -> schemas.ProjectsByUser:

	try:
		
		user = c_users.command_get_user(
			user_id = query.user_id
		)
		
		total = commands.command_get_total_project_user(
			user_id = query.user_id
		)

		projects = commands.command_get_projects_user(
			page = query.page,
			pageSize = query.pageSize,
			user_id = query.user_id
		)

	except ValueError as e:
		message, status_code = e.args

		return JSONResponse(
			content = {"message": message},
			status_code = STATUS_CODE_ERRORS[status_code]
		)


	pagination = pg.set_url_pagination(
		request = pg.get_url_from_request(request = request),
		elements = projects,
		total_elements = total,
		page = query.page,
		pageSize = query.pageSize,
		params = {
			"user_id": query.user_id
		}
	)

	response = {
		"previous": pagination.get('previous'),
		"current": query.page,
		"next": pagination.get('next'),
		"user": user,
		"content": {
			"total": total,
			"projects": projects
		}
	}

	return response
