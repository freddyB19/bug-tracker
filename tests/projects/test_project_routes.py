import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient

from tests import ENGINE
from tests import get_db
from tests import SESSION
from tests.projects import set_project
from tests.projects import set_project_schema

from main import app
from apps import Model
from apps.users.models import User
from apps.projects.models import Project
from apps.projects.schemas import schemas
from apps.projects.models import ChoicesPrority

from apps.projects.commands.utils.error_messages import (
	InvalidPriority,
	UnauthorizedProject,
	DoesNotExistsProject
)

from apps.users.commands.utils.error_messages import DoesNotExistsUser


ResponseNoToken = {"detail": "Ausencia del token en la cabecera"}
TokenExpirado = {
	"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
ResponseTokenNoValido = {"detail": "Token no valido"}

client = TestClient(app)


class TestRoutesProject:

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

		self.user = user

		project = set_project(user_id = self.user.id)
		
		self.db.add(project)
		self.db.commit()
		self.db.refresh(project)

		self.project = project

		self.url = "/project"
		self.headers = {"Content-Type": "application/json"}
		self.auth = {"Authorization": "Bearer token-key"}


	def teardown_method(self):
		self.db.rollback()
		self.db.close()

	def test_data_in_db(self):
		"""
			Validar que se hayan guradado los datos en la DB
		"""
		assert self.db.query(Project).count() == 1


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_project(self, mockToken):
		""" 
			Validar ruta para crear un proyecto
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project = set_project_schema(
			title = "Proyecto App a",
			description = "Una app movil",
			user_id = self.user.id
		)

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = project.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 201
		assert responseJson["id"] == 2
		assert responseJson["title"] == project.title
		assert responseJson["user"]["id"] == project.user_id
		assert responseJson["priority"] == project.priority

	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_project_without_title(self, mockToken):
		"""
			Intentar crear proyecto sin titulo
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"priority": "normal",
				"user_id": self.user.id,
				"description": "la descripción de un proyecto"
			}
		)

		responseStatus = response.status_code

		assert responseStatus == 422


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_project_with_too_long_title(self, mockToken):
		"""
			Intentar crear proyecto con titulo muy largo
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		title = """ 
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus
		"""

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"title": title,
				"priority": "normal",
				"user_id": self.user.id,
				"description": "la descripción de un proyecto"
			}
		)

		responseStatus = response.status_code

		assert responseStatus == 422
		

	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_project_with_too_short_title(self, mockToken):
		"""
			Intentar crear proyecto con titulo muy corto
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		title = "App"

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"title": title,
				"priority": "normal",
				"user_id": self.user.id,
				"description": "la descripción de un proyecto"
			}
		)

		responseStatus = response.status_code

		assert responseStatus == 422


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_project_without_description(self, mockToken):
		"""
			Intentar crear proyecto sin descripción
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"priority": "normal",
				"title": "Una nueva App",
				"user_id": self.user.id
			}
		)

		responseStatus = response.status_code

		assert responseStatus == 422


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_project_with_too_long_description(self, mockToken):
		"""
			Intentar crear proyecto con una descripción muy larga
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

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
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		"""

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"priority": "normal",
				"user_id": self.user.id,
				"title": "Una nueva App",
				"description": description
			}
		)

		responseStatus = response.status_code

		assert responseStatus == 422


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_project_with_too_short_description(self, mockToken):
		"""
			Intentar crear proyecto con una descripción muy corta
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		description = "App"

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"priority": "normal",
				"user_id": self.user.id,
				"title": "Una nueva App",
				"description": description
			}
		)

		responseStatus = response.status_code
 
		assert responseStatus == 422


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_project_with_wrong_priority(self, mockToken):
		"""
			Intentar crear proyecto con una prioridad incorrecta
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		priority = "ahora"

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"priority": priority,
				"user_id": self.user.id,
				"title": "Una nueva App",
				"description": "descripción de una app"
			}
		)

		responseStatus = response.status_code

		assert responseStatus == 422
		

	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_project_with_no_existent_user(self, mockToken):
		"""
			Intentar crear proyecto con el ID de un usuario
			que no existe
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		user_id = 100

		project = set_project_schema(
			user_id = user_id,
			priority = "normal",
			title = "Una nueva App",
			description = "descripción de una app",
		)

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = project.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 404
		assert responseJson == {"message": DoesNotExistsUser.get(id = project.user_id)}


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_create_project_without_user_id(self, mockToken):
		"""
			Intentar crear proyecto pero sin enviar 
			el ID de un usuario
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = {
				"priority": "normal",
				"title": "Una nueva App",
				"description": "descripción de una app"
			}
		)

		responseStatus = response.status_code

		assert responseStatus == 422

	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_route_create_project_without_authorization(self):
		"""
			Intentar crear proyecto, pero sin un token
			de autenticación
		"""
		project = set_project_schema(
			title = "Proyecto App a",
			description = "Una app movil",
			user_id = self.user.id
		)

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = project.model_dump()
		)
		
		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseNoToken


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_route_create_project_with_token_expired(self):
		"""
			Intentar crear proyecto, pero con un token
			expirado
		"""
		self.headers.update(TokenExpirado)

		project = set_project_schema(
			title = "Proyecto App a",
			description = "Una app movil",
			user_id = self.user.id
		)

		response = client.post(
			f"{self.url}",
			headers = self.headers,
			json = project.model_dump()
		)
		
		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseTokenNoValido


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_project_by_id(self, mockToken):
		"""
			Obtener proyecto por ID
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = self.project.id

		response = client.get(
			f"{self.url}/{project_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["id"] == self.project.id
		assert responseJson["title"] == self.project.title
		assert responseJson["description"] == self.project.description
		assert responseJson["priority"] == self.project.priority.name
		assert responseJson["user"]["id"] == self.project.user_id


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_not_existent_project(self, mockToken):
		"""
			Intentar obtener un proyecto que no existe 
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = 100

		response = client.get(
			f"{self.url}/{project_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 404
		assert responseJson == {"message": DoesNotExistsProject.get(id = project_id)}


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_route_get_project_by_id_without_authorization(self):
		"""
			Intentar obtener un proyecto, pero sin
			enviar un token de autorización
		"""
		project_id = self.project.id

		response = client.get(
			f"{self.url}/{project_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()


		assert responseStatus == 401
		assert responseJson == ResponseNoToken

	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_route_get_project_by_id_with_token_expired(self):
		"""
			Intentar obtener un proyecto, pero
			envinado un token expirado
		"""
		self.headers.update(TokenExpirado)
		project_id = self.project.id

		response = client.get(
			f"{self.url}/{project_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()
		
		assert responseStatus == 401
		assert responseJson == ResponseTokenNoValido


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_project(self, mockToken):
		"""
			Validar que se actualice un proyecto
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = 1

		infoUpdate = schemas.ProjectUpdate(
			title = "Actualizando el titulo",
			description = "Actualizando el la descripción",
			user_id = self.user.id,
			priority = "baja"
		)

		response = client.put(
			f"{self.url}/{project_id}",
			headers = self.headers,
			json = infoUpdate.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["id"] == self.project.id
		assert responseJson["title"] != self.project.title
		assert responseJson["description"] != self.project.description
		assert responseJson["priority"] != self.project.priority.name

		assert responseJson["title"] == infoUpdate.title
		assert responseJson["description"] == infoUpdate.description
		assert responseJson["priority"] == infoUpdate.priority


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_no_existent_project(self, mockToken):
		"""
			Intentar actualizar un proyecto que no existe
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = 100

		infoUpdate = schemas.ProjectUpdate(
			title = "Actualizando el titulo",
			description = "Actualizando el la descripción",
			user_id = self.user.id,
			priority = "baja"
		)

		response = client.put(
			f"{self.url}/{project_id}",
			headers = self.headers,
			json = infoUpdate.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 404
		assert responseJson == {"message": DoesNotExistsProject.get(id = project_id)}


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_project_with_too_long_title(self, mockToken):
		"""
			Intentar actualizar el titulo de un proyecto
			con un valor largo
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = 1
		
		title = """
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		"""

		response = client.put(
			f"{self.url}/{project_id}",
			headers = self.headers,
			json = {
				"title": title,
				"description": "Actualizando el la descripción",
				"user_id": self.user.id,
				"priority": "baja",

			}
		)

		responseStatus = response.status_code

		assert responseStatus == 422


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_project_with_too_short_title(self, mockToken):
		"""
			Intentar actualizar el titulo de un proyecto
			con un valor corto
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = 1
		title = "App"

		response = client.put(
			f"{self.url}/{project_id}",
			headers = self.headers,
			json = {
				"title": title,
				"description": "Actualizando el la descripción",
				"user_id": self.user.id,
				"priority": "baja",

			}
		)

		responseStatus = response.status_code

		assert responseStatus == 422


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_project_only_title(self, mockToken):
		"""
			Intentar actualizar solo el titulo de un proyecto
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = 1

		response = client.put(
			f"{self.url}/{project_id}",
			headers = self.headers,
			json = {
				"title": "Actualizando el titulo",
				"user_id": self.user.id,
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()


		assert responseStatus == 200
		assert responseJson["id"] == self.project.id
		assert responseJson["title"] != self.project.title
		assert responseJson["description"] == self.project.description
		assert responseJson["priority"] == self.project.priority.name



	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_project_with_too_long_description(self, mockToken):
		"""
			Intentar actualizar la descripción de un proyecto
			con un valor largo
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = 1

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

		response = client.put(
			f"{self.url}/{project_id}",
			headers = self.headers,
			json = {
				"title": "Actualizando el titulo",
				"description": description,
				"user_id": self.user.id,
				"priority": "baja",

			}
		)

		responseStatus = response.status_code
		
		assert responseStatus == 422


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_project_with_too_short_description(self, mockToken):
		"""
			Intentar actualizar la descripción de un proyecto
			con un valor corto
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = 1

		description = "app"

		response = client.put(
			f"{self.url}/{project_id}",
			headers = self.headers,
			json = {
				"title": "Actualizando el titulo",
				"description": description,
				"user_id": self.user.id,
				"priority": "baja",

			}
		)

		responseStatus = response.status_code
		
		assert responseStatus == 422


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_project_only_description(self, mockToken):
		"""
			Intentar actualizar solo la descripción un proyecto
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = 1

		response = client.put(
			f"{self.url}/{project_id}",
			headers = self.headers,
			json = {
				"description": "Actualizando la descripción",
				"user_id": self.user.id,
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["id"] == self.project.id
		assert responseJson["description"] != self.project.description
		assert responseJson["title"] == self.project.title
		assert responseJson["priority"] == self.project.priority.name


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_project_with_wrong_priority(self, mockToken):
		"""
			Intentar actualizar un proyecto
			con la priorida incorrecta
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = 1

		priority = "ahora"

		response = client.put(
			f"{self.url}/{project_id}",
			headers = self.headers,
			json = {
				"title": "Actualizando el titulo",
				"description": "Actualizando la descripción",
				"user_id": self.user.id,
				"priority": priority
			}
		)

		responseStatus = response.status_code

		assert responseStatus == 422


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_project_with_only_priority(self, mockToken):
		"""
			Intentar actualizar solo la prioridad de un proyecto
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = 1

		response = client.put(
			f"{self.url}/{project_id}",
			headers = self.headers,
			json = {
				"user_id": self.user.id,
				"priority": "alta"
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["id"] == self.project.id
		assert responseJson["priority"] != self.project.priority.name
		assert responseJson["title"] == self.project.title
		assert responseJson["description"] == self.project.description


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_project_with_no_existent_user(self, mockToken):
		"""
			Intentar actualizar un proyecto con un usuario que
			no existe
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = 1

		user_id = 100

		response = client.put(
			f"{self.url}/{project_id}",
			headers = self.headers,
			json = {
				"title": "Actualizando el titulo",
				"description": "Actualizando la descripción",
				"user_id": user_id,
				"priority": "baja"
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == {"message": UnauthorizedProject.get(id = project_id)}


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_update_project_with_unauthorized_user(self, mockToken):
		"""
			Intentar actualizar un proyecto que no le pertenece al
			usuario
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		alejandro = User(
			name = 'alejandro',
			email = 'alejandro@gmail.com',
			username = 'alejandro19',
			password = '12345'
		)

		self.db.add(alejandro)
		self.db.commit()
		self.db.refresh(alejandro)

		project_id = 1

		user_id = alejandro.id

		response = client.put(
			f"{self.url}/{project_id}",
			headers = self.headers,
			json = {
				"title": "Actualizando el titulo",
				"description": "Actualizando la descripción",
				"user_id": user_id,
				"priority": "baja"
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == {"message": UnauthorizedProject.get(id = project_id)}


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_route_update_project_without_authorization(self):
		"""
			Intentar actualizar un proyecto, pero sin 
			enviar un token de autorización
		"""
		project_id = 1

		infoUpdate = schemas.ProjectUpdate(
			title = "Actualizando el titulo",
			description = "Actualizando el la descripción",
			user_id = self.user.id,
			priority = "baja"
		)

		response = client.put(
			f"{self.url}/{project_id}",
			headers = self.headers,
			json = infoUpdate.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseNoToken


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_route_update_project_with_token_expired(self):
		"""
			Intentar actualizar un proyecto, pero
			enviando un token expirado
		"""
		self.headers.update(TokenExpirado)
		project_id = 1

		infoUpdate = schemas.ProjectUpdate(
			title = "Actualizando el titulo",
			description = "Actualizando el la descripción",
			user_id = self.user.id,
			priority = "baja"
		)

		response = client.put(
			f"{self.url}/{project_id}",
			headers = self.headers,
			json = infoUpdate.model_dump()
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseTokenNoValido


	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_delete_project(self, mockToken):
		"""
			Validar que se ha eliminado un proyecto
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = 1

		response = client.delete(
			f"{self.url}/{project_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code

		assert responseStatus == 204

	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_delete_no_existent_project(self, mockToken):
		"""
			Intentar eliminar un proyecto que no existe
		"""
		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		project_id = 100

		response = client.delete(
			f"{self.url}/{project_id}",
			headers = self.headers,
		)
		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 404
		assert responseJson == {"message": DoesNotExistsProject.get(id = project_id)}


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_route_delete_project_without_authorization(self):
		"""
			Intentar eliminar un proyecto, pero sin
			un token de autenticación
		"""
		project_id = 1

		response = client.delete(
			f"{self.url}/{project_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseNoToken


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_route_delete_project_with_token_expired(self):
		"""
			Intentar eliminar un proyecto, pero
			enviando un token expirado
		"""
		self.headers.update(TokenExpirado)
		project_id = 1

		response = client.delete(
			f"{self.url}/{project_id}",
			headers = self.headers,
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseTokenNoValido


	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_projects_by_user(self, mockToken):
		""" Validar obtener projectos por usuario """

		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		page = 1
		pageSize = 2
		user_id = 1

		proyecto_b = set_project(
			title = "Proyecto B",
			description = "Descripción del proyecto B",
			user_id = user_id
		)

		proyecto_c = set_project(
			title = "Proyecto C",
			description = "Descripción del proyecto C",
			user_id = user_id
		)

		self.db.add_all([proyecto_b, proyecto_c])
		self.db.commit()

		user = self.db.get(User, user_id)
		"""
		Esta consulta debe estar simpre después de un db.refresh(...)
		ya que sino es así, puede generar un error de instancia.
		Pero, este error solo se debe al comportamiento de la 
		instancia Session durante el test, no por otra razón. 
		"""

		response = client.get(
			f"{self.url}/list/user",
			headers = self.headers,
			params = {
				"page": page,
				"pageSize": pageSize,
				"user_id": user_id
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()
		
		assert responseStatus == 200
		assert "previous" in responseJson.keys()
		assert "current"  in responseJson.keys()
		assert "next" in responseJson.keys()
		assert responseJson["previous"] is None
		assert responseJson["next"] is not None
		assert responseJson["current"] == page
		assert responseJson["user"]["id"] == user.id
		assert responseJson["user"]["name"] == user.name
		assert "total" in responseJson["content"].keys()
		assert "projects" in responseJson["content"].keys()
		assert responseJson["content"]["total"] == 3
		assert len(responseJson["content"]["projects"]) == 2

		page = 2
		
		response = client.get(
			f"{responseJson['next']}",
			headers = self.headers,
			params = {
				"page": page,
				"pageSize": pageSize,
				"user_id": user_id
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] is not None
		assert responseJson["next"] is None
		assert responseJson["current"] == page
		assert responseJson["user"]["id"] == 1
		assert responseJson["user"]["name"] == "bolivar"
		assert "total" in responseJson["content"].keys()
		assert "projects" in responseJson["content"].keys()
		assert responseJson["content"]["total"] == 3
		assert len(responseJson["content"]["projects"]) == 1

	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_projects_user_with_filter(self, mockToken):
		""" 
			Obtener proyectos por usuario pero, 
			aplicando filtrado por prioridad del proyecto.
		"""

		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		page = 1
		pageSize = 5
		user_id = 1

		project1 = set_project(
			title = "Videojuego de Arcade",
			priority = "baja",
			description = "desarrollar un videojuego",
			user_id = user_id

		)

		project2 = set_project(
			title = "App de mensajeria",
			priority = "baja",
			description = "aplicación movil de mensajes",
			user_id = user_id

		)

		project3 = set_project(
			title = "Traductor AI",
			priority = "alta",
			description = "una app que usa la IA para traducir",
			user_id = user_id
		)

		self.db.add_all([project1, project2, project3])
		self.db.commit()


		# Filter: priority = "baja"
		
		priority = "baja"

		response = client.get(
			f"{self.url}/list/user",
			headers = self.headers,
			params = {
				"page": page,
				"pageSize": pageSize,
				"user_id": user_id,
				"priority": priority
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] is None
		assert responseJson["next"] is None
		assert responseJson["current"] == page
		assert responseJson["user"]["id"] == 1
		assert responseJson["user"]["name"] == "bolivar"
		assert "total" in responseJson["content"].keys()
		assert "projects" in responseJson["content"].keys()
		assert responseJson["content"]["total"] == 2
		assert responseJson["content"]["projects"]
		assert len(responseJson["content"]["projects"]) == 2

		
		# Filter: priority = "alta"
		
		priority = "alta"

		response = client.get(
			f"{self.url}/list/user",
			headers = self.headers,
			params = {
				"page": page,
				"pageSize": pageSize,
				"user_id": user_id,
				"priority": priority
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] is None
		assert responseJson["next"] is None
		assert responseJson["current"] == page
		assert responseJson["user"]["id"] == 1
		assert responseJson["user"]["name"] == "bolivar"
		assert "total" in responseJson["content"].keys()
		assert "projects" in responseJson["content"].keys()
		assert responseJson["content"]["total"] == 1
		assert responseJson["content"]["projects"]
		assert len(responseJson["content"]["projects"]) == 1

		
		# Filter: priority = "normal"

		priority = "normal"

		response = client.get(
			f"{self.url}/list/user",
			headers = self.headers,
			params = {
				"page": page,
				"pageSize": pageSize,
				"user_id": user_id,
				"priority": priority
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] is None
		assert responseJson["next"] is None
		assert responseJson["current"] == page
		assert responseJson["user"]["id"] == 1
		assert responseJson["user"]["name"] == "bolivar"
		assert "total" in responseJson["content"].keys()
		assert "projects" in responseJson["content"].keys()
		assert responseJson["content"]["total"] == 1
		assert responseJson["content"]["projects"]
		assert len(responseJson["content"]["projects"]) == 1

		
		# Filter: priority = "inmediata"

		priority = "inmediata"
		
		response = client.get(
			f"{self.url}/list/user",
			headers = self.headers,
			params = {
				"page": page,
				"pageSize": pageSize,
				"user_id": user_id,
				"priority": priority
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] is None
		assert responseJson["next"] is None
		assert responseJson["current"] == page
		assert responseJson["user"]["id"] == 1
		assert responseJson["user"]["name"] == "bolivar"
		assert "total" in responseJson["content"].keys()
		assert "projects" in responseJson["content"].keys()
		assert responseJson["content"]["total"] == 0
		assert not responseJson["content"]["projects"]
		assert len(responseJson["content"]["projects"]) == 0


	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_projects_user_with_wrong_filter_value(self, mockToken):
		""" 
			Obtener proyectos por usuario pero, 
			aplicando un valor de filtrado incorrecto.
		"""

		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		page = 1
		pageSize = 5
		user_id = 1
		priority = "ahora"

		response = client.get(
			f"{self.url}/list/user",
			headers = self.headers,
			params = {
				"page": page,
				"pageSize": pageSize,
				"user_id": user_id,
				"priority": priority
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()


		assert responseStatus == 422
		

	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_projects_by_user_with_too_hight_page(self, mockToken):
		""" 
			Obtener proyectos por usuario, pero
			accediendo una página muy alta
		"""

		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)
		
		page = 15
		pageSize = 2
		user_id = 1

		user = self.db.get(User, user_id)

		response = client.get(
			f"{self.url}/list/user",
			headers = self.headers,
			params = {
				"page": page,
				"pageSize": pageSize,
				"user_id": user_id
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] is None
		assert responseJson["next"] is None
		assert responseJson["current"] == page
		assert responseJson["user"]["id"] == user.id
		assert responseJson["user"]["name"] == user.name
		assert responseJson["content"]["total"] == 1
		assert len(responseJson["content"]["projects"]) == 0


	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_projects_by_user_without_page_and_pageSize(self, mockToken):
		""" 
			Obtener proyectos por usuario, pero
			sin pasar como parametro 'page' y 'pageSize'
		"""

		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)

		user_id = 1

		user = self.db.get(User, user_id)

		response = client.get(
			f"{self.url}/list/user",
			headers = self.headers,
			params = {
				"user_id": user_id
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 200
		assert responseJson["previous"] is None
		assert responseJson["next"] is None
		assert responseJson["current"] == 1
		assert responseJson["user"]["id"] == user.id
		assert responseJson["user"]["name"] == user.name
		assert responseJson["content"]["total"] == 1
		assert len(responseJson["content"]["projects"]) == 1


	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_projects_by_user_with_page_and_pageSize_negative(self, mockToken):
		""" 
			Obtener proyectos por usuario, pero
			definiendo un número de página y de tamaño de página negativos
		"""

		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)
		
		page = -1
		pageSize = -2
		user_id = 1

		user = self.db.get(User, user_id)

		response = client.get(
			f"{self.url}/list/user",
			headers = self.headers,
			params = {
				"page": page,
				"pageSize": pageSize,
				"user_id": user_id
			}
		)

		responseStatus = response.status_code

		assert responseStatus == 422


	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.projects.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_route_get_projects_with_no_existent_user_(self, mockToken):
		""" 
			Obtener proyectos por usuario, pero
			con un ID de usuario que no existe.
		"""

		mockToken.result_value.state.result_value = True
		
		self.headers.update(self.auth)
		
		page = 1
		pageSize = 5
		user_id = 100

		response = client.get(
			f"{self.url}/list/user",
			headers = self.headers,
			params = {
				"page": page,
				"pageSize": pageSize,
				"user_id": user_id
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 404
		assert responseJson == {"message": DoesNotExistsUser.get(id = user_id)}

	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_route_get_projects_by_user_without_authorization(self):
		"""
			Obtener proyectos por usuario, pero
			sin enviar un token de autorización
		"""
		user_id = 1

		proyecto_b = set_project(
			title = "Proyecto B",
			description = "Descripción del proyecto B",
			user_id = user_id
		)

		proyecto_c = set_project(
			title = "Proyecto C",
			description = "Descripción del proyecto C",
			user_id = user_id
		)

		self.db.add_all([proyecto_b, proyecto_c])
		self.db.commit()

		user = self.db.get(User, user_id)

		response = client.get(
			f"{self.url}/list/user",
			headers = self.headers,
			params = {
				"user_id": user_id
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseNoToken


	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_route_get_projects_by_user_with_token_expired(self):
		"""
			Obtener proyectos por usuario, pero
			enviando un token expirado
		"""
		self.headers.update(TokenExpirado)

		user_id = 1

		proyecto_b = set_project(
			title = "Proyecto B",
			description = "Descripción del proyecto B",
			user_id = user_id
		)

		proyecto_c = set_project(
			title = "Proyecto C",
			description = "Descripción del proyecto C",
			user_id = user_id
		)

		self.db.add_all([proyecto_b, proyecto_c])
		self.db.commit()

		user = self.db.get(User, user_id)

		response = client.get(
			f"{self.url}/list/user",
			headers = self.headers,
			params = {
				"user_id": user_id
			}
		)

		responseStatus = response.status_code
		responseJson = response.json()

		assert responseStatus == 401
		assert responseJson == ResponseTokenNoValido