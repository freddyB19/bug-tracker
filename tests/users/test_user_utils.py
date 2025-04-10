import pytest
from unittest.mock import patch

from pydantic import ValidationError

from tests import ENGINE
from tests import SESSION
from tests import get_db

from apps import Model
from apps.users.models import User
from apps.users.commands.utils.utils import user_serializer
from apps.users.commands.utils.password import HashPassword


class OtherUserTable:
	def __init__(self):
		self.name = "freddy"
		self.email = "freddy@gmail.com"
		self.username = "freddy19"
		self.password = "12345"

class TestCommandUserUtils:

	def setup_method(self):
		Model.metadata.drop_all(ENGINE)
		Model.metadata.create_all(ENGINE)

		self.db = SESSION

	@patch("apps.users.commands.utils.utils.User", User)
	@patch("apps.users.commands.commands.User", User)
	@patch("apps.users.commands.commands.get_db", get_db)
	def test_serializer_user(self):
		""" Validar que se genera un objeto User serializado """
		user = User(
			name = "freddy", 
			email = "freddy19@gmail.com", 
			password = HashPassword.getHash(password = "12345"), 
			username = "freddy19"
		)
		
		self.db.add(user)
		self.db.commit()
		self.db.refresh(user)

		serializer = user_serializer(user = user)

		assert type(serializer) == dict
		assert serializer['name'] == user.name
		assert serializer['email'] == user.email
		assert serializer['password'] == user.password.decode('utf-8')
		assert serializer['username'] == user.username

	@pytest.mark.xfail(reason = "Pasando un valor invalido", raises = ValueError)
	@patch("apps.users.commands.utils.utils.User", User)
	def test_serializer_with_wrong_param(self):
		""" Generar un error al enviar un objeto diferente de User """
		user = OtherUserTable()

		serializer = user_serializer(user = user)


	def teardown_method(self):
		self.db.rollback()
		self.db.close()