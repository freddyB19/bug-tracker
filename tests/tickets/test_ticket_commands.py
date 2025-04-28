import pytest
from typing import Literal
from unittest.mock import patch

from sqlalchemy import insert

from pydantic import ValidationError
from pydantic import BaseModel

from tests import ENGINE
from tests import SESSION
from tests import get_db
from tests.tickets import set_ticket
from tests.tickets import set_ticket_schema

from apps import Model
from apps.users.models import User
from apps.projects.models import Project
from apps.tickets.models import Ticket
from apps.tickets.models import Ticket
from apps.tickets.models import ChoicesPrority
from apps.tickets.models import ChoicesState
from apps.tickets.models import ChoicesType
from apps.tickets.schemas import schemas
from apps.tickets.commands import commands


class TestTicketSchema(BaseModel):
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
	        TestTicketSchema(
	        	title = "Interfaz Grafica"
	        ).model_dump(),
	        TestTicketSchema(
	        	title = "Formularios"
	        ).model_dump(),
	        TestTicketSchema(
	        	title = "Confirmación",
	        	priority = "inmediata"
	        ).model_dump(),
	        TestTicketSchema(
	        	title = "Tests",
	        	priority = "inmediata"
	        ).model_dump(),
	        TestTicketSchema(
	        	title = "Endpoints",
	        	priority = "alta",
	        	state = "desarrollo"
	        ).model_dump(),
	        TestTicketSchema(
	        	title = "Limites de petición",
	        	priority = "alta",
	        	state = "desarrollo"
	        ).model_dump(),
	        TestTicketSchema(
	        	title = "Refactoring",
	        	state = "repaso"
	        ).model_dump(),
	        TestTicketSchema(
	        	title = "Validaciones de Login",
	        	priority = "alta",
	        	state = "repaso"
	        ).model_dump(),
	        TestTicketSchema(
	        	title = "Consultas SQL",
	        	state = "repaso"
	        ).model_dump(),
	        TestTicketSchema(
	        	title = "Rendimiento de la API",
	        	priority = "baja",
	        	state = "repaso"
	        ).model_dump(),
	        TestTicketSchema(
	        	title = "Tabla Ticket",
	        	priority = "baja",
	        	type = "archivado"
	        ).model_dump(),
	        TestTicketSchema(
	        	title = "Algoritmo de busqueda",
	        	priority = "baja",
	        	type = "archivado"
	        ).model_dump(),
	        TestTicketSchema(
	        	title = "Sistema de caching",
	        	type = "cerrado"
	        ).model_dump()
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



