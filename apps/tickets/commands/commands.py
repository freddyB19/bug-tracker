from typing import List
from typing import Dict
from typing import Optional

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.orm import joinedload

from pydantic import validate_call

from apps import get_db
from .utils import utils
from .utils.error_messages import (
	InvalidPriority,
	InvalidState,
	InvalidType,
	DoesNotExistsTicket,
	PaginationError,
	DoesNotExistsTicketHistory,
	EmptyValues,
)
from apps.tickets.models import Ticket
from apps.tickets.models import TicketHistory
from apps.tickets.models import ChoicesType
from apps.tickets.models import ChoicesState
from apps.tickets.models import ChoicesPrority
from apps.tickets.models import StateTicketHistory 

from apps.tickets.schemas import schemas
from apps.projects.models.model import Project
from apps.projects.commands.utils.error_messages import DoesNotExistsProject

from apps.utils.pagination.pagination import calculate_start_pagination
from apps.utils.pagination.pagination import PageDefault
from apps.utils.pagination.pagination import PageSizeDefault

@validate_call
def command_add_ticket_history(ticket_id: int, state: str = StateTicketHistory.crear.name, infoTicket: Dict[str, str | int ] = None) -> TicketHistory:
	db = next(get_db())

	if db.query(Ticket).filter(Ticket.id == ticket_id).one_or_none() is None:
		raise ValueError(DoesNotExistsTicket.get(id = ticket_id), 404)

	if not utils.validate_choice(choice = state, options = StateTicketHistory):
		raise ValueError(DoesNotExistsTicketHistory.get(state = state), 400)

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
		raise ValueError(DoesNotExistsProject.get(id = ticket.project_id), 404)

	if not utils.validate_choice(choice = ticket.priority, options = ChoicesPrority):
		raise ValueError(InvalidPriority.get(), 400)


	new_ticket = Ticket(
		title = ticket.title,
		description = ticket.description,
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

	if db.query(Ticket).filter(Ticket.id == ticket_id).one_or_none() is None:
		raise ValueError(DoesNotExistsTicket.get(id = ticket_id), 404)

	sql = (
		select(Ticket)
		.options(joinedload(Ticket.project))
		.where(Ticket.id == ticket_id)
	)


	ticket = db.scalar(sql)

	return ticket

@validate_call
def command_get_total_tickets_filter(project_id: int, search: Dict[str, str] = {}) -> int:
	db = next(get_db())

	if "type" in search and not utils.validate_choice(choice = search["type"], options = ChoicesType):
		raise ValueError(InvalidType.get(), 400)
	if "state" in search and not utils.validate_choice(choice = search["state"], options = ChoicesState):
		raise ValueError(InvalidState.get(), 400)
	if "priority" in search and not utils.validate_choice(choice = search["priority"], options = ChoicesPrority):
		raise ValueError(InvalidPriority.get(), 400)

	data_search = search.copy()

	data_search.update({
		"project_id": project_id
	})
	
	total = db.query(Ticket).filter_by(
		**data_search
	).count()

	return total

@validate_call
def command_get_ticket_by_filter(project_id: int, search: Dict[str, str] = {}, page: int = PageDefault, pageSize: int = PageSizeDefault) -> Optional[List[Ticket]]:
	db = next(get_db())

	if "type" in search and not utils.validate_choice(choice = search["type"], options = ChoicesType):
		raise ValueError(InvalidType.get(), 400)
	if "state" in search and not utils.validate_choice(choice = search["state"], options = ChoicesState):
		raise ValueError(InvalidState.get(), 400)
	if "priority" in search and not utils.validate_choice(choice = search["priority"], options = ChoicesPrority):
		raise ValueError(InvalidPriority.get(), 400)

	if page < 0 or pageSize < 0:
		raise ValueError(PaginationError.get(), 400)

	data_search = search.copy()

	start = calculate_start_pagination(page = page, pageSize = pageSize)

	data_search.update({
		"project_id": project_id
	})

	tickets = db.query(Ticket).filter_by(
		**data_search
	).offset(start).limit(pageSize)

	return tickets.all()

@validate_call
def command_get_ticket_by_title(project_id: int, ticket: schemas.TicketByTitle) -> Optional[List[Ticket]]:
	db = next(get_db())

	sql = (
		select(Ticket)
		.where(Ticket.project_id == project_id)
		.where(
			Ticket.title.ilike(f"%{ticket.title}%")
		)
	)

	tickets = db.scalars(sql).all()

	return tickets

@validate_call
def command_update_ticket(ticket_id: int, infoUpdate: schemas.TicketUpdate) -> Ticket:
	db = next(get_db())

	if db.query(Ticket).filter(Ticket.id == ticket_id).one_or_none() is None:
		raise ValueError(DoesNotExistsTicket.get(id = ticket_id), 404)

	if infoUpdate.type is not None and not utils.validate_choice(choice = infoUpdate.type, options = ChoicesType):
		raise ValueError(InvalidType.get(), 400)
	if infoUpdate.state is not None and not utils.validate_choice(choice = infoUpdate.state, options = ChoicesState):
		raise ValueError(InvalidState.get(), 400)
	if infoUpdate.priority is not None and not utils.validate_choice(choice = infoUpdate.priority, options = ChoicesPrority):
		raise ValueError(InvalidPriority.get(), 400)

	update_values = infoUpdate.model_dump(exclude_defaults = True)

	if not update_values:
		raise ValueError(EmptyValues.get(), 400)

	sql = (
		update(Ticket)
		.where(Ticket.id == ticket_id)
		.values(**update_values)
		.returning(Ticket)
	)

	ticket = db.scalar(sql)
	
	db.close()
	return ticket

@validate_call
def command_delete_ticket(ticket_id: int) -> None:
	db = next(get_db())

	ticket = db.get(Ticket, ticket_id)

	if ticket is None:
		raise ValueError(DoesNotExistsTicket.get(id = ticket_id), 404)

	db.delete(ticket)
	db.commit()

@validate_call
def command_get_tickets_by_project(project_id: int, page: int = PageDefault, pageSize: int = PageSizeDefault) -> Optional[List[Ticket]]:
	db = next(get_db())

	if page < 0 or pageSize < 0:
		raise ValueError(PaginationError.get(), 400)

	start = calculate_start_pagination(page = page, pageSize = pageSize)

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

@validate_call
def command_get_total_ticket_histories(ticket_id: int) -> int:
	db = next(get_db())

	sql = (
		select(func.count())
		.select_from(TicketHistory)
		.where(TicketHistory.ticket_id == ticket_id)
	)

	total = db.scalar(sql)

	return total

@validate_call
def command_get_ticket_histories(ticket_id: int, page: int = PageDefault, pageSize: int = PageSizeDefault) -> Optional[TicketHistory]:
	db = next(get_db())

	if page < 0 or pageSize < 0:
		raise ValueError(PaginationError.get(), 400)

	start = calculate_start_pagination(page = page, pageSize = pageSize)

	sql = (
		select(TicketHistory)
		.where(TicketHistory.ticket_id == ticket_id)
		.offset(start)
		.limit(pageSize)
	)

	histories = db.scalars(sql).all()

	return histories


@validate_call
def command_get_detail_ticket_history(history_id: int) -> TicketHistory:
	db = next(get_db())

	if db.query(TicketHistory).filter(TicketHistory.id == history_id).one_or_none() is None:
		raise ValueError(DoesNotExistsTicketHistory.get(id = history_id), 404)

	sql = (
		select(TicketHistory)
		.options(joinedload(TicketHistory.ticket))
		.where(TicketHistory.id == history_id)
	)

	history = db.scalar(sql)

	return history