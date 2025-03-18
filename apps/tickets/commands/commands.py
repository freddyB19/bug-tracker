from sqlalchemy import select

from pydantic import validate_call

from apps import get_db
from .utils import utils
from apps.tickets.models import Ticket
from apps.tickets.models import ChoicesType
from apps.tickets.models import ChoicesState
from apps.tickets.models import ChoicesPrority

from apps.tickets.schemas import schemas
from apps.projects.models.model import Project


@validate_call
def command_create_ticket(ticket: schemas.TicketRequest) -> Ticket:
	db = next(get_db())

	project = db.get(Project, ticket.project_id)

	if project is None:
		raise ValueError("No existe información sobre este proyecto")


	if not utils.validate_choice(choice = ticket.type, options = ChoicesType):
		raise ValueError("El tipo elegido es el incorrecto")
	if not utils.validate_choice(choice = ticket.state, options = ChoicesState):
		raise ValueError("El estado elegido es el incorrecto")
	if not utils.validate_choice(choice = ticket.priority, options = ChoicesPrority):
		raise ValueError("La prioridad elegida es la incorrecta")


	new_ticket = Ticket(
		title = ticket.title,
		description = ticket.description,
		type = ticket.type,
		state = ticket.state,
		priority = ticket.priority,
		project_id = ticket.project_id,
	)

	db.add(new_ticket)
	db.commit()
	db.refresh(new_ticket)

	return new_ticket


@validate_call
def command_get_ticket(ticket_id: int) -> Ticket:
	db = next(get_db())

	ticket = db.get(Ticket, ticket_id)

	if ticket is None:
		raise ValueError("No existe información sobre este ticket")

	return ticket
