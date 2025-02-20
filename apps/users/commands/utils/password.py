from abc import ABC
from abc import abstractmethod
from typing_extensions import Annotated

import bcrypt

from pydantic import Field
from pydantic import validate_call
from pydantic import PlainSerializer
from pydantic.type_adapter import TypeAdapter

TypePassword = Annotated[
	str, 
	Field(frozen=True, strict=True),
	PlainSerializer(lambda value: value.encode('utf-8'), return_type=bytes)
]

TypePasswordHashed = Annotated[
	bytes, 
	Field(frozen=True, strict=True)
]


hashPassword = TypeAdapter(TypePassword)


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
		except ValidationError as e:
			raise ValueError("Error en el password, el tipo de dato ingresado no es valido")
		

class ValidateHashedPassword(ValidateHash):
	def is_validate(passwordPlainText: str, passwordHashed: TypePasswordHashed) -> bool:
		passwordBytes = hashPassword.dump_python(passwordPlainText)
		
		return bcrypt.checkpw(passwordBytes, passwordHashed)
