from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing_extensions import Annotated

import bcrypt

from pydantic import Field
from pydantic import validate_call
from pydantic import PlainSerializer
from pydantic import ValidationError
from pydantic.type_adapter import TypeAdapter

from apps.users.models import User
from apps.users.schemas import schemas

TypePassword = Annotated[
	str, 
	Field(frozen=True, strict=True),
	PlainSerializer(lambda value: value.encode('utf-8'), return_type=bytes)
]

TypePasswordHashed = Annotated[
	bytes, 
	Field(frozen=True, strict=True)
]


TypeDecodePassword = Annotated[
	TypePasswordHashed,
	PlainSerializer(lambda value: value.decode('utf-8'), return_type=str)

]

hashPassword = TypeAdapter(TypePassword)
decodePassword = TypeAdapter(TypeDecodePassword)

class Hashed(ABC):
	
	@classmethod
	@abstractmethod
	@validate_call
	def getHash(password: str) -> bytes:
		pass

class ValidateHash(ABC):

	@classmethod
	@abstractmethod
	@validate_call
	def is_validate(password: TypePasswordHashed, passwordHashed: TypePasswordHashed) -> bool:
		pass


class HashPassword(Hashed):
	def getHash(password: str) -> bytes:
		passwordBytes = hashPassword.dump_python(password)

		try:
			return bcrypt.hashpw(passwordBytes, bcrypt.gensalt(10))
		except TypeError as e:
			raise ValueError("Error en el password, el tipo de dato ingresado no es valido")
		

class ValidateHashedPassword(ValidateHash):
	def is_validate(passwordPlainText: str, passwordHashed: TypePasswordHashed) -> bool:
		passwordBytes = hashPassword.dump_python(passwordPlainText)
		
		return bcrypt.checkpw(passwordBytes, passwordHashed)


def user_properties_serializer(user: User) -> Dict[str, str | int]:
	try:
		serializer = schemas.UserResponse(
			id = user.id,
			name = user.name,
			email = user.email,
			username = user.username,
		)
	except ValidationError as e:
		return None

	userDict = serializer.model_dump()
	userDict.update({
		"password": decodePassword.dump_python(user.password)
	})

	return userDict