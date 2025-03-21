from typing import List
from typing import Dict
from typing import Literal
from typing import Optional

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import update

from pydantic import validate_call

from apps import get_db
from .utils import utils
from apps.tickets.models import Ticket
from apps.tickets.models import TicketHistory
from apps.tickets.models import ChoicesType
from apps.tickets.models import ChoicesState
from apps.tickets.models import ChoicesPrority
from apps.tickets.models import StateTicketHistory 

from apps.tickets.schemas import schemas
from apps.projects.models.model import Project


@validate_call
def command_add_history_ticket(ticket_id: int, state: str, infoTicket: Dict[str, str | int ] = None) -> TicketHistory:
	db = next(get_db())

	if not utils.validate_choice(choice = state, options = StateTicketHistory):
		raise ValueError(f"TicketHistory: 'state' invalido = {state}")

	new_history = TicketHistory(
		ticket_id = ticket_id,
		state = state,
		message = utils.set_message_ticket_history(
			ticket_id = ticket_id, 
			state = state, 
			data = infoTicket
		)
	)

	db.add(new_history)
	db.commit()
	db.refresh(new_history)

	return new_history


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

@validate_call
def command_get_ticket_by_filter(project_id: int, ticket: schemas.TicketFilter) -> Optional[List[Ticket]]:
	db = next(get_db())

	data_search = ticket.model_dump(exclude_defaults = True)
	data_search.update({
		"project_id": project_id
	})

	if not data_search:
		raise ValueError("Debe incluir parametros de busqueda.")

	tickets = db.query(Ticket).filter_by(
		**data_search
	)

	return tickets

@validate_call
def command_get_ticket_by_title(ticket: schemas.TicketByTitle) -> Optional[List[Ticket]]:
	db = next(get_db())

	sql = (
		select(Ticket)
		.where(
			Ticket.title.ilike(f"%{ticket.title}%")
		)
	)

	tickets = db.scalars(sql).all()

	return tickets

@validate_call
def command_update_ticket(ticket_id: int, infoUpdate: schemas.TicketUpdate) -> Ticket:
	db = next(get_db())

	if infoUpdate.type is not None and not utils.validate_choice(choice = infoUpdate.type, options = ChoicesType):
		raise ValueError("El tipo elegido es el incorrecto")
	if infoUpdate.state is not None and not utils.validate_choice(choice = infoUpdate.state, options = ChoicesState):
		raise ValueError("El estado elegido es el incorrecto")
	if infoUpdate.priority is not None and not utils.validate_choice(choice = infoUpdate.priority, options = ChoicesPrority):
		raise ValueError("La prioridad elegida es la incorrecta")

	update_values = infoUpdate.model_dump(exclude_defaults = True)

	sql = (
		update(Ticket)
		.where(Ticket.id == ticket_id)
		.values(**update_values)
		.returning(Ticket)
	)

	ticket = db.execute(sql).scalar_one_or_none()
	db.close()
	
	if ticket is None:
		raise ValueError("No existe información sobre este ticket")

	return ticket

@validate_call
def command_delete_ticket(ticket_id: int) -> None:
	db = next(get_db())

	ticket = db.get(Ticket, ticket_id)

	if ticket is None:
		raise ValueError("No existe información sobre este ticket")

	db.delete(ticket)
	db.commit()

@validate_call
def command_get_tickets_by_project(project_id: int, page: int, pageSize: int) -> List[Ticket]:
	db = next(get_db())

	start = page * pageSize

	sql = (
		select(Ticket)
		.where(Ticket.project_id == project_id)
		.offset(start)
		.limit(pageSize)
	)

	tickets = db.scalars(sql).all()

	return tickets

@validate_call
def command_get_total_tickets_project(project_id: int) -> int:
	db = next(get_db())
	
	sql = (
		select(func.count())
		.select_from(Ticket)
		.where(Ticket.project_id == project_id)
	)
	
	total = db.scalar(sql)
	
	return total
