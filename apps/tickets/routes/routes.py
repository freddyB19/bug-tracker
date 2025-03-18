from fastapi import status
from fastapi import APIRouter
from fastapi.responses import JSONResponse


from apps.tickets.schemas import schemas
from apps.tickets.commands import commands

router = APIRouter(prefix = "/ticket")

@router.post(
	"/",
	status_code = status.HTTP_201_CREATED,
	response_model = schemas.TicketResponse
)
def create_ticket(ticket: schemas.TicketRequest) -> schemas.TicketResponse:
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

