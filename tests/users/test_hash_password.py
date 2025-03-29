import os
import pytest

from pydantic import ValidationError

from apps.users.commands.utils.password import HashPassword
from apps.users.commands.utils.password import ValidateHashedPassword


def test_valid_hash_password():
	"""  Validar que se crea una hash de una contraseña """
	password = "12345"

	hashed = HashPassword.getHash(password)

	assert hashed != password
	assert type(hashed) != type(password)


@pytest.mark.parametrize('password', [
	12312312,
	None,
	False,
	{"id": 12},
	["hola", "mundo"]
])
@pytest.mark.xfail(reason = "Recibiendo parametros incorrectos", raises = ValidationError)
def test_invalid_hash_with_wrong_params(password):
	""" Validar el tipo de parametro del método getHash"""

	hashed = HashPassword.getHash(password)

@pytest.fixture
def create_hash_password():
	password = "12345"

	hashed = HashPassword.getHash(password)

	return {'password': password, "hashed": hashed}


def test_valid_validate_hash_password(create_hash_password):
	""" Validar que el hash coincide con el password """

	password = create_hash_password['password']
	hashed = create_hash_password['hashed']
	
	result = ValidateHashedPassword.is_validate(password, hashed)

	assert result


def test_valid_between_two_password(create_hash_password):
	""" Validar hash con un password diferente """
	password = "123abc"
	
	result = ValidateHashedPassword.is_validate(
		password, 
		create_hash_password['hashed']
	)

	assert not result


@pytest.mark.parametrize('password, hashed', [
	("12345", "12345"),
	(b"12345", "12345"),
])
@pytest.mark.xfail(reason = "Recibiendo parametros incorrectos", raises = (ValidationError, ValueError))
def test_invalid_validation_of_params(password, hashed):
	""" Validando parametros de entrada incorrectos"""
	
	ValidateHashedPassword.is_validate(
		passwordPlainText = password, 
		passwordHashed = hashed
	)

