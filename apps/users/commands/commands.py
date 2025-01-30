from random import randint
from typing import List
from typing import Dict
from typing import Optional



from abc import ABC
from abc import abstractmethod
from typing_extensions import Annotated

import bcrypt
from pydantic import Field
from pydantic import validate_call
from pydantic import ValidationError
from pydantic import PlainSerializer
from pydantic.type_adapter import TypeAdapter


from apps.users.models import User


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


@validate_call
def command_create_user(name: str, email: str, password: str, username: str, password_repeat: str) -> Dict[str, str]: # User
	new_user = {
		"id": randint(1, 60), 
		"name": name,
		"email": email,
		"password": HashPassword.getHash(password = password),
		"username": username
	}
	return new_user

@validate_call
def command_get_user(id: int, db:List[Dict] | None = None) -> Dict[str, str]:  #User
	
	user = [user for user in db if user["id"] == id]

	if not user:
		raise ValueError("Not Found")

	return user.pop()

@validate_call
def command_delete_user(id, db:List[Dict] | None = None) -> bool:
	user = command_get_user(id = id, db = db)
	
	newTable = [user for user in db if user['id'] != id]

	return newTable


@validate_call
def command_update_email_user(id, userInfo, db:List[Dict] | None = None) -> bool:
	user = command_get_user(id = id, db = db)

	passwordHashed = user['password']
	passwordPlainText = userInfo.password

	if not ValidateHashedPassword.is_validate(passwordPlainText, passwordHashed):
		raise ValueError("Credencial invalida, la contraseñas no coincide.")


	user['email'] = userInfo.email
	
	newTable = [user for user in db if user['id'] != id]

	newTable.append(user)

	return (newTable, user)






