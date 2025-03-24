import datetime
from typing import Any
from typing import Dict
from typing import Optional


from typing_extensions import Annotated

import jwt

from fastapi import status
from fastapi import Header
from fastapi import HTTPException

from pydantic import BaseModel
from pydantic import validate_call
from pydantic import ConfigDict
from pydantic import ValidationError
from pydantic import AfterValidator

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


class DecodeTokenResult(BaseModel):
	data: Optional[Dict[str, Any]] = {}
	message: Optional[str] = "OK"
	state: Optional[bool] = True


class VerifyTokenResult(BaseModel):
	message: str = "OK"
	state: bool = True


def is_empty(value: Dict[str, Any]) ->  Dict[str, Any]:
	if not value:
		raise ValueError("El diccionario esta vacio")

	return value

isEmpty = Annotated[Dict[str, Any], AfterValidator(is_empty)]


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def validate_token(token: str) -> None:

	try:
		jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM_JWT])
	except jwt.ExpiredSignatureError:
		raise TokenExpiredError()

	except  jwt.InvalidSignatureError:
		raise TokenInvalidError()

	except jwt.ImmatureSignatureError:
		raise TokenImmatureError()


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def verify_token(token: str = "") -> VerifyTokenResult:
	
	message = ""
	
	try:
		validate_token(token)
		return VerifyTokenResult(state = True, message = "OK")
	except TokenExpiredError as e:
		message = e
	except TokenInvalidError as e:
		message = e
	except TokenImmatureError as e:
		message = e

	return VerifyTokenResult(state = False, message = str(message))


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def create_token(infoDict: isEmpty) -> str:

	if not infoDict:
		raise ValidationError("")
	
	data = infoDict.copy()

	data.update({
		"exp": datetime.datetime.utcnow() + datetime.timedelta(hours = ACCESS_TOKEN_EXPIRE_HOURS),
		"iat": datetime.datetime.utcnow()
		#  identifica el momento en el que se emitió el JWT.
	})

	token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM_JWT)

	return token

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def create_refresh_token(infoDict: isEmpty) -> str:
	
	data = infoDict.copy()

	data.update({
		"exp": datetime.datetime.utcnow() + datetime.timedelta(hours = REFRESH_TOKEN_EXPIRE_HOURS),
		"iat": datetime.datetime.utcnow()
	})

	token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM_JWT)

	return token


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def decode_token(token: str) -> DecodeTokenResult:

	message = "" 
	
	try:
		data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM_JWT])
		return DecodeTokenResult(data = data)
	
	except jwt.ExpiredSignatureError:
		message = "El token a expirado"

	except  jwt.InvalidSignatureError:
		message = "Firma del token no valida" 

	except jwt.ImmatureSignatureError:
		message = "Error en la estimación del tiempo del token"

	return DecodeTokenResult(message = message, state = False)


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def extract_token_from_str(auth: str) -> str:
	find = "Bearer "
	
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

	if not result.state:
		raise HTTPException(
				status_code = status.HTTP_401_UNAUTHORIZED, 
				detail = "Token no valido",
				headers={"WWW-Authenticate": "Bearer"},
			)

	return token