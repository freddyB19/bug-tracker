import pytest
from  unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests import ENGINE
from tests import SESSION
from tests import get_db

from apps import Model
from apps.users.models import User
from apps.users.routes import router
from apps.users.schemas import schemas
from apps.users.commands.utils.password import HashPassword
from apps.users.commands.utils.password import ValidateHashedPassword
from apps.users.commands.utils.error_messages import (
	EmailORUsernameInvalid,
	DoesNotExistsUser,
	EmailUnchanged,
	EmailAlreadyExists,
	UsernameAlreadyExists,
	UsernamelUnchanged,
	InvalidCredentials,
	InvalidCredentialsNoEmail,
	SerializerUser
)


app = FastAPI()

app.include_router(router)

client = TestClient(app)


NAME = "Freddy"
EMAIL = "freddy19@gmail.com"
USERNAME = "freddy19"
PASSWORD = "12345"

def set_new_user(name: str = None, email: str = None, username: str = None, password: str = None) -> User:
	set_name = name if name is not None else NAME
	set_email = email if email is not None else EMAIL
	set_username = username if username is not None else USERNAME
	set_password = password if password is not None else PASSWORD

	return User(
		name = set_name,
		username = set_username,
		email = set_email,
		password = HashPassword.getHash(password = set_password),
	)


def set_user_schema(name: str = None, email: str = None, username: str = None, password: str = None) -> schemas.UserRequest:
	set_name = name if name is not None else NAME
	set_email = email if email is not None else EMAIL
	set_username = username if username is not None else USERNAME
	set_password = password if password is not None else PASSWORD
	set_password_repeat = set_password


	return schemas.UserRequest(
		name = set_name,
		username = set_username ,
		email = set_email,
		password = set_password,
		password_repeat = set_password_repeat
	)

