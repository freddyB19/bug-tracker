import os
import sys
from unittest.mock import patch 

import jwt
import pytest


from pydantic import ValidationError

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE)
sys.path.append(os.path.join(BASE, "apps"))

from apps.utils.token.token import create_token
from apps.utils.token.token import decode_token
from apps.utils.token.token import verify_token
from apps.utils.token.token import extract_token_from_str
from apps.utils.token.token import validate_token
from apps.utils.token.token import create_refresh_token
from apps.utils.token.token import validate_authorization
from apps.utils.token.token import TokenCreate
from apps.utils.token.token import TokenRefresh
from apps.utils.token.token import TokenDecode

from apps.utils.token.exceptions import TokenInvalidError
from apps.utils.token.exceptions import TokenExpiredError


def test_valid_create_a_token():
    """ Comprobando que se ha creado un token """
    token = TokenCreate.main(data = {"name": "Freddy"})

    assert not isinstance(token, int)
    assert isinstance(token, str)

@pytest.mark.parametrize("data_token", [
    None,
    [12,3,4,5],
    "Hola mundo",
    ("cadena", 123)
])
@pytest.mark.xfail(reason = "Pasando por parametro un valor incorrecto", raises = ValidationError)
def test_create_token_with_wrong_param(data_token):
    """ Intentando crear tokens con datos invalidos"""
    token = TokenCreate.main(data = data_token)


@pytest.mark.xfail(reason = "Parametro vacio", raises = ValueError)
def test_create_token_with_empty_param():
    """ Intentando crear token con un diccionario vacío"""
    token = TokenCreate.main(data = {})


def test_valid_create_refresh_token():
    token = TokenRefresh.main(data = {"name": "Freddy"})

    assert not isinstance(token, int)
    assert isinstance(token, str)

@pytest.mark.parametrize("data_token", [
    None,
    [12,3,4,5],
    "Hola mundo",
    ("cadena", 123)
])
@pytest.mark.xfail(reason = "Pasando por parametro un valor incorrecto", raises = ValidationError)
def test_create_refresh_token_with_wrong_param(data_token):
    """Intentando crear 'token refresh' con datos invalidos """
    token = TokenRefresh.main(data = data_token)


@pytest.mark.xfail(reason = "Parametro vacio", raises = ValueError)
def test_create_refresh_token_with_empty_param():
    """ Intentando crear un 'token refresh' con un diccionario vacío"""
    token = TokenRefresh.main(data = {})


def test_validate_data_in_token():
    """ Comprobar la información de un token"""
    data_user = {"id": 1, "name": "Freddy", "email": "freddy10@gmail.com"}
    token = TokenCreate.main(data = data_user)

    data_token = TokenDecode.main(token = token)

    assert data_token.state
    assert data_token.message == "OK"
    assert data_user['id'] == data_token.data['id']
    assert data_user['name'] == data_token.data['name']
    assert data_user['email'] == data_token.data['email']

def test_validate_data_with_wrong_token():
    """ Acceder a la información con un token invalido."""
    wrong_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    
    data_token = TokenDecode.main(wrong_token)

    assert not data_token.state
    assert data_token.data == {}


def test_valid_extraction_token_of_str():
    """ Extraer el token almacenado en un str"""
    string_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

    token = extract_token_from_str(string_token)

    assert not token.startswith("Bearer")
    assert token == string_token[7:]

    
@pytest.mark.parametrize("wrong_token", [
    "BearereyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
])
@pytest.mark.xfail(reason="Error en el formato del token", raises = ValueError)
def test_invalid_extraction_token_of_str_with_wrong_format(wrong_token):
    """ Extraer el token almacenado en un str con formato invalido."""
    token = extract_token_from_str(wrong_token)


@pytest.mark.parametrize("token", [
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYm9saXZhciIsImVtYWlsIjoiYm9saXZhckBkYXRhLmNvbSIsInVzZXJuYW1lIjoiYm9saXZhcjE5IiwiaWQiOjMsInBhc3N3b3JkIjoiJDJiJDEwJEpDSjRiRzlaMy5zU2hQb295eWxVeHVDVmZQV2FWbldSODk0L1cyZy5ISE16Y29hRElRZXB1IiwiZXhwIjoxNzQyNTM2MjM2LCJpYXQiOjE3NDI1MzI2MzZ9.iuEYp1mWQAu92WLksG6EFcIVeGJqaK7vUMnpKliSCcM",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
])
@pytest.mark.xfail(reason="El token expirado o firma invalida", raises = (TokenExpiredError, TokenInvalidError))
def test_validation_of_token(token):
    """ Comprobar si el token es uno valido."""
    validate_token(token = token)
    

def test_valid_verification_token():
    """ Comprobar que el token generado es valido."""
    data_user = {"id": 1, "name": "Freddy", "email": "freddy10@gmail.com"}
    token = TokenCreate.main(data = data_user)

    result = verify_token(token)

    assert result.state
    assert result.message == "OK"


def test_invalid_verification_token():
    """ Comprobar que el token generado es invalido."""
    data_user = {"id": 1, "name": "Freddy", "email": "freddy10@gmail.com"}
    token = TokenCreate.main(data = data_user)

    error_token = token[:160] # Se omite una parte del token
    
    result = verify_token(error_token)

    assert len(error_token) != len(token)
    assert not result.state
