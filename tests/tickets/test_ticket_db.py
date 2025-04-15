import pytest

from sqlalchemy.exc import IntegrityError

from tests import ENGINE
from tests import SESSION
from tests.tickets import set_ticket

from apps import Model
from apps.users.models import User
from apps.tickets.models import Ticket
from apps.projects.models import Project


class TestTicketDB:
	def setup_method(self):
		Model.metadata.drop_all(ENGINE)
		Model.metadata.create_all(ENGINE)

		self.db = SESSION

		user = user = User(
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

		self.ticket = ticket
		self.project = project

	def teardown_method(self):
		self.db.rollback()
		self.db.close()


	def test_save_data_db(self):
		"""
			Validar que se guardo la información en la BD
		"""

		tickets = self.db.query(Ticket).all()

		assert tickets
		assert len(tickets) == 1


	def test_create_ticket(self):
		"""
			Validar que se ha creado un ticket
		"""

		ticket = Ticket(
			title = "Tarea B",
			description = "Descripción de la tarea B",
			type = "abierto",
			state = "nuevo",
			priority = "baja",
			project_id = self.project.id
		)

		self.db.add(ticket)
		self.db.commit()
		self.db.refresh(ticket)


		assert ticket.id == 2
		assert ticket.title == "Tarea B"
		assert ticket.description == "Descripción de la tarea B"
		assert ticket.project_id == self.project.id
		assert ticket.type.name == "abierto"
		assert ticket.state.name == "nuevo"
		assert ticket.priority.name == "baja"


	def test_create_ticket_without_description(self):
		"""
			Crear un ticket sin una descripción
		"""

		ticket = Ticket(
			title = "Tarea B",
			type = "abierto",
			state = "nuevo",
			priority = "normal",
			project_id = self.project.id
		)

		self.db.add(ticket)
		self.db.commit()
		self.db.refresh(ticket)

		assert ticket.id == 2
		assert ticket.title == "Tarea B"
		assert ticket.description == None
		assert ticket.project_id == self.project.id
		assert ticket.type.name == "abierto"
		assert ticket.state.name == "nuevo"
		assert ticket.priority.name == "normal"


	def test_create_ticket_with_default_values(self):
		"""
			Intentar crear un ticket con sus valores por defecto
			- priority = "baja"
			- type = "abierto"
			- state = "nuevo"
		"""

		ticket = Ticket(
			title = "Tarea B",
			description = "Descripción de la tarea B",
			project_id = self.project.id
		)

		self.db.add(ticket)
		self.db.commit()
		self.db.refresh(ticket)

		assert ticket.id == 2
		assert ticket.title == "Tarea B"
		assert ticket.description == "Descripción de la tarea B"
		assert ticket.project_id == self.project.id
		assert ticket.type.name == "abierto"
		assert ticket.state.name == "nuevo"
		assert ticket.priority.name == "baja"


	def test_create_ticket_with_only_title_and_project_id(self):
		"""
			Crear un ticket con tan solo un titulo y el ID
			del proyecto al que pertece el ticket
		"""

		ticket = Ticket(
			title = "Tarea C",
			project_id = self.project.id
		)

		self.db.add(ticket)
		self.db.commit()
		self.db.refresh(ticket)


		assert ticket.id == 2
		assert ticket.title == "Tarea C"
		assert ticket.description == None
		assert ticket.type.name == "abierto"
		assert ticket.state.name == "nuevo"
		assert ticket.priority.name == "baja"
		assert ticket.project_id == self.project.id



	@pytest.mark.xfail(reason = "Datos incompletos", raises = IntegrityError)
	def test_create_ticket_with_incomplete_data(self):
		"""
			Intantar crear un ticket con datos incompletos
		"""

		ticket = Ticket(
			project_id = self.project.id
		)

		self.db.add(ticket)
		self.db.commit()
		self.db.refresh(ticket)


	@pytest.mark.xfail(reason = "Type incorrecto", raises = LookupError)
	def test_create_ticket_with_wrong_type(self):
		"""
			Intentar crear un ticket con una opción de 'type' incorrecta
		"""
		type_ticket = "oculto"
		
		ticket = Ticket(
			title = "Tarea B",
			description = "Descripción de la tarea B",
			type = type_ticket,
			project_id = self.project.id
		)

		self.db.add(ticket)
		self.db.commit()
		self.db.refresh(ticket)


	@pytest.mark.xfail(reason = "State incorrecto", raises = LookupError)
	def test_create_ticket_with_wrong_state(self):
		"""
			Intentar crear un ticket con una opción de 'state' incorrecta
		"""
		state_ticket = "documentado"
		
		ticket = Ticket(
			title = "Tarea B",
			description = "Descripción de la tarea B",
			state = state_ticket,
			project_id = self.project.id
		)

		self.db.add(ticket)
		self.db.commit()
		self.db.refresh(ticket)


	@pytest.mark.xfail(reason = "Prriority incorrecto", raises = LookupError)
	def test_create_ticket_with_wrong_priority(self):
		"""
			Intentar crear un ticket con una opción de 'priority' incorrecta
		"""
		priority_ticket = "ahora"
		
		ticket = Ticket(
			title = "Tarea B",
			description = "Descripción de la tarea B",
			priority = priority_ticket,
			project_id = self.project.id
		)

		self.db.add(ticket)
		self.db.commit()
		self.db.refresh(ticket)


	def test_create_ticket_without_project_id(self):
		"""
			Intentar crear un ticket sin el ID de un proyecto
		"""

		ticket = Ticket(
			title = "Tarea B",
			type = "abierto",
			state = "nuevo",
			priority = "normal",
			description = "Descripción de la tarea B",
		)

		self.db.add(ticket)
		self.db.commit()
		self.db.refresh(ticket)

		assert ticket.id == 2
		assert ticket.title == "Tarea B"
		assert ticket.type.name == "abierto"
		assert ticket.state.name == "nuevo"
		assert ticket.priority.name == "normal"
		assert ticket.description == "Descripción de la tarea B"
		assert ticket.project_id == None

		"""
		Se debe tener una validación que impida que se cree un
		ticket sin un proyecto
		"""


	def test_create_ticket_with_wrong_title(self):
		"""
			Intentar crear un ticket con un 'titulo' mayor
			a la restricción indicada en la tabla. 
		"""

		titulo = """
			Lorem ipsum dolor sit amet consectetur adipisicing elit. 
			Aspernatur, magni nostrum est deserunt officia quas illo quis, 
			aliquam unde animi quod debitis voluptates recusandae ut minima, 
			eos dicta molestiae accusamus?
		"""

		ticket = Ticket(
			title = titulo,
			description = "Descripción de la tarea B",
			project_id = self.project.id
		)

		self.db.add(ticket)
		self.db.commit()
		self.db.refresh(ticket)

		assert ticket.id == 2
		assert ticket.title == titulo
		assert len(ticket.title) == len(titulo)
		assert ticket.type.name == "abierto"
		assert ticket.state.name == "nuevo"
		assert ticket.priority.name == "baja"
		assert ticket.description == "Descripción de la tarea B"
		assert ticket.project_id == self.project.id

		"""
		Se debe crear una validación que impida que se cree 
		un ticket con un titulo que supere el limite
		de longitud establecido en la tabla.
		"""


	def test_create_ticket_with_wrong_description(self):
		"""
			Intentar crear un ticket con una 'descripción' mayor
			a la restricción indicada en la tabla. 
		"""

		descripcion = """
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

		ticket = Ticket(
			title = "Tarea B",
			description = descripcion,
			project_id = self.project.id
		)

		self.db.add(ticket)
		self.db.commit()
		self.db.refresh(ticket)

		assert ticket.id == 2
		assert ticket.title == "Tarea B"
		assert ticket.type.name == "abierto"
		assert ticket.state.name == "nuevo"
		assert ticket.priority.name == "baja"
		assert ticket.description == descripcion
		assert len(ticket.description) == len(descripcion)
		assert ticket.project_id == self.project.id

		"""
		Se debe crear una validación que impida que se cree 
		un ticket con una descripción que supere el limite
		de longitud establecido en la tabla
		"""