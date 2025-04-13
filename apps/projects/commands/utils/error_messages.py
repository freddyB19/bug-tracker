from typing import List
from pydantic import validate_call
from pydantic import ConfigDict


class InvalidPriority:
	@classmethod
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def get(cls, choices:List[str]) -> str:
		return f"La prioridad indicada es incorrecta, debe ser entre {choices}"


class DoesNotExistsProject:
	@classmethod
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def get(cls, id: int) -> str:
		return f"No existe información sobre el proyecto con ID: {id}"


class UnauthorizedProject:
	@classmethod
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def get(cls, id: int) -> str:
		return f"No existe información sobre este usuario o este proyecto no le pertenece. Proyecto ID: '{id}'"
