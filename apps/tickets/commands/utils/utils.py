from enum import Enum
from typing import Any
from typing import Dict
from typing_extensions import Annotated

from pydantic import validate_call

from apps.tickets.models import StateTicketHistory 

@validate_call
def validate_choice(choice: str, options: Annotated[Any, Enum]) -> bool:
	str_choices = [option.name for option in options]

	if choice not in str_choices:
		return False

	return True

@validate_call
def message_create(ticket_id: int) -> str:
	return f"Se ha creado un nuevo ticket con ID: {ticket_id}"

@validate_call
def message_update(ticket_id: int, data: Dict[str, str | int ] | None = None) -> str:
	if data is None:
		return ""

	update_fields = ""

	for field,value in data.items():
		update_fields += f" {field}='{value}' "

	return f"Se han actualizado los campos: [{update_fields}] del ticket con ID {ticket_id}"

@validate_call
def set_message_ticket_history(ticket_id: int, state: str, data: Dict[str, str | int ] | None = None) -> str:
	
	if not validate_choice(choice = state, options = StateTicketHistory):
		raise ValueError(f"TicketHistory: 'state' invalido = {state}")
	
	set_message_history = {
		'crear': message_create(ticket_id = ticket_id),
		'actualizar': message_update(ticket_id = ticket_id, data = data),
	}

	return set_message_history[state]