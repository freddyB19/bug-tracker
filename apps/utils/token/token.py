import datetime
from typing import Dict

from typing_extensions import Annotated

import jwt

from fastapi import status
from fastapi import Header
from fastapi import HTTPException

from pydantic import validate_call

from apps import (
	SECRET_KEY,
	ALGORITHM_JWT,
	ACCESS_TOKEN_EXPIRE_HOURS,
	REFRESH_TOKEN_EXPIRE_HOURS
)
from apps.utils.token.exceptions import (
	TokenExpiredError,
	TokenInvalidError,
	TokenImmatureError
) 

def validate_token(token):
	try:
		jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM_JWT])
	except jwt.ExpiredSignatureError:
		raise TokenExpiredError()

	except  jwt.InvalidSignatureError:
		raise TokenInvalidError()

	except jwt.ImmatureSignatureError:
		raise TokenImmatureError()


def verify_token(token: str = ""):
	message = ""
	
	try:
		validate_token(token)
		return {"state": True, "message": "OK"}
	except TokenExpiredError as e:
		message = e
	except TokenInvalidError as e:
		message = e
	except TokenImmatureError as e:
		message = e

	return {"state": False, "message": message}


def create_token(infoDict: Dict):
	data = infoDict.copy()

	data.update({
		"exp": datetime.datetime.utcnow() + datetime.timedelta(hours = ACCESS_TOKEN_EXPIRE_HOURS),
		"iat": datetime.datetime.utcnow()
		#  identifica el momento en el que se emitió el JWT.
	})

	token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM_JWT)

	return token


def create_refresh_token(infoDict: Dict):
	data = infoDict.copy()

	data.update({
		"exp": datetime.datetime.utcnow() + datetime.timedelta(hours = REFRESH_TOKEN_EXPIRE_HOURS),
		"iat": datetime.datetime.utcnow()
	})

	token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM_JWT)

	return token

def decode_token(token: str) -> Dict[str, str | int]:
	return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM_JWT])

@validate_call
def extract_token_from_str(auth: str) -> str:
	find = "Bearer "
	
	if not isinstance(auth, str):
		raise ValueError("El dato recibido no es una cadena de texto")

	if not auth.startswith(find):
		raise ValueError("Error en el formato de envio del token")
	
	return auth.replace(find, "").strip(" ")


def validate_authorization(authorization: Annotated[str | None, Header()] = None) -> str:
	if authorization is None:
		raise HTTPException(
				status_code = status.HTTP_401_UNAUTHORIZED, 
				detail = "Ausencia del token en la cabecera.",
				headers={"WWW-Authenticate": "Bearer"},
			)
	token = extract_token_from_str(auth = authorization)
	
	result = verify_token(token = token)

	if not result['state']:
		raise HTTPException(
				status_code = status.HTTP_401_UNAUTHORIZED, 
				detail = "Token no valido",
				headers={"WWW-Authenticate": "Bearer"},
			)

	return token