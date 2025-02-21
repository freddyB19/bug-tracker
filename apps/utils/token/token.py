import datetime
from typing import Dict


import jwt

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