class TestTicketCommand:

	def setup_method(self):
		Model.metadata.drop_all(ENGINE)
		Model.metadata.create_all(ENGINE)

		self.db = SESSION

		user = User(
			name = 'bolivar',
			email = 'bolivar@gmail.com',
			username = 'bolivar19',
			password = '12345'
		)

		self.db.add(user)
		self.db.commit()
		self.db.refresh(user)

		project = Project(
			title = "Proyecto de tests",
			description = "Proyecto para hacer tests",
			user_id = user.id
		)
		
		self.db.add(project)
		self.db.commit()
		self.db.refresh(project)

		ticket = set_ticket(project_id = project.id)
		
		self.db.add(ticket)
		self.db.commit()
		self.db.refresh(ticket)

		self.user = user
		self.project = project
		self.ticket = ticket

	def teardown_method(self):
		self.db.rollback()
		self.db.close()


	def test_save_data_db(self):
		"""
			Validar que se han guardo los datos
		"""
		tickets = self.db.query(Ticket).all()

		assert tickets
		assert len(tickets) == 1

		ticket = self.db.get(Ticket, 1)

		assert ticket.id == self.ticket.id
		assert ticket.title == self.ticket.title
		assert ticket.priority.name == self.ticket.priority.name
		assert ticket.state.name == self.ticket.state.name
		assert ticket.type.name == self.ticket.type.name
		assert ticket.project_id == self.ticket.project_id

	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket(self):
		"""
			Validar que se ha creado un ticket
		"""

		schema_ticket = set_ticket_schema(project_id = self.project.id)

		ticket = commands.command_create_ticket(ticket = schema_ticket)

		assert ticket
		assert ticket.id == 2
		assert ticket.title == schema_ticket.title
		assert ticket.description == schema_ticket.description
		assert ticket.priority.name == schema_ticket.priority
		assert ticket.state.name == ChoicesState.nuevo.name
		assert ticket.type.name == ChoicesType.abierto.name
		assert ticket.project_id == schema_ticket.project_id


	@pytest.mark.xfail(reason = "Titulo muy largo", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_with_too_long_title(self):
		"""
			Validar la longitud del titulo cuando es muy largo
		"""
		title = """
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		"""
		
		ticket = commands.command_create_ticket(ticket = {
			"title": title,
			"project_id": self.project.id,
			"description": "Descripción de la tarea",
			"priority": "alta"

		})


	@pytest.mark.xfail(reason = "Titulo muy corto", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_with_too_short_title(self):
		"""
			Validar la longitud del titulo cuando es muy corto
		"""
		title = "App"
		
		ticket = commands.command_create_ticket(ticket = {
			"title": title,
			"project_id": self.project.id,
			"description": "Descripción de la tarea",
			"priority": "alta"

		})


	@pytest.mark.xfail(reason = "Sin titulo", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_without_title(self):
		"""
			Validar que no se cree un ticket sin 'titulo' 
		"""
		ticket = commands.command_create_ticket(ticket = {
			"project_id": self.project.id,
			"description": "Descripción de la tarea",
			"priority": "alta"

		})

	@pytest.mark.xfail(reason = "'Descripción' muy larga", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_with_too_long_description(self):
		"""
			Validar la longitud de la descripción cuando es muy larga 
		"""

		description = """
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		"""

		ticket = commands.command_create_ticket(ticket = {
			"title": "Tarea a",
			"project_id": self.project.id,
			"description": description,
			"priority": "alta"

		})


	@pytest.mark.xfail(reason = "Descripción muy corta", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_with_too_short_description(self):
		"""
			Validar la longitud de la descripción cuando es muy corta
		"""

		description = "App"

		ticket = commands.command_create_ticket(ticket = {
			"title": "Tarea a",
			"project_id": self.project.id,
			"description": description,
			"priority": "alta"

		})


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_with_without_description(self):
		"""
			Validar que se cree un ticket sin 'descripción' 
		"""

		ticket = commands.command_create_ticket(ticket = {
			"title": "Tarea a",
			"project_id": self.project.id,
			"priority": "alta"

		})

		assert ticket.id == 2
		assert ticket.title == "Tarea a"
		assert ticket.project_id == self.project.id


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_with_param_state(self):
		"""
			Validar que se cree un ticket
			ignorando el valor para el 'state'
			si se envia.
		"""
		ticket = commands.command_create_ticket(ticket = {
			"title": "Tarea a",
			"description": "Descripción de la tarea a",
			"project_id": self.project.id,
			"priority": "alta",
			"state": "prueba",

		})

		assert ticket.id == 2
		assert ticket.state.name !=  "prueba"
		assert ticket.state.name ==  "nuevo"


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_with_param_type(self):
		"""
			Validar que se cree un ticket
			ignorando el valor para el 'type'
			si se envia.
		"""

		ticket = commands.command_create_ticket(ticket = {
			"title": "Tarea a",
			"description": "Descripción de la tarea a",
			"project_id": self.project.id,
			"priority": "alta",
			"type": "archivado",

		})

		assert ticket.id == 2
		assert ticket.type.name !=  "archivado"
		assert ticket.type.name == "abierto"


	@pytest.mark.xfail(reason="Incorrecto 'priority'", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_with_wrong_priority(self):
		"""
			Validar que no se cree un ticket
			enviando un valor incorrecto para el 'priority'
		"""

		ticket = commands.command_create_ticket(ticket = {
			"title": "Tarea a",
			"description": "Descripción de la tarea a",
			"project_id": self.project.id,
			"priority": "ahora",
		})

	@pytest.mark.xfail(reason="No existe este proyecto", raises = ValueError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_with_no_existent_project(self):
		"""
			Validar que no se cree un ticket
			con el ID de un proyecto que no existe
		"""	

		schema_ticket = set_ticket_schema(project_id = 100)

		ticket = commands.command_create_ticket(ticket = schema_ticket)

	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_ticket_by_id(self):
		"""
			Validar obtener un ticket por ID
		"""

		ticket = commands.command_get_ticket(ticket_id = 1)

		assert ticket.id == 1
		assert ticket.title == self.ticket.title
		assert ticket.description == self.ticket.description
		assert ticket.priority.name == self.ticket.priority.name
		assert ticket.state.name == self.ticket.state.name
		assert ticket.type.name == self.ticket.type.name
		assert ticket.project_id == self.ticket.project_id


	@pytest.mark.xfail(reason = "No existe este ticket", raises = ValueError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_no_existent_ticket(self):
		"""
			Validar que se genere un error
			al intentar acceder a un ticket que no existe
		"""
		ticket_id = 100
		
		ticket = commands.command_get_ticket(ticket_id = ticket_id)

		assert ticket.id == ticket_id


	@pytest.mark.xfail(reason = "Sin ticket_id", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_ticket_without_ticket_id(self):
		"""
			Validar que se genere un error 
			al no enviar un valor para ticket_id
		"""

		ticket = commands.command_get_ticket()

		assert ticket.id == 2

	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_update_ticket(self):
		"""
			Validar actualización de un ticket
		"""

		ticket_id = self.ticket.id

		infoUpdate = schemas.TicketUpdate(
			title = "Update Tarea A",
			description = "Update descripción de tarea A",
			type = "archivado",
			state = "desarrollo",
			priority = "inmediata"
		)

		ticket = commands.command_update_ticket(
			ticket_id = ticket_id,
			infoUpdate = infoUpdate
		)

		assert ticket.id == self.ticket.id
		assert ticket.title == infoUpdate.title
		assert ticket.description == infoUpdate.description
		assert ticket.type.name == infoUpdate.type
		assert ticket.state.name == infoUpdate.state
		assert ticket.priority.name == infoUpdate.priority


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_update_ticket_only_title(self):
		"""
			Validar que solo se actualice el titulo
		"""
		ticket_id = self.ticket.id

		infoUpdate = schemas.TicketUpdate(
			title = "Update Tarea A"
		)

		ticket = commands.command_update_ticket(
			ticket_id = ticket_id,
			infoUpdate = infoUpdate
		)

		assert ticket.id == self.ticket.id
		assert ticket.title == infoUpdate.title
		assert ticket.title != self.ticket.title


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_update_ticket_only_description(self):
		"""
			Validar que solo se actualice la descripción
		"""
		ticket_id = self.ticket.id

		infoUpdate = schemas.TicketUpdate(
			description = "Update descripción de tarea A"
		)

		ticket = commands.command_update_ticket(
			ticket_id = ticket_id,
			infoUpdate = infoUpdate
		)

		assert ticket.id == self.ticket.id
		assert ticket.description == infoUpdate.description
		assert ticket.description != self.ticket.description


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_update_ticket_only_type(self):
		"""
			Validar que solo se actualice el tipo 
		"""
		ticket_id = self.ticket.id

		infoUpdate = schemas.TicketUpdate(
			type = "archivado"
		)

		ticket = commands.command_update_ticket(
			ticket_id = ticket_id,
			infoUpdate = infoUpdate
		)

		assert ticket.id == self.ticket.id
		assert ticket.type.name == infoUpdate.type
		assert ticket.type.name != self.ticket.type.name


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_update_ticket_only_state(self):
		"""
			Validar que solo se actualice el estado
		"""
		ticket_id = self.ticket.id

		infoUpdate = schemas.TicketUpdate(
			state = "desarrollo"
		)

		ticket = commands.command_update_ticket(
			ticket_id = ticket_id,
			infoUpdate = infoUpdate
		)

		assert ticket.id == self.ticket.id
		assert ticket.state.name == infoUpdate.state
		assert ticket.state.name != self.ticket.state.name


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_update_ticket_only_priority(self):
		"""
			Validar que solo se actualice la prioridad
		"""
		ticket_id = self.ticket.id

		infoUpdate = schemas.TicketUpdate(
			priority = "inmediata"
		)

		ticket = commands.command_update_ticket(
			ticket_id = ticket_id,
			infoUpdate = infoUpdate
		)

		assert ticket.id == self.ticket.id
		assert ticket.priority.name == infoUpdate.priority
		assert ticket.priority.name != self.ticket.priority.name

	@pytest.mark.xfail(reason = "(Update) Titulo muy largo", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_update_ticket_with_too_long_title(self):
		"""
			Validar la longitud del titulo
			para la actualización cuando es muy larga
		"""
		ticket_id = self.ticket.id
		title = """
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		"""
		
		ticket = commands.command_update_ticket(
			ticket_id = ticket_id,
			infoUpdate = {"title": title}
		)


	@pytest.mark.xfail(reason = "(Update) Titulo muy corto", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_update_ticket_with_too_short_title(self):
		"""
			Validar la longitud del titulo
			para la actualización cuando es muy corta
		"""
		ticket_id = self.ticket.id
		title = "App"

		ticket = commands.command_update_ticket(
			ticket_id = ticket_id,
			infoUpdate = {"title": title}
		)


	@pytest.mark.xfail(reason = "(Update) Descripción muy larga", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_update_ticket_with_too_long_description(self):
		"""
			Validar la longitud de la descripción
			para la actualización cuando es muy larga
		"""
		ticket_id = self.ticket.id
		description = """
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		"""

		ticket = commands.command_update_ticket(
			ticket_id = ticket_id,
			infoUpdate = {"description": description}
		)


	@pytest.mark.xfail(reason = "(Update) Descripción muy corta", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_update_ticket_with_too_short_description(self):
		"""
			Validar la longitud de la descripción
			para la actualización cuando es muy corta
		"""
		ticket_id = self.ticket.id
		description = "App"

		ticket = commands.command_update_ticket(
			ticket_id = ticket_id,
			infoUpdate = {"description": description}
		)

	@pytest.mark.xfail(reason = "(Update) Incorrecto 'state'", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_update_ticket_with_wrong_state(self):
		"""
			Validar que se genere un error
			por enviar un state incorrecto para 
			actualizar el ticket
		"""
		ticket_id = self.ticket.id
		state = "eliminado"

		ticket = commands.command_update_ticket(
			ticket_id = ticket_id,
			infoUpdate = {"state": state}
		)


	@pytest.mark.xfail(reason = "(Update) Incorrecto 'type'", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_update_ticket_with_wrong_type(self):
		"""
			Validar que se genere un error
			por enviar un type incorrecto para 
			actualizar el ticket
		"""
		ticket_id = self.ticket.id
		type = "guardado"

		ticket = commands.command_update_ticket(
			ticket_id = ticket_id,
			infoUpdate = {"type": type}
		)


	@pytest.mark.xfail(reason = "(Update) Incorrecto 'priotity'", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_update_ticket_with_wrong_priority(self):
		"""
			Validar que se genere un error
			por enviar un priotity incorrecto para 
			actualizar el ticket
		"""
		ticket_id = self.ticket.id
		priority = "ahora"

		ticket = commands.command_update_ticket(
			ticket_id = ticket_id,
			infoUpdate = {"priority": priority}
		)


	@pytest.mark.xfail(reason = "(Update) No existe este ticket", raises = ValueError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_update_with_no_existent_ticket(self):
		"""
			Validar que se genere un error
			al intentar actualizar un ticket
			que no existe
		"""
		ticket_id = 100

		infoUpdate = schemas.TicketUpdate(
			description = "Update descripción de tarea A"
		)

		ticket = commands.command_update_ticket(
			ticket_id = ticket_id,
			infoUpdate = infoUpdate
		)


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_delete_ticket(self):
		"""
			Validar que se elimine un ticket
		"""

		ticket_id = self.ticket.id

		commands.command_delete_ticket(ticket_id = ticket_id)
		
		assert self.db.get(Ticket, ticket_id) is None


	@pytest.mark.xfail(reason = "(Delete) No existe este ticket", raises = ValueError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_delete_no_existent_ticket(self):
		"""
			Validar que se genere un error
			al intentar eliminar un ticket que no existe
		"""

		ticket_id = 100

		commands.command_delete_ticket(ticket_id = ticket_id)

	@pytest.mark.xfail(reason = "(Delete) Sin ticket_id", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_delete_ticket_without_ticket_id(self):
		"""
			Validar que se genere un error
			al intentar eliminar un ticket
			sin enviar ticket_id
		"""
		commands.command_delete_ticket()


	@pytest.mark.xfail(reason = "(Delete) Valor incorrecto en ticket_id", raises = ValidationError)
	@pytest.mark.parametrize("ticket_id", [
		12.1,
		"ab12",
		(12,1),
		{"id": 1},
		[56,1,7,12]
	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_delete_ticket_with_wrong_ticket_id(self, ticket_id):
		"""
			Validar que se genere un error
			al intentar eliminar un ticket
			al enviar un valor incorrecto para ticket_id
		"""

		commands.command_delete_ticket(ticket_id = ticket_id)


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_tickets_filter(self):
		"""
			Validar obtener el total de tickets
			aplicando un filtro
		"""
		project_id = self.project.id

		bulk_insert_ticket(db = self.db)

		search = schemas.TicketFilterPagination(
			priority = "baja"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		total_tickets_by_baja = commands.command_get_total_tickets_filter(
			project_id = project_id,
			search = search 
		)

		search = schemas.TicketFilterPagination(
			priority = "normal"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		total_tickets_by_normal = commands.command_get_total_tickets_filter(
			project_id = project_id,
			search = search
		)

		search = schemas.TicketFilterPagination(
			priority = "inmediata"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		total_tickets_by_inmediata = commands.command_get_total_tickets_filter(
			project_id = project_id,
			search = search
		)

		search = schemas.TicketFilterPagination(
			state = "desarrollo"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		total_tickets_by_desarrollo = commands.command_get_total_tickets_filter(
			project_id = project_id,
			search = search
		) 

		search = schemas.TicketFilterPagination(
			state = "repaso"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		total_tickets_by_repaso = commands.command_get_total_tickets_filter(
			project_id = project_id,
			search = search
		)

		search = schemas.TicketFilterPagination(
			type = "archivado"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		total_tickets_by_archivado = commands.command_get_total_tickets_filter(
			project_id = project_id,
			search = search
		)

		search = schemas.TicketFilterPagination(
			type = "cerrado"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		total_tickets_by_cerrado = commands.command_get_total_tickets_filter(
			project_id = project_id,
			search = search
		)

		assert total_tickets_by_baja == 4
		assert total_tickets_by_normal == 5
		assert total_tickets_by_inmediata == 2
		assert total_tickets_by_desarrollo == 2
		assert total_tickets_by_repaso == 4
		assert total_tickets_by_archivado == 2
		assert total_tickets_by_cerrado == 1


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_tickets_filter_with_no_existent_project(self):
		"""
			Intentar obtener el total de tickets
			pero de un proyecto que no existe
		"""
		project_id = 100

		bulk_insert_ticket(db = self.db)

		search = schemas.TicketFilterPagination(
			priority = "baja"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		total_tickets = commands.command_get_total_tickets_filter(
			project_id = project_id,
			search = search
		)

		assert total_tickets == 0


	@pytest.mark.xfail(reason = "Valor incorrecto en priority", raises = ValueError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_tickets_filter_with_wrong_priority(self):
		"""
			Generar un error al enviar
			un valor de prioridad incorrecto
		"""
		project_id = 1

		bulk_insert_ticket(db = self.db)

		total_tickets = commands.command_get_total_tickets_filter(
			project_id = project_id,
			search = {"priority": "ahora"}
		)


	@pytest.mark.xfail(reason = "Valor incorrecto en state", raises = ValueError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_tickets_filter_with_wrong_state(self):
		"""
			Generar un error al enviar
			un valor de estado incorrecto
		"""
		project_id = 1

		bulk_insert_ticket(db = self.db)

		total_tickets = commands.command_get_total_tickets_filter(
			project_id = project_id,
			search = {"state": "salvado"}
		)


	@pytest.mark.xfail(reason = "Valor incorrecto en type", raises = ValueError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_tickets_filter_with_wrong_type(self):
		"""
			Generar un error al enviar
			un valor de tipo incorrecto
		"""
		project_id = 1

		bulk_insert_ticket(db = self.db)

		total_tickets = commands.command_get_total_tickets_filter(
			project_id = project_id,
			search = {"type": "registrado"}
		)

	@pytest.mark.xfail(reason = "Sin project_id", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_tickets_filter_without_project_id(self):
		"""
			Generar un error al no enviar
			el project_id
		"""
		project_id = 1

		bulk_insert_ticket(db = self.db)

		total_tickets = commands.command_get_total_tickets_filter(
			search = {"type": "abierto"}
		)
		

	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_tickets_filter_without_param_search(self):
		"""
			Validar que se obtenga el total de tickets
			sin aplicar filtros
		"""
		project_id = 1

		bulk_insert_ticket(db = self.db)

		total_tickets = commands.command_get_total_tickets_filter(
			project_id = project_id
		)

		assert total_tickets == 14


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_tickets_by_filter(self):
		"""
			Validar obtener tickets por proyecto
			aplicando un filtro
		"""
		project_id = 1

		bulk_insert_ticket(db = self.db)

		search = schemas.TicketFilterPagination(
			priority = "baja"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		tickets_by_priority_baja = commands.command_get_ticket_by_filter(
			project_id = project_id,
			search = search 
		)

		search = schemas.TicketFilterPagination(
			priority = "normal"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		tickets_by_priority_normal = commands.command_get_ticket_by_filter(
			project_id = project_id,
			search = search
		)

		search = schemas.TicketFilterPagination(
			priority = "inmediata"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		tickets_by_priority_inmediata = commands.command_get_ticket_by_filter(
			project_id = project_id,
			search = search
		)

		search = schemas.TicketFilterPagination(
			state = "desarrollo"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		tickets_by_state_desarrollo = commands.command_get_ticket_by_filter(
			project_id = project_id,
			search = search
		) 

		search = schemas.TicketFilterPagination(
			state = "repaso"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		tickets_by_state_repaso = commands.command_get_ticket_by_filter(
			project_id = project_id,
			search = search
		)

		search = schemas.TicketFilterPagination(
			type = "archivado"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		tickets_by_type_archivado = commands.command_get_ticket_by_filter(
			project_id = project_id,
			search = search
		)

		search = schemas.TicketFilterPagination(
			type = "cerrado"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		tickets_by_type_cerrado = commands.command_get_ticket_by_filter(
			project_id = project_id,
			search = search
		)

		assert tickets_by_priority_baja
		assert len(tickets_by_priority_baja) == 4
		assert tickets_by_priority_baja[0].project_id == project_id
		assert tickets_by_priority_baja[0].priority.name == "baja"

		assert tickets_by_priority_normal
		assert len(tickets_by_priority_normal) == 5
		assert tickets_by_priority_normal[0].project_id == project_id
		assert tickets_by_priority_normal[0].priority.name == "normal"

		assert tickets_by_priority_inmediata
		assert len(tickets_by_priority_inmediata) == 2
		assert tickets_by_priority_inmediata[0].project_id == project_id
		assert tickets_by_priority_inmediata[0].priority.name == "inmediata"

		assert tickets_by_state_desarrollo
		assert len(tickets_by_state_desarrollo) == 2
		assert tickets_by_state_desarrollo[0].project_id == project_id
		assert tickets_by_state_desarrollo[0].state.name == "desarrollo"

		assert tickets_by_state_repaso
		assert len(tickets_by_state_repaso) == 4
		assert tickets_by_state_repaso[0].project_id == project_id
		assert tickets_by_state_repaso[0].state.name == "repaso"

		assert tickets_by_type_archivado
		assert len(tickets_by_type_archivado) == 2
		assert tickets_by_type_archivado[0].project_id == project_id
		assert tickets_by_type_archivado[0].type.name == "archivado"

		assert tickets_by_type_cerrado
		assert len(tickets_by_type_cerrado) == 1
		assert tickets_by_type_cerrado[0].project_id == project_id
		assert tickets_by_type_cerrado[0].type.name == "cerrado"


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_tickets_by_filter_with_no_existent_project(self):
		"""
			Validar que retorne una lista vacia al
			intentar obtener los tickets de un proyecto
			que no existe.
		"""

		project_id = 100

		search = schemas.TicketFilterPagination(
			priority = "normal"
		).model_dump(exclude_defaults = True, exclude=['page', 'pageSize'])
		
		tickets = commands.command_get_ticket_by_filter(
			project_id = project_id,
			search = search
		)

		assert not tickets


	@pytest.mark.xfail(reason = "Valor incorrecto en priority", raises = ValueError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_tickets_by_filter_with_wrong_priority(self):
		"""
			Generer un error al enviar como
			filtro un valor incorrecto para 'priority'
		"""
		project_id = 1

		bulk_insert_ticket(db = self.db)

		tickets = commands.command_get_ticket_by_filter(
			project_id = project_id,
			search = {"priority": "ahora"}
		)


	@pytest.mark.xfail(reason = "Valor incorrecto en state", raises = ValueError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_tickets_by_filter_with_wrong_state(self):
		"""
			Generer un error al enviar como
			filtro un valor incorrecto para 'state'
		"""
		project_id = 1

		bulk_insert_ticket(db = self.db)

		tickets = commands.command_get_ticket_by_filter(
			project_id = project_id,
			search = {"state": "descartado"}
		)

	@pytest.mark.xfail(reason = "Valor incorrecto en type", raises = ValueError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_tickets_by_filter_with_wrong_type(self):
		"""
			Generer un error al enviar como
			filtro un valor incorrecto para 'type'
		"""
		project_id = 1

		bulk_insert_ticket(db = self.db)

		tickets = commands.command_get_ticket_by_filter(
			project_id = project_id,
			search = {"type": "eliminado"}
		)

	@pytest.mark.xfail(reason = "Sin project_id", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_tickets_by_filter_without_project_id(self):
		"""
			Generar un error al no enviar
			project_id
		"""
		bulk_insert_ticket(db = self.db)

		tickets = commands.command_get_ticket_by_filter(
			search = {"priority": "normal"}
		)


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_tickets_by_filter_without_param_search(self):
		"""
			Validar que se obtenga todos los tickets
			de un proyecto sin aplicar algún filtro
		"""
		project_id = 1

		bulk_insert_ticket(db = self.db)

		tickets_page_0 = commands.command_get_ticket_by_filter(
			project_id = project_id 
		)

		tickets_page_1 = commands.command_get_ticket_by_filter(
			project_id = project_id,
			page = 1
		)

		assert tickets_page_0
		assert len(tickets_page_0) == 10

		assert tickets_page_1
		assert len(tickets_page_1) == 4


	@pytest.mark.xfail(reason = "Valores no validos en paginación", raises = (ValueError, ValidationError))
	@pytest.mark.parametrize("pagination", [
		{"page": -1, "pageSize": 5},
		{"page": 0, "pageSize": -1},
		{"page": 0.1, "pageSize": 5},
		{"page": 1, "pageSize": 5.4},
	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_tickets_by_filter_with_wrong_page_and_pageSize(self, pagination):
		"""
			Generar un error al enviar valores
			negativos y con decimales en 'page' y 'pageSize'
		"""
		project_id = 1

		bulk_insert_ticket(db = self.db)

		tickets = commands.command_get_ticket_by_filter(
			project_id = project_id,
			search = {"priority": "normal"},
			page = pagination['page'],
			pageSize = pagination['pageSize']
		)


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_ticket_by_title(self):
		"""
			Validar obtener uno o más tickets por el titulo
		"""

		bulk_insert_ticket(db = self.db)

		ticket_title = schemas.TicketByTitle(
			title = "API"
		)

		result = commands.command_get_ticket_by_title(
			ticket = ticket_title
		)

		assert result
		assert ticket_title.title.lower() in result[0].title.lower()


		ticket_title_min = schemas.TicketByTitle(
			title = "api"
		)

		result = commands.command_get_ticket_by_title(
			ticket = ticket_title_min
		)

		assert result
		assert ticket_title_min.title.lower() in result[0].title.lower()


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_ticket_by_title_return_not_found_tickets(self):
		"""
			Validar que retorne una lista
			vacia cuando no encuentra ticket con
			el determinado titulo.
		"""

		bulk_insert_ticket(db = self.db)

		ticket_title = schemas.TicketByTitle(
			title = "Not found"
		)

		result = commands.command_get_ticket_by_title(
			ticket = ticket_title
		)

		assert not result
		assert len(result) == 0

	@pytest.mark.xfail(reason = "(Search by title) Titulo muy largo", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_ticket_by_title_with_too_long_title(self):
		"""
			Validar que genere un error
			al enviar un titulo a buscar muy largo
		"""

		bulk_insert_ticket(db = self.db)

		title = """
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		"""

		result = commands.command_get_ticket_by_title(
			ticket = {"title": title}
		)


	@pytest.mark.xfail(reason = "Sin 'title'", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_ticket_by_title_without_title(self):
		"""
			Generar un error al no enviar
			'title'
		"""
		bulk_insert_ticket(db = self.db)

		result = commands.command_get_ticket_by_title()


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_tickets_by_projects(self):
		"""
			Validar obtener tickets por proyecto
		"""

		insert_projects(db = self.db)
		insert_ticket_by_project(db = self.db)

		project_id_1 = 1
		project_id_2 = 2
		project_id_3 = 3
		project_id_4 = 4
		project_id_5 = 5


		tickets_project_id_1 = commands.command_get_tickets_by_project(
			project_id = project_id_1
		) 
		tickets_project_id_2 = commands.command_get_tickets_by_project(
			project_id = project_id_2
		)
		tickets_project_id_3 = commands.command_get_tickets_by_project(
			project_id = project_id_3
		)
		tickets_project_id_4 = commands.command_get_tickets_by_project(
			project_id = project_id_4
		)
		tickets_project_id_5 = commands.command_get_tickets_by_project(
			project_id = project_id_5
		)


		assert tickets_project_id_1
		assert len(tickets_project_id_1) == 2
		assert tickets_project_id_1[0].project_id == project_id_1


		assert tickets_project_id_2
		assert len(tickets_project_id_2) == 3
		assert tickets_project_id_2[0].project_id == project_id_2


		assert tickets_project_id_3
		assert len(tickets_project_id_3) == 2
		assert tickets_project_id_3[0].project_id == project_id_3


		assert tickets_project_id_4
		assert len(tickets_project_id_4) == 1
		assert tickets_project_id_4[0].project_id == project_id_4


		assert tickets_project_id_5
		assert len(tickets_project_id_5) == 1
		assert tickets_project_id_5[0].project_id == project_id_5


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_tickets_by_projects_with_no_existent_project(self):
		"""
			Intentar obtener todos los tickets de un
			proyecto que no existe.
		"""
		project_id = 3
		
		tickets = commands.command_get_tickets_by_project(
			project_id = project_id
		)

		assert not tickets
		assert len(tickets) == 0


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_tickets_by_projects_checking_pagination(self):
		"""
			Validar obtener los tickets de un proyecto
			y validando la paginación
		"""
		insert_projects(db = self.db)
		insert_ticket_by_project(db = self.db)

		project_id = 2

		tickets_page_0 = commands.command_get_tickets_by_project(
			project_id = project_id,
			pageSize = 2
		)

		tickets_page_1 = commands.command_get_tickets_by_project(
			project_id = project_id,
			page = 1,
			pageSize = 2
		)

		assert tickets_page_0
		assert len(tickets_page_0) == 2
		assert tickets_page_0[0].project_id == project_id

		assert tickets_page_1
		assert len(tickets_page_1) == 1
		assert tickets_page_1[0].project_id == project_id


	@pytest.mark.xfail(reason = "Valores no validos en paginación", raises = (ValueError, ValidationError))
	@pytest.mark.parametrize("pagination", [
		{"page": -1, "pageSize": 5},
		{"page": 1, "pageSize": -5},
		{"page": 0.1, "pageSize": 5},
		{"page": 0, "pageSize": 5.3}
	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_tickets_by_projects_with_wrong_page_and_pageSize(self, pagination):
		"""
			Generar un error al enviar valores para [page, pageSize]
			incorrectos (enteros negativos y números decimales)
		"""
		insert_projects(db = self.db)
		insert_ticket_by_project(db = self.db)
		
		project_id = 2

		tickets = commands.command_get_tickets_by_project(
			project_id = project_id,
			page = pagination["page"],
			pageSize = pagination["pageSize"]
		)

	@pytest.mark.xfail(reason = "Sin project_id", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_tickets_by_projects_without_project_id(self):
		"""
			Generar un error al no eviar un valor
			para 'project_id'
		"""

		insert_projects(db = self.db)
		insert_ticket_by_project(db = self.db)

		commands.command_get_tickets_by_project()


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_tickets_by_project(self):
		"""
			Validar obtener el total de tickets
			por proyectos
		"""
		insert_projects(db = self.db)
		insert_ticket_by_project(db = self.db)

		project_id_1 = 1
		project_id_2 = 2
		project_id_3 = 3
		project_id_4 = 4
		project_id_5 = 5

		total_tickets_project_id_1 = commands.command_get_total_tickets_project(
			project_id = project_id_1
		) 
		total_tickets_project_id_2 = commands.command_get_total_tickets_project(
			project_id = project_id_2
		)
		total_tickets_project_id_3 = commands.command_get_total_tickets_project(
			project_id = project_id_3
		)
		total_tickets_project_id_4 = commands.command_get_total_tickets_project(
			project_id = project_id_4
		)
		total_tickets_project_id_5 = commands.command_get_total_tickets_project(
			project_id = project_id_5
		)


		assert total_tickets_project_id_1 == 2

		assert total_tickets_project_id_2 == 3

		assert total_tickets_project_id_3 == 2

		assert total_tickets_project_id_4 == 1

		assert total_tickets_project_id_5 == 1


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_tickets_by_project_with_no_existent_project(self):
		"""
			Intentar obtener el total de tickets
			de un proyecto que no existe.
		"""
		project_id = 2

		total_tickets = commands.command_get_total_tickets_project(
			project_id = project_id
		)

		assert total_tickets == 0


	@pytest.mark.xfail(reason = "Sin project_id", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_tickets_by_project_without_project_id(self):
		"""
			Generar un error al no enviar el 
			project_id
		"""
		insert_projects(db = self.db)
		insert_ticket_by_project(db = self.db)

		total_tickets = commands.command_get_total_tickets_project()


	@pytest.mark.xfail(reason = "Valor incorrecto en project_id", raises = ValidationError)
	@pytest.mark.parametrize("project_id", [
		"abc",
		1.2,
		{"id": 1},
		[3],
		None,
		(2,3)
	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_tickets_by_project_with_wrong_project_id(self, project_id):
		"""
			Generar un error al enviar un valor incorrecto 
			en project_id
		"""
		insert_projects(db = self.db)
		insert_ticket_by_project(db = self.db)

		total_tickets = commands.command_get_total_tickets_project(
			project_id = project_id
		)
