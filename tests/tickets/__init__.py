from apps.tickets.models import Ticket
from apps.tickets.models import ChoicesType
from apps.tickets.models import ChoicesState
from apps.tickets.models import ChoicesPrority

from apps.tickets.schemas import schemas

TYPE = [choice.name for choice in ChoicesType]
STATE = [choice.name for choice in ChoicesState]
PRIORYTY = [choice.name for choice in ChoicesPrority]


def set_ticket(title:str = None, description:str = None, priority:str = None, state:str = None, type:str = None, project_id: int = None):
	set_title = title if title else "Tarea 1"
	set_description = description if description else "Descripción de tarea 1"
	set_type = type if type in TYPE else ChoicesType.abierto.name
	set_state = state if state in STATE else ChoicesState.nuevo.name
	set_priority = priority if priority in PRIORYTY else ChoicesPrority.baja.name
	set_project_id = project_id if project_id else 1

	return Ticket(
		title = set_title,
		description = set_description,
		type =  set_type,
		state = set_state,
		priority = set_priority,
		project_id = set_project_id
	)


def set_ticket_schema(title:str = None, description:str = None, priority:str = None, state:str = None, type:str = None, project_id: int = None):
	set_title = title if title else "Tarea 1"
	set_description = description if description else "Descripción de tarea 1"
	set_priority = priority if priority in PRIORYTY else ChoicesPrority.baja.name
	set_project_id = project_id if project_id else 1

	return schemas.TicketRequest(
		title = set_title,
		description = set_description,
		priority = set_priority,
		project_id = set_project_id
	)
