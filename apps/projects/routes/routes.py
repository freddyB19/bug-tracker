from typing import List

from fastapi import status
from fastapi import Depends
from fastapi import Request
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from apps.projects.schemas import schemas
from apps.projects.commands import commands
from apps.users.commands import commands as c_users

from apps.utils.pagination import pagination as pg
from apps.utils.token.token import validate_authorization

router  = APIRouter(prefix = '/project')

@router.post(
	"/",
 	status_code = status.HTTP_201_CREATED,
 	response_model = schemas.ProjectResponse,
 )
def create_project(project: schemas.ProjectRequest, token: str = Depends(validate_authorization)) -> schemas.ProjectResponse:
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
def get_project(id: int, token: str = Depends(validate_authorization)) -> schemas.ProjectResponse:
	try:
		project = commands.command_get_project(project_id = id)
	except ValueError as e:
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_404_NOT_FOUND
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
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_404_NOT_FOUND
		)

	return project


@router.delete(
	"/{id}",
	status_code = status.HTTP_204_NO_CONTENT,
)
def delete_project(id: int, project: schemas.ProjectDelete, token: str = Depends(validate_authorization)) -> JSONResponse:
	try:
		commands.command_delete_project(
			project_id = id,
			infoDelete = project
		)
	except ValueError as e:
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_404_NOT_FOUND
		)

	return JSONResponse(
		content={"message": f"Proyecto: con ID '{id}' eliminado con exito."}
	)


@router.get(
	"/list/user",
	status_code = status.HTTP_200_OK,
	response_model = schemas.ProjectsPagination
)
def get_project_by_user(request: Request, user_id: int, page: int = 0, pageSize: int = 10,token: str = Depends(validate_authorization)) -> schemas.ProjectsPagination:

	try:
		
		user = c_users.command_get_user(
			user_id = user_id
		)
		
		total = commands.command_get_total_project_user(
			user_id = user_id
		)

		projects = commands.command_get_projects_user(
			page = page,
			pageSize = pageSize,
			user_id = user_id
		)
	
	except ValueError as e:
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_404_NOT_FOUND
		)


	pagination = pg.set_url_pagination(
		request = request,
		elements = projects,
		total_elements = total,
		page = page,
		pageSize = pageSize,
		params = {
			"user_id": user_id
		}
	)

	response = {
		"previous": pagination.get('previous'),
		"current": page,
		"next": pagination.get('next'),
		"user": user,
		"content": {
			"total": total,
			"projects": projects
		}
	}

	return response