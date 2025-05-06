import pytest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy import func
from sqlalchemy import select

from pydantic import ValidationError

from tests import ENGINE
from tests import SESSION
from tests import get_db
from tests.tickets import set_ticket
from tests.tickets import set_ticket_schema
from tests.tickets import bulk_insert_ticket
from tests.tickets import create_ticket_histories
from tests.tickets import bulk_insert_ticket_multiple_projects

from main import app
from apps import Model
from apps.users.models import User
from apps.projects.models import Project
from apps.tickets.models import Ticket
from apps.tickets.models import ChoicesType
from apps.tickets.models import ChoicesState
from apps.tickets.models import ChoicesPrority
from apps.tickets.models import StateTicketHistory
from apps.tickets.routes import router
from apps.tickets.schemas import schemas
from apps.tickets.commands.utils.error_messages import (
	InvalidPriority,
	InvalidState,
	InvalidType,
	DoesNotExistsTicket,
	PaginationError,
	DoesNotExistsTicketHistory,
	EmptyValues
)

from apps.projects.commands.utils.error_messages import DoesNotExistsProject

str_choices_priority = [choice.name for choice in ChoicesPrority]

ResponseNoToken = {"detail": "Ausencia del token en la cabecera"}
TokenExpirado = {
	"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
ResponseTokenNoValido = {"detail": "Token no valido"}



client = TestClient(app)

class TestTicketRoute:
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

		project_2 = Project(
			title = "Proyecto de videojuegos",
			description = "Proyecto para un videojuego de arcade",
			user_id = user.id
		)
		
		self.db.add(project_2)
		self.db.commit()
		self.db.refresh(project_2)

		ticket = set_ticket(project_id = project.id)
		
		self.db.add(ticket)
		self.db.commit()
		self.db.refresh(ticket)

		self.user = user
		self.project = project
		self.project_2 = project_2

		self.ticket = ticket

		self.url = "/ticket"
		self.headers = {"Content-Type": "application/json"}
		self.auth = {"Authorization": "Bearer token-key"}

	def teardown_method(self):
		self.db.rollback()
		self.db.close()


	def test_save_db(self):
		"""
			Validar que se han guardado los datos en la DB
		"""

		user = self.db.get(User, 1)
		project = self.db.get(Project, 1)
		ticket = self.db.get(Ticket, 1)

		assert user.id == 1
		assert project.id == 1
		assert ticket.id == 1


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_ticket(self, mockToken):
		"""
			Validar ruta para crear un ticket
		"""
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		ticket = set_ticket_schema(
			title = "Probar proyecto",
			project_id = self.project.id,
			priority = "alta",
		)

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = ticket.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 201
		assert responseJson["id"] == 2
		assert responseJson["title"] == ticket.title
		assert responseJson["description"] ==  ticket.description
		assert responseJson["type"] ==  ChoicesType.abierto.name
		assert responseJson["state"] ==  ChoicesState.nuevo.name
		assert responseJson["priority"] ==  ticket.priority
		assert responseJson["project_id"] ==  ticket.project_id


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_ticket_with_wrong_priority(self, mockToken):
		"""
			Intentar crear un nuevo ticket
			con una prioridad incorrecta
		"""
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		priority = "ahora"

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"project_id": self.project.id,
				"title": "Tarea 1",
				"priority": priority
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson["message"] == f"La prioridad elegida es incorrecta, debe ser: {str_choices_priority} alguna de estás opciones."
		assert responseJson["detail"] == f"Input error: {priority}"

	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_ticket_with_too_long_title(self, mockToken):
		"""
			Intentar crear un ticket con un titulo
			muy largo
		"""
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		title ="""
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		"""
		
		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"project_id": self.project.id,
				"title": title
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson["message"] == "El titulo es demasiado largo, debe ser menor o igual a 30 caracteres"
		assert responseJson["detail"] == f"Input error: {title}"


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_ticket_with_too_short_title(self, mockToken):
		"""
			Intentar crear un ticket con un titulo
			muy largo
		"""
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		title = "App"
		
		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"project_id": self.project.id,
				"title": title
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson["message"] == "El titulo es demasiado corto, debe ser mayor o igual a 5 caracteres"
		assert responseJson["detail"] == f"Input error: {title}"


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_ticket_without_title(self, mockToken):
		"""
			Intentar crear un ticket sin enviar
			un valor para el titulo
		"""
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"project_id": self.project.id,
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson["message"] == "Field required"
		assert "detail" not in responseJson


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_ticket_with_too_long_description(self, mockToken):
		"""
			Intentar crear un ticket con una descripción
			muy larga
		"""
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		description ="""
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
		
		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"project_id": self.project.id,
				"title": "Tarea 1",
				"description": description
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson["message"] == "La descripción  es demasiado largo, debe ser menor o igual a 200 caracteres"
		assert responseJson["detail"] == f"Input error: {description}"


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_ticket_with_too_short_description(self, mockToken):
		"""
			Intentar crear un ticket con una descripción
			muy larga
		"""
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		description = "App"
		
		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"project_id": self.project.id,
				"title": "Tarea 1",
				"description": description
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson["message"] == "La descripción es demasiado corto, debe ser mayor o igual a 5 caracteres"
		assert responseJson["detail"] == f"Input error: {description}"


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_ticket_without_description(self, mockToken):
		"""
			Intentar crear un ticket sin una
			descripción
		"""
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)
		
		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"project_id": self.project.id,
				"title": "Tarea 1",
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 201
		assert responseJson["id"] == 2
		assert responseJson["title"] == "Tarea 1"
		assert responseJson["description"] == None


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_ticket_with_no_existent_project(self, mockToken):
		"""
			Intentar crear un ticket con un ID
			de proyecto que no existe
		"""

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)
		
		project_id = 100

		ticket = set_ticket_schema(
			title = "Probar proyecto",
			project_id = project_id,
			priority = "alta",
		)

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = ticket.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 404
		assert responseJson == {"message": DoesNotExistsProject.get(id = project_id)}


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_create_ticket_without_authorization(self):
		"""
			Intentar crear un ticket pero,
			sin enviar un token de autorización
		"""

		ticket = set_ticket_schema(
			title = "Probar proyecto",
			project_id = self.project.id,
			priority = "alta",
		)

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = ticket.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseNoToken


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_create_ticket_with_expired_token(self):
		"""
			Intentar crear un ticket pero,
			enviando un token expirado
		"""
		self.auth.update(TokenExpirado)
		
		self.headers.update(self.auth)

		ticket = set_ticket_schema(
			title = "Probar proyecto",
			project_id = self.project.id,
			priority = "alta",
		)

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = ticket.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseTokenNoValido


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_by_id(self, mockToken):
		"""
			Validar obtener un ticket por su ID
		"""

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)
		
		ticket_id = self.ticket.id

		response = client.get(
			f"{self.url}/{ticket_id}",
			headers = self.headers
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["id"] == self.ticket.id
		assert responseJson["title"] == self.ticket.title
		assert responseJson["description"] == self.ticket.description
		assert responseJson["type"] == self.ticket.type.name
		assert responseJson["state"] == self.ticket.state.name
		assert responseJson["priority"] == self.ticket.priority.name
		assert responseJson["project"]["id"] == self.ticket.project_id


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_with_no_existent_ticket(self, mockToken):
		"""
			Intentar obtener un ticket por un ID
			que no existe
		"""

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)
		
		ticket_id = 100

		response = client.get(
			f"{self.url}/{ticket_id}",
			headers = self.headers
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 404
		assert responseJson == {"message": DoesNotExistsTicket.get(id = ticket_id)}


	@pytest.mark.parametrize("ticket_id", [
		"acbd",
		12.2,
		None
	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_by_id_wit_wrong_ticket_id(self, mockToken, ticket_id):
		"""
			Intentar obtener un ticket pero,
			enviado como valor del ticket_id, un
			valor incorrecto
		"""

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)
		
		response = client.get(
			f"{self.url}/{ticket_id}",
			headers = self.headers
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_get_ticket_by_id_without_authorization(self):
		"""
			Intentar obtener un ticket por su ID pero,
			sin enviar un token autorización
		"""
		ticket_id = self.ticket.id

		response = client.get(
			f"{self.url}/{ticket_id}",
			headers = self.headers
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseNoToken


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_get_ticket_by_id_with_expired_token(self):
		"""
			Intentar obtener un ticket por su ID pero,
			con un token expirado
		"""
		self.auth.update(TokenExpirado)
		
		self.headers.update(self.auth)

		ticket_id = self.ticket.id

		response = client.get(
			f"{self.url}/{ticket_id}",
			headers = self.headers
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseTokenNoValido


	@pytest.mark.parametrize("search, total_search", [
		({"priority": "normal"}, 5),
		({"priority": "inmediata"}, 2),
		({"priority": "alta"}, 3),
		({"state": "desarrollo"}, 2),
		({"state": "repaso"}, 4),
		({"type": "archivado"}, 2),
		({"type": "cerrado"}, 1)
	])
	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_by_filter(self, mockToken, search, total_search):
		"""
			Validar obtener tickets aplicando un filtro
			de busqueda
		"""
		bulk_insert_ticket(db = self.db)

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)
		
		project_id = self.project.id
		
		response = client.get(
			f"{self.url}/project/{project_id}/search",
			headers = self.headers,
			params = search
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] == None
		assert responseJson["current"] == 1
		assert responseJson["next"] == None
		assert responseJson["project"]["id"] == project_id
		assert responseJson["content"]["total"] == total_search

		key = list(search.keys()).pop()
		value = list(search.values()).pop()

		assert responseJson["content"]["tickets"][0][key] == value


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_by_filter_with_wrong_value_filter(self, mockToken):
		"""
			Intentar obtener tickets aplicando
			un filtro pero, enviado un valor incorrecto
			para los filtros 
		"""

		bulk_insert_ticket(db = self.db)

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)
		
		project_id = self.project.id

		search_priority = {"priority": "ahora"}
		response = client.get(
			f"{self.url}/project/{project_id}/search",
			headers = self.headers,
			params = search_priority
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson["detail"] == f"Input error: {search_priority['priority']}"


		search_state = {"state": "check"}
		response = client.get(
			f"{self.url}/project/{project_id}/search",
			headers = self.headers,
			params = search_state
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson["detail"] == f"Input error: {search_state['state']}"
		

		search_type = {"type": "eliminado"}
		response = client.get(
			f"{self.url}/project/{project_id}/search",
			headers = self.headers,
			params = search_type
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson["detail"] == f"Input error: {search_type['type']}"


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_by_filter_with_no_existent_project(self, mockToken):
		"""
			Intentar obtener todos los tickets de
			un proyecto aplicando un filtro de busqueda, 
			pero enviado un ID de proyecto que no existe.
		"""
		bulk_insert_ticket(db = self.db)

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)
		
		project_id = 100

		search = {"priority": "alta"}
		
		response = client.get(
			f"{self.url}/project/{project_id}/search",
			headers = self.headers,
			params = search
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 404
		assert responseJson == {"message": DoesNotExistsProject.get(id = project_id)}

	
	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_by_filter_checking_pagination(self, mockToken):
		"""
			Validar el funcionamiento de la paginación
			en la busqueda de tickets por proyecto,
			aplicando un filtro. 
		"""
		bulk_insert_ticket(db = self.db)

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		project_id = self.project.id

		pageSize = 3

		search = {
			"priority": "normal",
			"pageSize": pageSize
		}
		
		response = client.get(
			f"{self.url}/project/{project_id}/search",
			headers = self.headers,
			params = search
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] == None 
		assert responseJson["current"] == 1
		assert responseJson["next"] != None
		assert responseJson["project"]["id"] == project_id
		assert responseJson["content"]["total"] == 5
		assert len(responseJson["content"]["tickets"]) == 3
		assert responseJson["content"]["tickets"][0]["priority"] == "normal"

		page = 2

		search = {
			"priority": "normal",
			"page": page,
			"pageSize": pageSize
		}
		
		response = client.get(
			responseJson["next"],
			headers = self.headers
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] != None 
		assert responseJson["current"] == page
		assert responseJson["next"] == None
		assert responseJson["project"]["id"] == project_id
		assert responseJson["content"]["total"] == 5
		assert len(responseJson["content"]["tickets"]) == 2
		assert responseJson["content"]["tickets"][0]["priority"] == "normal"


	@pytest.mark.parametrize("pagination, errors", [
		(
			{"page": 1, "pageSize": -5},
			{"message": "Input should be greater than or equal to 1"}
		),
		(
			{"page": -1, "pageSize": 5},
			{"message": "Input should be greater than or equal to 1"}
		),
		(
			{"page": 0, "pageSize": 5},
			{"message": "Input should be greater than or equal to 1"}
		),
		(
			{"page": 1, "pageSize": 25},
			{"message": "Input should be less than or equal to 20"}
		),

	])
	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_by_filter_with_wrong_value_pagination(self, mockToken, pagination, errors):
		"""
			Intentar obtener todos los tickets de
			un proyecto aplicando un filtro de busqueda,
			pero enviando valores incorrectos para la paginación
		"""
		bulk_insert_ticket(db = self.db)

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		project_id = self.project.id

		search = {
			"priority": "normal",
			"page": pagination["page"],
			"pageSize": pagination["pageSize"]
		}
		
		response = client.get(
			f"{self.url}/project/{project_id}/search",
			headers = self.headers,
			params = search
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson == errors


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_by_filter_with_too_high_page(self, mockToken):
		"""
			Intentar obtener todos los tickets de
			un proyecto aplicando un filtro de busqueda,
			pero enviando un valor muy grande para page 
			en la paginación 
		"""

		bulk_insert_ticket(db = self.db)

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		project_id = self.project.id

		page = 3

		search = {
			"priority": "normal",
			"page": page,
			"pageSize": 3
		}

		response = client.get(
			f"{self.url}/project/{project_id}/search",
			headers = self.headers,
			params = search
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] == None 
		assert responseJson["current"] == page
		assert responseJson["next"] == None
		assert responseJson["project"]["id"] == project_id
		assert responseJson["content"]["total"] == 5
		assert not responseJson["content"]["tickets"]
		assert len(responseJson["content"]["tickets"]) == 0


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_by_filter_without_filter_search(self, mockToken):
		"""
			Intentar obtener todos los tickets de
			un proyecto sin aplicar un filtro de busqueda
		"""
		bulk_insert_ticket(db = self.db)

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		project_id = self.project.id

		response = client.get(
			f"{self.url}/project/{project_id}/search",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] == None 
		assert responseJson["current"] == 1
		assert responseJson["next"] != None
		assert responseJson["project"]["id"] == project_id
		assert responseJson["content"]["total"] == 14
		assert responseJson["content"]["tickets"]
		assert len(responseJson["content"]["tickets"]) == 10

		response = client.get(
			responseJson["next"],
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] != None 
		assert responseJson["current"] == 2
		assert responseJson["next"] == None
		assert responseJson["project"]["id"] == project_id
		assert responseJson["content"]["total"] == 14
		assert responseJson["content"]["tickets"]
		assert len(responseJson["content"]["tickets"]) == 4


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_get_ticket_by_filter_without_authorization(self):
		"""
			Intentar obtener todos los tickets de
			un proyecto aplicando un filtro de busqueda,
			pero sin enviar token de autenticación
		"""
		bulk_insert_ticket(db = self.db)

		project_id = self.project.id

		search = {
			"priority": "normal",
		}

		response = client.get(
			f"{self.url}/project/{project_id}/search",
			headers = self.headers,
			params = search
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseNoToken


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_get_ticket_by_filter_with_expired_token(self):
		"""
			Intentar obtener todos los tickets de
			un proyecto aplicando un filtro de busqueda,
			pero enviando un token expirado
		"""
		self.auth.update(TokenExpirado)
		
		self.headers.update(self.auth)

		bulk_insert_ticket(db = self.db)

		project_id = self.project.id

		search = {
			"priority": "normal",
		}

		response = client.get(
			f"{self.url}/project/{project_id}/search",
			headers = self.headers,
			params = search
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseTokenNoValido


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_by_title(self, mockToken):
		"""
			Obtener un ticket haciendo una busqueda
			por su titulo
		"""
		bulk_insert_ticket_multiple_projects(db = self.db)

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		project_id = self.project.id

		ticket = schemas.TicketByTitle(
			title = "ción"
		)

		response = client.get(
			f"{self.url}/project/{project_id}/ticket",
			headers = self.headers,
			params = ticket.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["tickets"]
		assert ticket.title in responseJson["tickets"][0]["title"]


		project_id = 2
		ticket = schemas.TicketByTitle(
			title = "API"
		)
		
		response = client.get(
			f"{self.url}/project/{project_id}/ticket",
			headers = self.headers,
			params = ticket.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["tickets"]
		assert len(responseJson["tickets"]) == 2
		assert ticket.title in responseJson["tickets"][0]["title"]


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_by_title_with_no_existent_project(self, mockToken):
		"""
			Intentar obtener un ticket por su titulo,
			pero enviado el ID de un proyecto que no existe
		"""
		bulk_insert_ticket_multiple_projects(db = self.db)

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		project_id = 100
		ticket = schemas.TicketByTitle(
			title = "limites"
		)

		response = client.get(
			f"{self.url}/project/{project_id}/ticket",
			headers = self.headers,
			params = ticket.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert not responseJson["tickets"]
		assert len(responseJson["tickets"]) == 0


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_by_title_with_wrong_title(self, mockToken):
		"""
			Intentar obtener un ticket 
			pero enviando un valor para la busqueda muy grande
		"""
		bulk_insert_ticket_multiple_projects(db = self.db)

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		title = """
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		"""
		project_id = self.project.id

		response = client.get(
			f"{self.url}/project/{project_id}/ticket",
			headers = self.headers,
			params = {
				"title": title
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_by_title_with_not_find_ticket(self, mockToken):
		"""
			Intentar obtener un ticket por su titulo,
			pero sin encontrar resultados
		"""
		bulk_insert_ticket_multiple_projects(db = self.db)

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		project_id = self.project_2.id

		ticket = schemas.TicketByTitle(
			title = "App"
		)

		response = client.get(
			f"{self.url}/project/{project_id}/ticket",
			headers = self.headers,
			params = ticket.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert not responseJson["tickets"]
		assert len(responseJson["tickets"]) == 0


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_by_title_without_title(self, mockToken):
		"""
			Intentar obtener un ticket 
			pero sin enviar un valor para la busqueda por
			su titulo 
		"""
		bulk_insert_ticket_multiple_projects(db = self.db)

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		project_id = self.project_2.id

		response = client.get(
			f"{self.url}/project/{project_id}/ticket",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson == {"message": "Field required"}


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_get_ticket_by_title_without_authorization(self):
		"""
			Intentar obtener un ticket por su titulo,
			pero sin enviar un token de authorización
		"""
		bulk_insert_ticket_multiple_projects(db = self.db)

		project_id = self.project.id
		ticket = schemas.TicketByTitle(
			title = "Tarea"
		)

		response = client.get(
			f"{self.url}/project/{project_id}/ticket",
			headers = self.headers,
			params = ticket.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseNoToken


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_get_ticket_by_title_with_expired_token(self):
		"""
			Intentar obtener un ticket por su titulo,
			pero enviando un token expirado
		"""
		bulk_insert_ticket_multiple_projects(db = self.db)

		self.auth.update(TokenExpirado)
		
		project_id = self.project_2.id
		ticket = schemas.TicketByTitle(
			title = "formularios"
		)

		self.headers.update(self.auth)

		response = client.get(
			f"{self.url}/project/{project_id}/ticket",
			headers = self.headers,
			params = ticket.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseTokenNoValido


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_ticket(self, mockToken):
		"""
			Validar actualizar un ticket
		"""
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)
		
		ticket_id = self.ticket.id
		old_ticket = self.ticket

		ticket = schemas.TicketUpdate(
			title = "Pruebas tests",
			priority = "alta"
		)

		response = client.put(
			f"{self.url}/{ticket_id}",
			headers = self.headers,
			json = ticket.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["id"] ==  ticket_id
		assert responseJson["title"] == ticket.title
		assert responseJson["priority"] == ticket.priority

		assert responseJson["title"] != old_ticket.title 
		assert responseJson["priority"] != old_ticket.priority.name


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_ticket_with_no_existent_ticket(self, mockToken):
		"""
			Intentar actualizar un ticket, pero 
			con un ID que no existe
		"""
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		ticket_id = 2

		ticket = schemas.TicketUpdate(
			title = "Pruebas tests",
			priority = "alta"
		)

		response = client.put(
			f"{self.url}/{ticket_id}",
			headers = self.headers,
			json = ticket.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 404
		assert responseJson == {"message": DoesNotExistsTicket.get(id = ticket_id)}


	@pytest.mark.parametrize("options, error", [
		(
			{"option": {"priority": "ahora"}},
			"Input error: ahora"
		),
		(
			{"option": {"state": "fin"}},
			"Input error: fin"
		),
		(
			{"option": {"type": "eliminado"}},
			"Input error: eliminado"
		)

	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_ticket_with_wrong_options(self, mockToken, options, error):
		"""
			Intentar actualizar un ticket, pero
			enviando valores incorrectos para:
			priority - state- type
		"""

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		ticket_id = self.ticket.id

		response = client.put(
			f"{self.url}/{ticket_id}",
			headers = self.headers,
			json = options["option"]
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson["detail"] == error


	@pytest.mark.parametrize("update_ticket, error", [
		(
			{
				"title": """
				Lorem ipsum dolor sit amet consectetur adipisicing elit. 
				Aspernatur, magni nostrum est deserunt officia quas illo quis, 
				aliquam unde animi quod debitis voluptates recusandae ut minima, 
				eos dicta molestiae accusamus?
				"""
			},
			"El titulo es demasiado largo, debe ser menor o igual a 30 caracteres"
		),
		(
			{"title": "App"},
			"El titulo es demasiado corto, debe ser mayor o igual a 5 caracteres"
		)

	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_ticket_with_wrong_title(self, mockToken, update_ticket, error):
		"""
			Intentar actualizar un ticket, pero
			enviando un valor para el titulo muy
			largo o muy corto
		"""
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		ticket_id = self.ticket.id

		response = client.put(
			f"{self.url}/{ticket_id}",
			headers = self.headers,
			json = update_ticket
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson["message"] == error


	@pytest.mark.parametrize("update_ticket, error", [
		(
			{"description": "Info"},
			"La descripción es demasiado corto, debe ser mayor o igual a 5 caracteres"
		),
		(
			{
				"description": """
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
			},
			"La descripción  es demasiado largo, debe ser menor o igual a 200 caracteres"
		)

	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_ticket_with_wrong_description(self, mockToken, update_ticket, error):
		"""
			Intentar actualizar un ticket, pero
			enviando un valor para la descripción muy
			larga o muy corta
		"""
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		ticket_id = self.ticket.id

		response = client.put(
			f"{self.url}/{ticket_id}",
			headers = self.headers,
			json = update_ticket
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson["message"] == error


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_ticket_with_nothing(self, mockToken):
		"""
			Intentar actualizar un ticket, pero
			sin enviar algun valor para actualizar
		"""

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		ticket_id = self.ticket.id
		old_ticket = self.ticket

		response = client.put(
			f"{self.url}/{ticket_id}",
			headers = self.headers,
			json = {}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 400
		assert responseJson == {"message": EmptyValues.get()}


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_update_ticket_without_authorization(self):
		"""
			Intentar actualizar un ticket, pero
			sin enviar un token de autorización
		"""
		ticket_id = self.ticket.id
		ticket = schemas.TicketUpdate(
			priority = "alta"
		)

		response = client.put(
			f"{self.url}/{ticket_id}",
			headers = self.headers,
			json = ticket.model_dump()
		)
		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseNoToken


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_update_ticket_with_expired_token(self):
		"""
			Intentar actualizar un ticket, pero
			enviando un token expirado
		"""
		self.auth.update(TokenExpirado)

		self.headers.update(self.auth)

		ticket_id = self.ticket.id
		ticket = schemas.TicketUpdate(
			priority = "alta"
		)

		response = client.put(
			f"{self.url}/{ticket_id}",
			headers = self.headers,
			json = ticket.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseTokenNoValido


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_delete_ticket(self, mockToken):
		"""
			Validar que se elimine un ticket
		"""
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		ticket_id = self.ticket.id

		response = client.delete(
			f"{self.url}/{ticket_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code

		assert responseStatus == 204


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_delete_ticket_with_no_existent_ticket(self, mockToken):
		"""
			Intentar eliminar un ticket, pero
			con un ID que no existe
		"""

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		ticket_id = 3

		response = client.delete(
			f"{self.url}/{ticket_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 404
		assert responseJson == {"message": DoesNotExistsTicket.get(id = ticket_id)}


	@pytest.mark.parametrize("ticket_id", [
		"abc32",
		None,
		1.5,
	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_delete_ticket_with_wrong_ticket_id(self, mockToken, ticket_id):
		"""
			Intentar eliminar un ticket, pero
			enviando un valor incorrecto para 'ticket_id'
		"""
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		response = client.delete(
			f"{self.url}/{ticket_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		
		assert responseStatus == 422


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_delete_ticket_without_autorization(self):
		"""
			Intentar eliminar un ticket, pero
			sin enviar un token de validación
		"""
		ticket_id = self.ticket.id

		response = client.delete(
			f"{self.url}/{ticket_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseNoToken


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_delete_ticket_with_token_expired(self):
		"""
			Intentar eliminar un ticket, pero
			enviando un token expirado
		"""
		self.auth.update(TokenExpirado)
		self.headers.update(self.auth)

		ticket_id = self.ticket.id

		response = client.delete(
			f"{self.url}/{ticket_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseTokenNoValido


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_ticket_history_by_ticket(self, mockToken):
		"""
			Validar obtener el listado de cambios
			de un ticket
		"""
		ticket_id = self.ticket.id
		create_ticket_histories(db = self.db, ticket_id = ticket_id)
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		response = client.get(
			f"{self.url}/{ticket_id}/history",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] == None
		assert responseJson["current"] == 1
		assert responseJson["next"] == None
		assert responseJson["ticket"]["id"] == ticket_id
		assert responseJson["content"]["total"] == 4
		assert responseJson["content"]["histories"]
		assert len(responseJson["content"]["histories"]) == 4
		assert responseJson["content"]["histories"][0]["state"] == StateTicketHistory.crear.name
		assert responseJson["content"]["histories"][1]["state"] == StateTicketHistory.actualizar.name


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_ticket_history_by_ticket_with_no_existent_ticket(self, mockToken):
		"""
			Intenatr obtener el listado de cambios
			de un ticket, pero enviando el ID de un ticket
			que no existe
		"""
		ticket_id = 100
		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		response = client.get(
			f"{self.url}/{ticket_id}/history",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 404
		assert responseJson == {"message": DoesNotExistsTicket.get(id = ticket_id)}



	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_ticket_history_by_ticket_checking_pagination(self, mockToken):
		"""
			Validar obtener el listado de cambios
			de un ticket, y verificando el funcionamiento
			de la paginación
		"""
		ticket_id = self.ticket.id
		create_ticket_histories(db = self.db, ticket_id = ticket_id)
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		pageSize = 2
		response = client.get(
			f"{self.url}/{ticket_id}/history",
			headers = self.headers,
			params = {
				"pageSize": pageSize
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] == None
		assert responseJson["current"] == 1
		assert responseJson["next"] != None
		assert responseJson["ticket"]["id"] == ticket_id
		assert responseJson["content"]["total"] == 4
		assert responseJson["content"]["histories"]
		assert len(responseJson["content"]["histories"]) == 2


		page = 2
		response = client.get(
			responseJson["next"],
			headers = self.headers,
			params = {
				"page": page,
				"pageSize": pageSize
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] != None
		assert responseJson["current"] == page
		assert responseJson["next"] == None
		assert responseJson["ticket"]["id"] == ticket_id
		assert responseJson["content"]["total"] == 4
		assert responseJson["content"]["histories"]
		assert len(responseJson["content"]["histories"]) == 2


	@pytest.mark.parametrize("pagination, error", [
		(
			{"page": 1, "pageSize": -5},
			"Input should be greater than or equal to 1"
		),
		(
			{"page": -1, "pageSize": 5},
			"Input should be greater than or equal to 1"
		),
		(
			{"page": 1, "pageSize": 5.2},
			"Input should be a valid integer, unable to parse string as an integer"
		),
		(
			{"page": 1.2, "pageSize": 5},
			"Input should be a valid integer, unable to parse string as an integer"
		),
		(
			{"page": 0, "pageSize": 5},
			"Input should be greater than or equal to 1"
		),
		(
			{"page": 1, "pageSize": 25},
			"Input should be less than or equal to 20"
		),
	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_ticket_history_by_ticket_with_wron_value_pagination(self, mockToken, pagination, error):
		"""
			Intentar obtener el listado de cambios
			de un ticket, pero enviando valores 
			incorrectos (decimales, negativos y mayores o
			menores al limite definido) para la paginación
		"""
		ticket_id = self.ticket.id
		create_ticket_histories(db = self.db, ticket_id = ticket_id)
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		response = client.get(
			f"{self.url}/{ticket_id}/history",
			headers = self.headers,
			params = pagination
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422
		assert responseJson["message"] == error


	@patch("apps.tickets.commands.commands.get_db", get_db)	
	def test_route_ticket_history_by_ticket_without_authorization(self):
		"""
			Intentar obtener el listado de cambios
			de un ticket, pero sin enviar un token de
			autenticación
		"""
		ticket_id = self.ticket.id
		create_ticket_histories(db = self.db, ticket_id = ticket_id)

		response = client.get(
			f"{self.url}/{ticket_id}/history",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseNoToken


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_ticket_history_by_ticket_with_expired_token(self):
		"""
			Intentar obtener el listado de cambios
			de un ticket, pero enviando un token expirado
		"""
		ticket_id = self.ticket.id
		create_ticket_histories(db = self.db, ticket_id = ticket_id)

		self.headers.update(TokenExpirado)

		response = client.get(
			f"{self.url}/{ticket_id}/history",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseTokenNoValido


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_history(self, mockToken):
		"""
			Validar obtener el detalle de historial
			de cambios de un ticket
		"""
		create_ticket_histories(db = self.db, ticket_id = self.ticket.id)
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		history_id = 1
		ticket_id = self.ticket.id
		response = client.get(
			f"{self.url}/history/{history_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["id"] == history_id 
		assert responseJson["ticket"]["id"] == ticket_id
		assert responseJson["state"] == StateTicketHistory.crear.name

		history_id = 2
		response = client.get(
			f"{self.url}/history/{history_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["id"] == history_id 
		assert responseJson["ticket"]["id"] == ticket_id
		assert responseJson["state"] == StateTicketHistory.actualizar.name


	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_history_with_no_existent_ticket_history(self, mockToken):
		"""
			Intentar obtener el detalle de historial
			de cambios de un ticket, pero con ID de historial
			que no existe
		"""
		create_ticket_histories(db = self.db, ticket_id = self.ticket.id)
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		history_id = 100
		ticket_id = self.ticket.id
		response = client.get(
			f"{self.url}/history/{history_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 404
		assert responseJson == {"message": DoesNotExistsTicketHistory.get(id = history_id)}


	@pytest.mark.parametrize("history_id", [
		"abcs12",
		12.45,
		None
	])
	@patch("apps.tickets.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_ticket_history_with_wrong_history_id(self, mockToken, history_id):
		"""
			Intentar obtener el detalle de historial
			de cambios de un ticket, pero enviando un valor
			incorrecto para 'history_id'
		"""
		create_ticket_histories(db = self.db, ticket_id = self.ticket.id)
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)
		response = client.get(
			f"{self.url}/history/{history_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 422


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_get_ticket_history_without_authorization(self):
		"""
			Intentar obtener el detalle de historial
			de cambios de un ticket, pero sin enviar un
			token de autenticación
		"""
		create_ticket_histories(db = self.db, ticket_id = self.ticket.id)
		history_id = 1

		response = client.get(
			f"{self.url}/history/{history_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseNoToken


	@patch("apps.tickets.commands.commands.get_db", get_db)
	def test_route_get_ticket_history_with_token_expired(self):
		"""
			Intentar obtener el detalle de historial
			de cambios de un ticket, pero enviando un 
			token expirado
		"""
		create_ticket_histories(db = self.db, ticket_id = self.ticket.id)
		history_id = 1
		self.headers.update(TokenExpirado)
		
		response = client.get(
			f"{self.url}/history/{history_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseTokenNoValido