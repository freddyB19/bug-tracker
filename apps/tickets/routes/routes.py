from typing import Optional
from typing_extensions import Annotated

from fastapi import status
from fastapi import Request
from fastapi import APIRouter
from fastapi import Query
from fastapi import Depends
from fastapi.responses import JSONResponse

from apps.tickets.schemas import schemas
from apps.tickets.commands import commands
from apps.tickets.models import StateTicketHistory

from apps.projects.commands import commands as c_projects

from apps.utils.pagination import pagination as pg
from apps.utils.token.token import validate_authorization


router = APIRouter(prefix = "/ticket")

@router.post(
	"/",
	status_code = status.HTTP_201_CREATED,
	response_model = schemas.TicketSimpleResponse
)
def create_ticket(ticket: schemas.TicketRequest, token: str = Depends(validate_authorization)) -> schemas.TicketSimpleResponse:
	try:
		new_ticket = commands.command_create_ticket(
			ticket = ticket
		)

		commands.command_add_history_ticket(
			ticket_id = new_ticket.id, 
			state = StateTicketHistory.crear.name
		)
	except ValueError as e:
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_400_BAD_REQUEST
		)

	return new_ticket


@router.get(
	"/{id}",
	status_code = status.HTTP_200_OK,
	response_model = schemas.TicketResponse
)
def get_ticket(id: int, token: str = Depends(validate_authorization)) -> schemas.TicketResponse:
	try:
		ticket = commands.command_get_ticket(
			ticket_id = id
		)
	except ValueError as e:
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_404_NOT_FOUND
		)

	return ticket


@router.get(
	"/project/{project_id}/search",
	status_code = status.HTTP_200_OK,
	response_model = schemas.TicketsByProjectResponse
)
def get_ticket_by_filter(request: Request, project_id: int, ticket_filter: Annotated[schemas.TicketFilterPagination, Query()], token: str = Depends(validate_authorization)) -> schemas.TicketsByProjectResponse:
	
	try:

		project = c_projects.command_get_project(
			project_id = project_id
		)

		total_tickets = commands.command_get_total_tickets_filter(
			infoFilter = ticket_filter,
			project_id = project_id
		)
		
		tickets = commands.command_get_ticket_by_filter(
			infoFilter = ticket_filter,
			project_id = project_id
		)
	except ValueError as e:
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_404_NOT_FOUND
		)

	search = ticket_filter.model_dump(
		exclude_defaults = True, 
		exclude=['page', 'pageSize']
	)
	pagination = pg.set_url_pagination(
		request = request,
		elements = tickets,
		total_elements = total_tickets,
		page = ticket_filter.page,
		pageSize = ticket_filter.pageSize,
		params = search 
	)

	response = {
		"previous": pagination.get('previous'),
		"current": ticket_filter.page,
		"next": pagination.get("next"),
		"project": project,
		"content": {
			"total": total_tickets,
			"tickets": tickets
		}	
	}
	
	return response


@router.get(
	"/search/title",
	status_code = status.HTTP_200_OK,
	response_model = schemas.TicketSimpleResponse
)
def get_ticket_by_title(ticket: schemas.TicketByTitle, token: str = Depends(validate_authorization)) ->  schemas.TicketSimpleResponse:
	try:
		tickets = commands.command_get_ticket_by_title(
			ticket = ticket
		)
	except ValueError as e:
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_404_NOT_FOUND
		)

	response = {
		"tickets": tickets
	}
	return response


@router.put(
	"/{id}",
	status_code = status.HTTP_200_OK,
	response_model = schemas.TicketSimpleResponse
)
def update_ticket(id: int, ticket: schemas.TicketUpdate, token: str = Depends(validate_authorization)) -> schemas.TicketSimpleResponse:
	try:
		ticket_update = ticket.model_dump(exclude_defaults = True)

		ticket = commands.command_update_ticket(
			ticket_id = id,
			infoUpdate = ticket
		)
		
		commands.command_add_history_ticket(
			ticket_id = id, 
			state = StateTicketHistory.actualizar.name,
			infoTicket = ticket_update
		)

	except ValueError as e:
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_404_NOT_FOUND
		)

	return ticket


@router.delete(
	"/{id}",
	status_code = status.HTTP_204_NO_CONTENT,
)
def delete_ticket(id: int, token: str = Depends(validate_authorization)) -> None:
	try:
		commands.command_delete_ticket(
			ticket_id = id
		)
	except ValueError as e:
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_404_NOT_FOUND
		)

@router.get(
	"/list/project/",
	status_code = status.HTTP_200_OK,
	response_model = schemas.TicketsByProjectResponse
)
def get_tickets_by_project(request: Request, query: Annotated[schemas.TicketPagination, Query()], token: str = Depends(validate_authorization)) -> schemas.TicketsByProjectResponse:

	try:
		project = c_projects.command_get_project(
			project_id = query.project_id
		)
		
		total_tickets = commands.command_get_total_tickets_project(
			project_id = query.project_id,
		)
		
		tickets = commands.command_get_tickets_by_project(
			project_id = query.project_id,
			page = query.page,
			pageSize = query.pageSize,
		)
	except ValueError as e:
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_404_NOT_FOUND
		)


	pagination = pg.set_url_pagination(
		request = request,
		elements = tickets,
		total_elements = total_tickets,
		page = query.page,
		pageSize = query.pageSize,
		params = {
			"project_id": query.project_id
		}
	)

	response = {
		"previous": pagination.get("previous"),
		"current": query.page,
		"next": pagination.get("next"),
		"project": project,
		"content": {
			"total": total_tickets,
			"tickets": tickets
		}
	}

	return response


@router.get(
	"/{id}/history",
	status_code = status.HTTP_200_OK,
	response_model = schemas.TicketsHistoryByTicketResponse
)

def get_ticket_history_by_ticket(request: Request, id: int, query: Annotated[pg.ListPagination, Query()]) -> schemas.TicketsHistoryByTicketResponse:
	try:
		ticket = commands.command_get_ticket(
			ticket_id = id
		)

		total_tickets_history = commands.command_get_total_tickets_history(
			ticket_id = id
		)

		histories = commands.command_get_tickets_history(
			ticket_id = id,
			page = query.page,
			pageSize = query.pageSize,
		)
	except ValueError as e:
		return JSONResponse(
			content = {"message": str(e)},
			status_code = status.HTTP_404_NOT_FOUND
		)


	pagination = pg.set_url_pagination(
		request = request,
		elements = histories,
		total_elements = total_tickets_history,
		page = query.page,
		pageSize = query.pageSize
	)


	response = {
		"previous": pagination.get('previous'),
		"current": query.page,
		"next": pagination.get('next'),
		"ticket": ticket,
		"content": {
			"total": total_tickets_history,
			"histories": histories
		}
	}


	return response
	