class TestRouterUser:

	def setup_method(self):
		Model.metadata.drop_all(ENGINE)
		Model.metadata.create_all(ENGINE)

		self.db = SESSION

		user = set_new_user()

		self.db.add(user)
		self.db.commit()

		self.url = "/user"
		self.headers = {"Content-Type": "application/json"}
		self.auth = {"Authorization": "Bearer token-key"}


	def teardown_method(self):
		self.db.rollback()
		self.db.close()


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_create_user(self):
		""" Validando ruta para crear un usuario"""

		request = set_user_schema(
			name = "marcelo",
			username = "marcelo19",
			email = "marcelo19@data.com",
			password = "12345",

		)

		response = client.post(
			f"{self.url}/",
			headers=self.headers,
			json = request.model_dump()
		)

		user = request.model_dump(exclude = ['password', 'password_repeat'])
		
		resultJson = response.json()
		
		assert response.status_code == 201
		assert resultJson['id'] == 2
		assert resultJson['name'] == user['name']
		assert resultJson['username'] == user['username']
		assert resultJson['email'] == user['email']


	@pytest.mark.parametrize("data_user", [
		set_user_schema(username = "bol19"),
		set_user_schema(email = "bol19@data.com")
	])
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_create_user_with_an_existing_email_or_username(self, data_user):
		""" Validar que no se cree un usuario con un email o username ya registrado """

		response = client.post(
			f"{self.url}/",
			headers = self.headers,
			json = data_user.model_dump()
		)

		resultJson = response.json()
		resultStatus = response.status_code

		assert resultStatus == 409
		assert resultJson == {"message": EmailORUsernameInvalid.get()}


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_get_user_by_id(self, mockToken):
		""" Validar obtener usuario por ID"""

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)
		
		response = client.get(f"{self.url}/{1}", headers = self.headers)

		resultJson = response.json()
		resultStatus = response.status_code

		user = set_new_user()

		assert resultStatus == 200
		assert resultJson['id'] == 1
		assert resultJson['name'] == user.name
		assert resultJson['username'] == user.username
		assert resultJson['email'] == user.email

	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_get_user_does_not_exists(self, mockToken):
		""" Obtener información de un usuario que no existe """

		mockToken.result_value.state.result_value = True

		self.headers.update(self.auth)

		user_id = 100

		response = client.get(f"{self.url}/{user_id}", headers = self.headers)

		resultJson = response.json()
		resultStatus = response.status_code

		assert resultStatus == 404
		assert resultJson == {"message": DoesNotExistsUser.get(id = user_id)}


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_delete_user(self, mockToken):
		""" Validar que se elimine un Usuario """

		mockToken.result_value.state.result_value = True
		self.headers.update(self.auth)

		user_id = 1

		response = client.delete(f"{self.url}/{user_id}", headers = self.headers)
		resultStatus = response.status_code

		assert resultStatus == 204


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_delete_user_does_not_exists(self, mockToken):
		""" """

		mockToken.result_value.state.result_value = True
		self.headers.update(self.auth)

		user_id = 100

		response = client.delete(f"{self.url}/{user_id}", headers = self.headers)

		resultStatus = response.status_code
		resultJson = response.json()


		assert resultStatus == 404
		assert resultJson == {"message": DoesNotExistsUser.get(id = user_id)}


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_update_email_user(self, mockToken):
		""" Validar actualización del 'email' del usuario """

		mockToken.result_value.state.result_value = True
		self.headers.update(self.auth)

		user_id = 1

		infoUdate = schemas.UserEmail(
			email = "bolivar19@gmail.com",
			password = "12345"
		)

		response = client.put(
			f"{self.url}/{user_id}/email", 
			headers = self.headers,
			json=infoUdate.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 200
		assert resultJson['id'] == user_id
		assert resultJson['email'] == infoUdate.email

	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_update_email_does_not_exists_user(self, mockToken):
		""" Actualizar el 'email' de un usuario que no existe """

		mockToken.result_value.state.result_value = True
		self.headers.update(self.auth)

		user_id = 100

		infoUdate = schemas.UserEmail(
			email = "bolivar19@gmail.com",
			password = "12345"
		)

		response = client.put(
			f"{self.url}/{user_id}/email", 
			headers = self.headers,
			json=infoUdate.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 404
		assert resultJson == {"message": DoesNotExistsUser.get(id = user_id)}

	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_update_email_with_existing_email(self, mockToken):
		""" Actualizar un 'email' con uno ya registrado """
		DATA_EMAIL = "bolivar19@data.com"

		user = set_new_user(email = DATA_EMAIL, username="bolivar19")

		self.db.add(user)
		self.db.commit()

		mockToken.result_value.state.result_value = True
		self.headers.update(self.auth)

		infoUdate = schemas.UserEmail(
			email = DATA_EMAIL,
			password = "12345"
		)

		user_id = 1

		response = client.put(
			f"{self.url}/{user_id}/email", 
			headers = self.headers,
			json=infoUdate.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 409
		assert resultJson == {"message": EmailAlreadyExists.get(email = infoUdate.email)}


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_update_email_unchanged(self, mockToken):
		""" 
			Intentar hacer una actualización del 'email' pero,
			sin hacer cambios. (Dejando el mismo 'email' que posee el usuario)
		"""
		mockToken.result_value.state.result_value = True
		self.headers.update(self.auth)

		data = set_new_user()

		infoUdate = schemas.UserEmail(
			email = data.email,
			password = data.password
		)

		user_id = 1

		response = client.put(
			f"{self.url}/{user_id}/email", 
			headers = self.headers,
			json=infoUdate.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 409
		assert resultJson == {"message": EmailUnchanged.get()}



	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_update_email_with_invalid_credentials(self, mockToken):
		""" 
			Actualizando email pero ingresando credenciales
			invalidas (contraseña invalida) 
		"""
		mockToken.result_value.state.result_value = True
		self.headers.update(self.auth)

		infoUdate = schemas.UserEmail(
			email = "bolivar19@data.com",
			password = "abcdef"
		)

		user_id = 1

		response = client.put(
			f"{self.url}/{user_id}/email", 
			headers = self.headers,
			json=infoUdate.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 401
		assert resultJson == {"message": InvalidCredentials.get()}


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_update_password_user(self, mockToken):
		""" Validar actualización del 'password' """

		mockToken.result_value.state.result_value = True
		self.headers.update(self.auth)

		infoUdate = schemas.UserPassword(
			password = "abcdef",
			password_repeat = "abcdef",
		)

		user_id = 1

		response = client.put(
			f"{self.url}/{user_id}/password", 
			headers = self.headers,
			json=infoUdate.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 200
		assert resultJson['id'] == 1
		assert resultJson['email'] == EMAIL

	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_update_password_does_not_exists_user(self, mockToken):
		""" 
			Actualizar 'password' de un usuario que no existe
		"""

		mockToken.result_value.state.result_value = True
		self.headers.update(self.auth)

		infoUdate = schemas.UserPassword(
			password = "abcdef",
			password_repeat = "abcdef",
		)

		user_id = 100

		response = client.put(
			f"{self.url}/{user_id}/password", 
			headers = self.headers,
			json=infoUdate.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 404
		assert resultJson == {"message": DoesNotExistsUser.get(id = user_id)}

	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_update_username_user(self, mockToken):
		""" Validar actualización del nombre de usuario """

		mockToken.result_value.state.result_value = True
		self.headers.update(self.auth)

		user_id = 1

		infoUdate = schemas.UserUsername(
			username = "freddy645",
			password = "12345"
		)

		response = client.put(
			f"{self.url}/{user_id}/username", 
			headers = self.headers,
			json=infoUdate.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 200
		assert resultJson["id"] == user_id
		assert resultJson["username"] == infoUdate.username

	
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_update_username_does_not_exists_user(self, mockToken):
		""" 
			Intentar actualizar el 'username' de un usuario que
			no existe.
		"""

		mockToken.result_value.state.result_value = True

		user_id = 100

		self.headers.update(self.auth)

		infoUdate = schemas.UserUsername(
			username = "bolivar19",
			password = "12345"
		)

		response = client.put(
			f"{self.url}/{user_id}/username", 
			headers = self.headers,
			json=infoUdate.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 404
		assert resultJson == {"message": DoesNotExistsUser.get(id = user_id)}


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_update_username_with_existing_username(self, mockToken):
		""" Actualizar 'username' pero con una ya registrado. """
		mockToken.result_value.state.result_value = True
		
		user = set_new_user(username = "bolivar19", email = "bolivar19@data.com")

		self.db.add(user)
		self.db.commit()

		user_id = 1

		self.headers.update(self.auth)

		infoUdate = schemas.UserUsername(
			username = "bolivar19",
			password = "12345"
		)

		response = client.put(
			f"{self.url}/{user_id}/username", 
			headers = self.headers,
			json=infoUdate.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 409
		assert resultJson == {"message": UsernameAlreadyExists.get(username = infoUdate.username)}

	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_update_username_unchanged(self, mockToken):
		""" 
			Intentar actualizar el 'username' sin
			hacer cambios. (Dejar el mismo 'username' que ya posee el usuario)
		"""
		mockToken.result_value.state.result_value = True

		user_id = 1

		self.headers.update(self.auth)

		data = set_new_user()

		infoUdate = schemas.UserUsername(
			username = data.username,
			password = data.password
		)

		response = client.put(
			f"{self.url}/{user_id}/username", 
			headers = self.headers,
			json=infoUdate.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 409
		assert resultJson == {"message": UsernamelUnchanged.get()}


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	@patch("apps.utils.token.token.verify_token")
	def test_update_username_with_invalid_credentials(self, mockToken):
		""" 
			Intentar actualizar el 'username' pero ingresando
			credenciales invalidas
		"""

		mockToken.result_value.state.result_value = True

		user_id = 1

		self.headers.update(self.auth)

		infoUdate = schemas.UserUsername(
			username = "bolivar19",
			password = "abcdef"
		)

		response = client.put(
			f"{self.url}/{user_id}/username", 
			headers = self.headers,
			json=infoUdate.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 401
		assert resultJson == {"message": InvalidCredentials.get()}

	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.utils.utils.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_login_user(self):
		""" Valiadar el acceso del usuario """

		data = set_user_schema()

		auth = schemas.UserLogin(
			email = data.email,
			password = data.password
		)

		response = client.post(
			f"{self.url}/login",
			headers = self.headers,
			json = auth.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 200
		assert resultJson["id"] == 1
		assert resultJson["name"] == data.name 
		assert resultJson["username"] == data.username 
		assert resultJson["email"] == data.email
		assert "auth" in resultJson.keys()
		assert "token" in resultJson["auth"]
		assert "refresh" in resultJson["auth"]

	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.utils.utils.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_login_with_an_invalid_email(self):
		""" 
			Intentar acceder al sistema con un email incorrecto
		"""

		data = set_user_schema()

		auth = schemas.UserLogin(
			email = "bolivar19@data.com",
			password = data.password
		)

		response = client.post(
			f"{self.url}/login",
			headers = self.headers,
			json = auth.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 401
		assert resultJson == {"message": InvalidCredentialsNoEmail.get(email = auth.email)}

	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.utils.utils.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_login_with_invalid_credentials(self):
		""" 
			Intentar acceder al sistema con credenciales 
			invalidas (Contraseña incorrecta)
		"""

		data = set_user_schema()

		auth = schemas.UserLogin(
			email = data.email,
			password = "abcdef1234"
		)

		response = client.post(
			f"{self.url}/login",
			headers = self.headers,
			json = auth.model_dump()
		)

		resultStatus = response.status_code
		resultJson = response.json()

		assert resultStatus == 401
		assert resultJson == {"message": InvalidCredentials.get()}


