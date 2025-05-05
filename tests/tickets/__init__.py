from typing import Literal

from sqlalchemy import insert
from sqlalchemy import update


from pydantic import BaseModel

from apps.projects.models import Project

from apps.tickets.models import Ticket
from apps.tickets.models import ChoicesType
from apps.tickets.models import ChoicesState
from apps.tickets.models import ChoicesPrority
from apps.tickets.models import TicketHistory
from apps.tickets.models import StateTicketHistory
from apps.tickets.schemas import schemas
from apps.tickets.commands.utils.utils import set_message_ticket_history


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


class CreateTicket(BaseModel):
	title: str
	priority: Literal["baja", "normal", "alta", "inmediata"] = "normal"
	state: Literal["nuevo", "desarrollo", "prueba", "repaso", "terminado"] = "nuevo"
	type: Literal["abierto", "archivado", "cerrado"] = "abierto"
	description: str | None = None
	project_id: int = 1


def bulk_insert_ticket(db):
	db.execute(
	    insert(Ticket),
	    [
	        CreateTicket(
	        	title = "Interfaz Grafica"
	        ).model_dump(),
	        CreateTicket(
	        	title = "Formularios"
	        ).model_dump(),
	        CreateTicket(
	        	title = "Confirmación",
	        	priority = "inmediata"
	        ).model_dump(),
	        CreateTicket(
	        	title = "Tests",
	        	priority = "inmediata"
	        ).model_dump(),
	        CreateTicket(
	        	title = "Endpoints",
	        	priority = "alta",
	        	state = "desarrollo"
	        ).model_dump(),
	        CreateTicket(
	        	title = "Limites de petición",
	        	priority = "alta",
	        	state = "desarrollo"
	        ).model_dump(),
	        CreateTicket(
	        	title = "Refactoring",
	        	state = "repaso"
	        ).model_dump(),
	        CreateTicket(
	        	title = "Validaciones de Login",
	        	priority = "alta",
	        	state = "repaso"
	        ).model_dump(),
	        CreateTicket(
	        	title = "Consultas SQL",
	        	state = "repaso"
	        ).model_dump(),
	        CreateTicket(
	        	title = "Rendimiento de la API",
	        	priority = "baja",
	        	state = "repaso"
	        ).model_dump(),
	        CreateTicket(
	        	title = "Tabla Ticket",
	        	priority = "baja",
	        	type = "archivado"
	        ).model_dump(),
	        CreateTicket(
	        	title = "Algoritmo de busqueda",
	        	priority = "baja",
	        	type = "archivado"
	        ).model_dump(),
	        CreateTicket(
	        	title = "Sistema de caching",
	        	type = "cerrado"
	        ).model_dump()
	    ]
	)

	db.commit()


def bulk_insert_ticket_multiple_projects(db):
	db.execute(
		insert(Ticket),
		[
			CreateTicket(
	        	title = "Interfaz Grafica",
	        	project_id = 2
	        ).model_dump(),
	        CreateTicket(
	        	title = "Formularios",
	        	project_id = 2
	        ).model_dump(),
	        CreateTicket(
	        	title = "Confirmación",
	        	priority = "inmediata"
	        ).model_dump(),
	        CreateTicket(
	        	title = "Tests de la API",
	        	project_id = 2,
	        	priority = "inmediata"
	        ).model_dump(),
	        CreateTicket(
	        	title = "API de los Endpoints",
	        	priority = "alta",
	        	state = "desarrollo",
	        	project_id = 2,
	        ).model_dump(),
	        CreateTicket(
	        	title = "Limites de petición",
	        	priority = "alta",
	        	state = "desarrollo"
	        ).model_dump(),
		]
	)

	db.commit()


def insert_projects(db):
	db.execute(
		insert(Project),
		[
			{
				"title" : "Frontend (Bug tracker)",
				"description" : "Frontend del proyecto",
				"user_id" : 1
			},
			{
				"title" : "Diseño UI (Bug tracker)",
				"description" : "el diseño UI para el proyecto",
				"user_id" : 1
			},
			{
				"title" : "Diagrama de la DB (Bug tracker)",
				"description" : "Diagrama de la DB para el proyecto",
				"user_id" : 1
			},
			{
				"title" : "Documentación (Bug tracker)",
				"description" : "Crear la documentación para el proyecto",
				"user_id" : 1
			},

		]
	)

	db.commit()


def insert_ticket_by_project(db):
	
	db.execute(
		insert(Ticket),
		[
			set_ticket_schema(
				project_id = 1, 
				title = "Tests para la DB", 
			).model_dump(),
			set_ticket_schema(
				project_id = 2, 
				title = "Función para consumir API", 
			).model_dump(),
			set_ticket_schema(
				project_id = 2, 
				title = "Validación de formularios", 
			).model_dump(),
			set_ticket_schema(
				project_id = 2, 
				title = "Vistas", 
			).model_dump(),
			set_ticket_schema(
				project_id = 3, 
				title = "Apariencia de formularios", 
			).model_dump(),
			set_ticket_schema(
				project_id = 3, 
				title = "Colores de las páginas", 
			).model_dump(),
			set_ticket_schema(
				project_id = 4, 
				title = "Relaciones de tablas", 
			).model_dump(),
			set_ticket_schema(
				project_id = 5, 
				title = "Documentar progreso", 
			).model_dump(),
		]
	)

	db.commit()


def create_ticket_histories(db, ticket_id: int = 1):
	db.execute(
		insert(TicketHistory),
		[
			{
				"ticket_id": ticket_id,
				"state": StateTicketHistory.crear.name,
				"message": set_message_ticket_history(
					ticket_id = ticket_id, 
					state = StateTicketHistory.crear.name, 
				)
			},
			{
				"ticket_id": ticket_id,
				"state": StateTicketHistory.actualizar.name,
				"message": set_message_ticket_history(
					ticket_id = ticket_id, 
					state = StateTicketHistory.actualizar.name,
					data = {"state": "desarrollo", "priority": "alta"}
				)
			},
			{
				"ticket_id": ticket_id,
				"state": StateTicketHistory.actualizar.name,
				"message": set_message_ticket_history(
					ticket_id = ticket_id, 
					state = StateTicketHistory.actualizar.name,
					data = {"state": "prueba"}
				)
			},
			{
				"ticket_id": ticket_id,
				"state": StateTicketHistory.actualizar.name,
				"message": set_message_ticket_history(
					ticket_id = ticket_id, 
					state = StateTicketHistory.actualizar.name,
					data = {"title": "Formato del CSS"}
				)
			},
		]
	)

	db.commit()