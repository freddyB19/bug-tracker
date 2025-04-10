import pytest
from unittest.mock import patch

from pydantic import ValidationError

from tests import ENGINE
from tests import SESSION
from tests import get_db

from apps import Model
from apps.users.models import User
from apps.users.schemas import schemas
from apps.users.commands import commands
from apps.utils.token.token import TokenCreate
from apps.utils.token.token import verify_token
from apps.users.commands.utils.password import HashPassword
from apps.users.commands.utils.password import ValidateHashedPassword


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


class TestCommandsUser:

	def setup_method(self):
		Model.metadata.drop_all(ENGINE)
		Model.metadata.create_all(ENGINE)

		self.db = SESSION

		user = set_new_user()

		self.db.add(user)
		self.db.commit()
		self.db.refresh(user)
		
		self.user = user


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_data_in_db(self):
		""" Validar que se han guardado los datos en la DB"""

		list_data = self.db.query(User).all()

		assert len(list_data) == 1
		assert list_data[0].id == 1


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_create_user(self):
		""" Validar que se crea un usuario"""

		user = schemas.UserRequest(
			name = "Carlos",
			username = "carlos19",
			email = "carlos19@gmail.com",
			password = "12345",
			password_repeat = "12345"
		)


		new_user = commands.command_create_user(user = user)

		assert new_user.id == 2
		assert new_user.name == user.name
		assert new_user.username == user.username
		assert new_user.email == user.email


	@pytest.mark.xfail(reason = "Existe un usuario con ese email", raises = ValueError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_create_user_with_an_existing_email(self):
		""" Validar que no se cree un usuario con un email ya registrado """
		user = set_user_schema()
		new_user = commands.command_create_user(user = user)


	@pytest.mark.xfail(reason = "Existe un usuario con ese username", raises = ValueError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_create_user_with_an_existing_username(self):
		""" Validar que no se cree un usuario con un email ya registrado """

		user = set_user_schema(email = "freddy@gmail.com")
		new_user = commands.command_create_user(user = user)
	

	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_get_user_by_id(self):
		""" Obtener la información de un usuario por ID"""
		
		user = commands.command_get_user(user_id = 1)

		assert user.id == 1
		assert user.username == "freddy19"
		assert user.email == "freddy19@gmail.com"


	@pytest.mark.xfail(reason = "No existe información sobre este usuario", raises = ValueError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_get_does_not_exists_user(self):
		""" Generar un error al tratar de obtener un usuario con una ID invalida"""
		user = commands.command_get_user(user_id = 100)


	@pytest.mark.parametrize("user_id", [
		"1",
		{"id": 1},
		None,
		1.2
	])
	@pytest.mark.xfail(reason = "Pasando parametro incorrecto", raises = ValidationError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_get_user_with_wrong_params(self, user_id):
		""" Validar que se este pasando el tipo de dato correcto a la función"""
		
		user = commands.command_get_user(user_id = user_id)


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_delete_user(self):
		""" Validar que se puede eliminar un usuario """
		
		user_id = 1

		commands.command_delete_user(user_id = user_id)

		user = self.db.get(User, user_id)

		assert user is None


	@pytest.mark.xfail(reason="No existe información sobre el usuario a eliminar", raises=ValueError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_delete_does_not_exists_user(self):
		""" Generar un error al intentar eliminar un usuario que no existe """		
		
		user_id = 100

		commands.command_delete_user(user_id = user_id)


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_update_email_user(self):
		""" Validar que se actualice el email de un usuario """
		
		user_id = 1

		user = schemas.UserEmail(
			email = "freddydata@gmail.com", 
			password="12345"
		)

		userUpdate = commands.command_update_email_user(
			user_id = user_id,
			infoUpdate = user
		)


		assert self.user.id == userUpdate.id
		assert self.user.email != userUpdate.email


	@pytest.mark.xfail(reason = "No existe información sobre este usuario", raises = ValueError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_update_email_with_does_not_exists_user(self):
		""" 
			Generar un error al intear actualizar el email de un usuario
			que no existe
		"""
		user_id = 100

		user = schemas.UserEmail(
			email = "freddydata@gmail.com", 
			password="12345"
		)

		userUpdate = commands.command_update_email_user(
			user_id = user_id,
			infoUpdate = user
		)


	@pytest.mark.xfail(reason = "Actualización con el mismo email", raises = ValueError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_update_email_without_changes(self):
		""" 
			Generar un error al intentar actualizar el email 
			con el email actual.

		"""

		user_id = 1

		user = schemas.UserEmail(
			email = EMAIL, 
			password="12345"
		)

		userUpdate = commands.command_update_email_user(
			user_id = user_id,
			infoUpdate = user
		)


	@pytest.mark.xfail(reason = "Ya existe registro con este email", raises = ValueError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_update_email_with_existing_email(self):
		""" 
			Generar un error al intentar actualizar un email
			por uno ya registrado
		"""
		new_user = set_new_user(email = "bolivar19@gmail.com", username="bolivar19")

		self.db.add(new_user)
		self.db.commit()

		user_id = 1

		user = schemas.UserEmail(
			email = "bolivar19@gmail.com", 
			password="12345"
		)

		userUpdate = commands.command_update_email_user(
			user_id = user_id,
			infoUpdate = user
		)


	@pytest.mark.xfail(reason = "La contraseña no coincide", raises = ValueError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_update_email_with_invalid_credential(self):
		""" 
			Generar un error al intentar actualizar un email,
			pero ingresando la credencial incorrecta (contraseña)
		"""

		user_id = 1

		user = schemas.UserEmail(
			email = "bolivar19@gmail.com", 
			password="abcdef"
		)

		userUpdate = commands.command_update_email_user(
			user_id = user_id,
			infoUpdate = user
		)


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_update_password_user(self):
		""" Validar la actualización de la contraseña """
		
		user_id = 1
		new_password = "abcdef"

		user = schemas.UserPassword(
			password = new_password,
			password_repeat = new_password
		)

		userUpdate = commands.command_update_password_user(
			user_id = user_id,
			infoUpdate = user
		)

		assert userUpdate.id == self.user.id
		assert ValidateHashedPassword.is_validate(
			passwordPlainText = user.password, 
			passwordHashed = userUpdate.password
		)


	@pytest.mark.xfail(reason = "No existe información sobre este usuario", raises = ValueError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_update_password_with_does_not_exists_user(self):
		""" 
			Generar un error al intentar cambiar la contraseña
			de un usuario que no existe
		"""

		user_id = 1000
		new_password = "abcdef"

		user = schemas.UserPassword(
			password = new_password,
			password_repeat = new_password
		)

		userUpdate = commands.command_update_password_user(
			user_id = user_id,
			infoUpdate = user
		)


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_update_username_user(self):
		""" Validar la actualización del username del usuario """
		user_id = 1

		user = schemas.UserUsername(
			username = "freddy645",
			password = "12345"
		)

		userUpdate = commands.command_update_username_user(
			user_id = user_id,
			infoUpdate = user
		)

		data = self.db.get(User, user_id)


		assert userUpdate.id == data.id
		assert userUpdate.username == data.username
		assert userUpdate.username != self.user.username


	@pytest.mark.xfail(reason="No existe información sobre este usuario", raises=ValueError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_update_username_with_does_not_exists_user(self):
		""" 
			Generar un error al intear actualizar el username de un usuario
			que no existe
		"""

		user_id = 100

		user = schemas.UserUsername(
			username = "freddy645",
			password = "12345"
		)

		userUpdate = commands.command_update_username_user(
			user_id = user_id,
			infoUpdate = user
		)


	@pytest.mark.xfail(reason="Actualización con el mismo username", raises=ValueError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_update_username_without_changes(self):
		""" 
			Generar un error al intentar actualizar el username 
			con el username actual
		"""

		user_id = 1

		user = schemas.UserUsername(
			username = self.user.username,
			password = "12345"
		)

		userUpdate = commands.command_update_username_user(
			user_id = user_id,
			infoUpdate = user
		)


	@pytest.mark.xfail(reason="Ya existe registro con este username", raises=ValueError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_update_username_with_exsisting_username(self):
		""" 
			Generar un error al intentar actualizar un username
			por uno ya registrado
		"""
		new_user = set_new_user(email="bolivar19@gmail.com", username="bolivar19")

		self.db.add(new_user)
		self.db.commit()
		
		user_id = 1

		user = schemas.UserUsername(
			username = "bolivar19",
			password = "12345"
		)

		userUpdate = commands.command_update_username_user(
			user_id = user_id,
			infoUpdate = user
		)


	@pytest.mark.xfail(reason="la contraseña no coincide", raises=ValueError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_update_username_with_invalid_credential(self):
		""" 
			Generar un error al intentar actualizar un username,
			pero ingresando la credencial incorrecta (contraseña)
		"""

		user_id = 1

		user = schemas.UserUsername(
			username = "bolivar19",
			password = "abcdef"
		)

		userUpdate = commands.command_update_username_user(
			user_id = user_id,
			infoUpdate = user
		)


	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.utils.utils.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_login_user(self):
		""" Validar que el usuario puede hacer login"""
		
		credentials = schemas.UserLogin(
			email = EMAIL,
			password = PASSWORD
		)

		user = commands.command_login(
			infoLogin = credentials
		)

		# Validación del tipo de dato devuelto
		assert type(user) == dict

		# Validación del usuario
		assert user['id'] == self.user.id
		assert user['name'] == self.user.name
		assert user['email'] == self.user.email
		assert user['username'] == self.user.username
		assert user['password'] == self.user.password.decode("utf-8")

		#Validación de credenciales de acceso
		assert "auth" in user.keys()
		assert "token" in user["auth"]
		assert "refresh" in user["auth"]

		result_token = verify_token(token = user['auth']['token'])
		retusl_refresh = verify_token(token = user['auth']['refresh'])

		assert result_token.state
		assert result_token.message == "OK"

		assert retusl_refresh.state
		assert retusl_refresh.message == "OK"


	@pytest.mark.parametrize("credentials", [
		# Usando un correo incorrecto
		{"email": "bolivar19@gmail.com", "password": PASSWORD},
		# Usando un contraseña incorrecta
		{"email": EMAIL, "password": "abcdf"},

	])
	@pytest.mark.xfail(reason = "Credenciales invalidas, email o password incorrecto", raises=ValueError)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.utils.utils.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_login_with_wrong_credentials(self, credentials):
		""" 
			Generar un error al intentar hacer login
			con credenciales invalidas
		"""

		user = commands.command_login(
			infoLogin = credentials
		)
	

	def test_get_refresh_token(self):
		""" Validar que se crea un token-refresh """
		user = {"id": 1, "name": "Freddy", "email": "freddy10@gmail.com"}

		token = TokenCreate.main(data = user)

		refresh = commands.command_refresh_token(token = token)

		assert type(refresh) == dict
		assert "auth" in refresh.keys()
		assert "token" in refresh["auth"]
		assert "refresh" in refresh["auth"]


	def test_refresh_token_with_invalid_token(self):
		""" No se generan un token-refresh ante un token no valido """

		invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

		refresh = commands.command_refresh_token(token = invalid_token)

		assert "auth" not in refresh
		assert not refresh['state']
		assert refresh['message'] != ""

	def teardown_method(self):
		self.db.rollback()
		self.db.close()