import pytest
from unittest.mock import patch

from sqlalchemy import insert
from sqlalchemy import update
from pydantic import ValidationError

from tests import ENGINE
from tests import SESSION
from tests import get_db
from tests.tickets import set_ticket

from apps import Model
from apps.users.models import User
from apps.projects.models import Project
from apps.tickets.models import Ticket
from apps.tickets.commands import commands
from apps.tickets.models import TicketHistory
from apps.tickets.models import StateTicketHistory
from apps.tickets.commands.utils.utils import set_message_ticket_history

def create_ticket(db, project_id: int = 1):
	ticket = set_ticket(project_id = project_id)

	db.add(ticket)
	db.commit()
	db.refresh(ticket)

	return ticket


def update_ticket(db, ticket_id: int = 1, values:dict = {}):

	sql = (
		update(Ticket)
		.where(Ticket.id == ticket_id)
		.values(**values)
		.returning(Ticket)
	)

	ticket = db.scalar(sql)

	return ticket


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

class TestTicketHistoryCommand:

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


		self.project = project


	def teardown_method(self):
		self.db.rollback()
		self.db.close()


	def test_validate_save_db(self):
		"""
			Validar que se han guardado
			los datos iniciales en la DB
		"""

		user = self.db.get(User, 1)

		assert user
		assert user.id == 1

		project = self.db.get(Project, 1)

		assert project
		assert project.id == 1


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_history(self):
		"""
			Validar que se genere el historial
			cuando se crea un nuevo ticket
		"""

		ticket = create_ticket(db = self.db, project_id = self.project.id)

		ticket_history = commands.command_add_ticket_history(
			ticket_id = ticket.id
		)

		assert ticket_history
		assert ticket_history.id == 1
		assert ticket_history.ticket_id == ticket.id
		assert ticket_history.state.name == StateTicketHistory.crear.name


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_history_by_update_ticket(self):
		"""
			Validar que se genere el historial
			cuando se actualiza un ticket
		"""

		ticket = create_ticket(db = self.db, project_id = self.project.id)

		values = {"title": "Nuevo titulo tarea"}
		
		updated = update_ticket(
			db = self.db,
			ticket_id = ticket.id, 
			values = values
		)

		ticket_history = commands.command_add_ticket_history(
			ticket_id = ticket.id,
			infoTicket = values,
			state = "actualizar"
		)

		assert ticket_history
		assert ticket_history.id == 1
		assert ticket_history.ticket_id == ticket.id
		assert ticket_history.state.name == StateTicketHistory.actualizar.name


	@pytest.mark.xfail(reason = "Valor incorreto para 'state'", raises = ValueError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_history_with_wrong_state(self):
		"""
			Generar un error al crear el historial
			de un ticket con un 'state' incorrecto
		"""
		ticket = create_ticket(db = self.db, project_id = self.project.id)

		ticket_history = commands.command_add_ticket_history(
			ticket_id = ticket.id,
			state = "nuevo"
		)


	@pytest.mark.xfail(reason = "No existe este ticket", raises = ValueError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_history_with_no_existent_ticket(self):
		"""
			Generar un error al crear el historial
			con un ticket ID invalido
		"""
		ticket = create_ticket(db = self.db, project_id = self.project.id)

		ticket_id = ticket.id + 1
		
		ticket_history = commands.command_add_ticket_history(
			ticket_id = ticket_id,
		)

		assert ticket_history
		assert ticket_history.id == 1


	@pytest.mark.xfail(reason = "Valor incorrecto para ticket_id", raises = ValidationError)
	@pytest.mark.parametrize("ticket_id", [
		"ab12",
		12.3,
		None
	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_history_with_wrong_ticket_id(self, ticket_id):
		"""
			Generar un error al crear el historial
			con un ticket_id incorrecto
		"""

		ticket_history = commands.command_add_ticket_history(
			ticket_id = ticket_id,
		)
		
	
	@pytest.mark.xfail(reason = "Sin ticket_id", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_create_ticket_history_without_ticket_id(self):
		"""
			Generar un error al crear el historial
			sin enviar ticket_id
		"""
		ticket = create_ticket(db = self.db, project_id = self.project.id)

		ticket_history = commands.command_add_ticket_history()

	
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_ticket_histories(self):
		"""
			Validar obtener la lista de historial
			de cambios de un ticket
		"""
		ticket = create_ticket(db = self.db, project_id = self.project.id)
		create_ticket_histories(db = self.db, ticket_id = ticket.id)

		histories = commands.command_get_ticket_histories(
			ticket_id = ticket.id
		)

		assert histories
		assert len(histories) == 4
		assert histories[0].ticket_id == ticket.id
		assert histories[0].message == f"Se ha creado un nuevo ticket con ID: {ticket.id}"
		assert histories[0].state.name == StateTicketHistory.crear.name
		assert histories[1].state.name == StateTicketHistory.actualizar.name


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_ticket_histories_with_no_existent_ticket(self):
		"""
			Intentar obtener el historial de cambio de un
			ticket que no existe
		"""

		ticket = create_ticket(db = self.db, project_id = self.project.id)
		create_ticket_histories(db = self.db, ticket_id = ticket.id)

		ticket_id = 100

		histories = commands.command_get_ticket_histories(
			ticket_id = ticket_id
		)

		assert not histories
		assert len(histories) == 0


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_ticket_histories_with_pagination(self):
		"""
			Validar obtener el historial de cambios de
			un ticket pero, usando paginación para
			manipular la respuesta
		"""
		ticket = create_ticket(db = self.db, project_id = self.project.id)
		create_ticket_histories(db = self.db, ticket_id = ticket.id)

		ticket_id = ticket.id

		histories_page_0 = commands.command_get_ticket_histories(
			ticket_id = ticket_id,
			page = 0,
			pageSize = 3 
		)

		histories_page_1 = commands.command_get_ticket_histories(
			ticket_id = ticket_id,
			page = 1,
			pageSize = 3 
		)

		assert histories_page_0
		assert len(histories_page_0) == 3

		assert histories_page_1
		assert len(histories_page_1) == 1


	@pytest.mark.xfail(reason = "Valor incorrecto para ticket_id", raises = ValidationError)
	@pytest.mark.parametrize("ticket_id", [
		[3],
		"abc",
		None,
		4.4,
	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_ticket_histories_with_wrong_ticket_id(self, ticket_id):
		"""
			Generar un error al enviar un valor incorrecto
			para ticket_id
		"""
		ticket = create_ticket(db = self.db, project_id = self.project.id)
		create_ticket_histories(db = self.db, ticket_id = ticket.id)

		histories = commands.command_get_ticket_histories(
			ticket_id = ticket_id
		)


	@pytest.mark.xfail(reason = "Valor incorrecto para 'page' y 'pageSize'", raises = (ValidationError, ValueError))
	@pytest.mark.parametrize("pagination", [
		{"page": 0, "pageSize": -5},
		{"page": -1, "pageSize": 5},
		{"page": 0.1, "pageSize": 5},
		{"page": 0, "pageSize": 5.2}
	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_ticket_histories_with_wrong_values_for_pagination(self, pagination):
		"""
			Generar un error al enviar un valor incorrecto
			para ticket_id
		"""
		ticket = create_ticket(db = self.db, project_id = self.project.id)
		create_ticket_histories(db = self.db, ticket_id = ticket.id)

		histories = commands.command_get_ticket_histories(
			ticket_id = ticket.id,
			page = pagination["page"],
			pageSize = pagination["pageSize"]
		)


	@pytest.mark.xfail(reason = "Sin ticket_id", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_ticket_histories_without_ticket_id(self):
		"""
			Generar un error al no eviar un valor
			para ticket_id
		"""
		ticket = create_ticket(db = self.db, project_id = self.project.id)
		create_ticket_histories(db = self.db, ticket_id = ticket.id)

		histories = commands.command_get_ticket_histories()


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_ticket_histories(self):
		"""
			Validar obtener el total de historial de cambios
			creado para un ticket
		"""
		ticket = create_ticket(db = self.db, project_id = self.project.id)
		create_ticket_histories(db = self.db, ticket_id = ticket.id)

		total_histories = commands.command_get_total_ticket_histories(
			ticket_id = ticket.id
		)

		assert total_histories == 4


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_ticket_histories_with_no_existent_ticket(self):
		"""
			Validar obtener el total de historial de cambios
			de un ticket que no existe
		"""

		ticket = create_ticket(db = self.db, project_id = self.project.id)
		create_ticket_histories(db = self.db, ticket_id = ticket.id)

		ticket_id = 100
		
		total_histories = commands.command_get_total_ticket_histories(
			ticket_id = ticket_id
		)

		assert total_histories == 0


	@pytest.mark.xfail(reason = "Sin ticket_id", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_ticket_histories_without_ticket_id(self):
		"""
			Generar un error al no eviar un valor para
			ticket_id
		"""
		ticket = create_ticket(db = self.db, project_id = self.project.id)
		create_ticket_histories(db = self.db, ticket_id = ticket.id)

		total_histories = commands.command_get_total_ticket_histories()

	
	@pytest.mark.xfail(reason = "Valor incorrecto para ticket_id", raises = ValidationError)
	@pytest.mark.parametrize("ticket_id", [
		12.2,
		"bnh",
		None,
		(12,4)
	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_total_ticket_histories_with_wrong_ticket_id(self, ticket_id):
		"""
			Generar un error al eviar valores incorrectos
			para ticket_id
		"""
		ticket = create_ticket(db = self.db, project_id = self.project.id)
		create_ticket_histories(db = self.db, ticket_id = ticket.id)

		total_histories = commands.command_get_total_ticket_histories(
			ticket_id = ticket_id
		)


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_detail_ticket_history(self):
		"""
			Validar obtener el detalle de un 
			historial de cambio
		"""

		ticket = create_ticket(db = self.db, project_id = self.project.id)
		create_ticket_histories(db = self.db, ticket_id = ticket.id)

		detail_history = commands.command_get_detail_ticket_history(
			history_id = 1
		)


		assert detail_history.id == 1
		assert detail_history.state.name == StateTicketHistory.crear.name
		assert detail_history.message == f"Se ha creado un nuevo ticket con ID: {1}"


		detail_history = commands.command_get_detail_ticket_history(
			history_id = 3
		)

		assert detail_history.id == 3
		assert detail_history.state.name == StateTicketHistory.actualizar.name


	@pytest.mark.xfail(reason = "No existe este historial de cambios", raises = ValueError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_detail_with_no_existent_ticket_history(self):
		"""
			Intentar obtener el detalle de un historial
			de cambio que no existe
		"""
		ticket = create_ticket(db = self.db, project_id = self.project.id)
		create_ticket_histories(db = self.db, ticket_id = ticket.id)

		history_id = 100
		
		detail_history = commands.command_get_detail_ticket_history(
			history_id = history_id
		)


	@pytest.mark.xfail(reason = "Sin history_id", raises = ValidationError)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_detail_ticket_history_without_history_id(self):
		"""
			Generar un error al no enviar un valor para
			history_id
		"""
		ticket = create_ticket(db = self.db, project_id = self.project.id)
		create_ticket_histories(db = self.db, ticket_id = ticket.id)

		detail_history = commands.command_get_detail_ticket_history()


	@pytest.mark.xfail(reason = "Valor incorrecto para history_id", raises = ValidationError)
	@pytest.mark.parametrize("history_id", [
		1.3,
		"hola",
		[1,3],
		{"id": 1}
	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_get_detail_ticket_history_wit_wrong_history_id(self, history_id):
		"""
			Generar un error al enviar un valor incorrecto para
			history_id
		"""
		ticket = create_ticket(db = self.db, project_id = self.project.id)
		create_ticket_histories(db = self.db, ticket_id = ticket.id)

		detail_history = commands.command_get_detail_ticket_history(
			history_id = history_id
		)

