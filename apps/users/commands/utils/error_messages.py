from pydantic import ConfigDict
from pydantic import validate_call


class EmailORUsernameInvalid:
	@classmethod
	def get(cls) -> str:
		return "Ya existe un usuario con ese email o username"


class DoesNotExistsUser:
	@classmethod
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def get(cls, id: int) -> str:
		return f"No existe información sobre el usuario con ID: '{id}'"


class EmailUnchanged:
	@classmethod
	def get(cls) -> str:
		return "Tu nuevo email debe ser diferente al que posees actualmente"


class EmailAlreadyExists:
	@classmethod
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def get(cls, email: str) -> str:
		return f"Ya existe un usuario con ese email: {email}"


class UsernameAlreadyExists:
	@classmethod
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def get(cls, username: str) -> str:
		return f"Ya existe un usuario con ese username: {username}"


class UsernamelUnchanged:
	@classmethod
	def get(cls) -> str:
		return "Tu nuevo nombre de usuario debe ser diferente al que posees actualmente."


class InvalidCredentials:
	@classmethod
	def get(cls) -> str:
		return "Credencial invalida, la contraseña no coincide"


class InvalidCredentialsNoEmail:
	@classmethod
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def get(cls, email: str) -> str:
		return f"Credencial invalida, no exite un usuario con ese email: {email}"


class SerializerUser:
	@classmethod
	def get(cls):
		return f"Ha ocurrido un error interno al momento de serializar User"