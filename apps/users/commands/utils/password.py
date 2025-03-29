from abc import ABC
from abc import abstractmethod

from typing_extensions import Annotated

import bcrypt

from pydantic import Field
from pydantic import ConfigDict
from pydantic import validate_call
from pydantic import PlainSerializer
from pydantic import BeforeValidator

from pydantic.type_adapter import TypeAdapter

def is_byte(value: bytes) -> bytes:

	if not isinstance(value, bytes):
		raise ValueError("El tipo de dato debe ser un 'byte'")

	return value


TypePassword = Annotated[
	str, 
	Field(frozen=True, strict=True),
	PlainSerializer(lambda value: value.encode('utf-8'), return_type=bytes)
]

IsByte = Annotated[bytes, BeforeValidator(is_byte)]

TypePasswordHashed = Annotated[
	IsByte, 
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
	def getHash(password: str) -> bytes:
		pass

class ValidateHash(ABC):

	@classmethod
	@abstractmethod
	def is_validate(password: TypePasswordHashed, passwordHashed: TypePasswordHashed) -> bool:
		pass


class HashPassword(Hashed):
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def getHash(password: str) -> bytes:
		passwordBytes = hashPassword.dump_python(password)

		try:
			return bcrypt.hashpw(passwordBytes, bcrypt.gensalt(10))
		except TypeError as e:
			raise ValueError("Error en el password, el tipo de dato ingresado no es valido")
		

class ValidateHashedPassword(ValidateHash):
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def is_validate(passwordPlainText: str, passwordHashed: TypePasswordHashed) -> bool:
		passwordBytes = hashPassword.dump_python(passwordPlainText)
		
		return bcrypt.checkpw(passwordBytes, passwordHashed)
