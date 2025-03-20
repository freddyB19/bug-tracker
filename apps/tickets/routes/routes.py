from typing import Optional
from typing_extensions import Annotated

from fastapi import status
from fastapi import APIRouter
from fastapi import Query
from fastapi import Depends
from fastapi.responses import JSONResponse

from apps.tickets.schemas import schemas
from apps.tickets.commands import commands
from apps.utils.token.token import validate_authorization


router = APIRouter(prefix = "/ticket")

@router.post(
	"/",
	status_code = status.HTTP_201_CREATED,
	response_model = schemas.TicketResponse
)
def create_ticket(ticket: schemas.TicketRequest, token: str = Depends(validate_authorization)) -> schemas.TicketResponse:
	try:
		new_ticket = commands.command_create_ticket(
			ticket = ticket
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
	"/search/",
	status_code = status.HTTP_200_OK,
	response_model = schemas.ListTicketsResponse
)
def get_ticket_by_filter(ticket_filter: Annotated[schemas.TicketFilter, Query()], token: str = Depends(validate_authorization)) -> schemas.ListTicketsResponse:
	try:
		tickets = commands.command_get_ticket_by_filter(
			ticket = ticket_filter
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


@router.get(
	"/search/title",
	status_code = status.HTTP_200_OK,
	response_model = schemas.ListTicketsResponse
)
def get_ticket_by_title(ticket: schemas.TicketByTitle, token: str = Depends(validate_authorization)) ->  schemas.ListTicketsResponse:
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
		ticket = commands.command_update_ticket(
			ticket_id = id,
			infoUpdate = ticket
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