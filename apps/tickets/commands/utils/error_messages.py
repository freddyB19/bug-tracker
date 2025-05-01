from pydantic import validate_call
from pydantic import ConfigDict


class InvalidPriority:
	@classmethod
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def get(cls) -> str:
		return f"La prioridad indicada es incorrecta"


class InvalidState:
	@classmethod
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def get(cls) -> str:
		return f"El estado indicado es incorrecto"


class InvalidType:
	@classmethod
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def get(cls) -> str:
		return f"El tipo indicado es incorrecto"


class DoesNotExistsTicket:
	@classmethod
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def get(cls, id: int) -> str:
		return f"No existe información sobre el ticket con ID: {id}"


class PaginationError:
	@classmethod
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def get(cls) -> str:
		return "Los valores para la paginación deben ser números enteros positivos"


class DoesNotExistsTicketHistory:
	@classmethod
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def get(cls, id: int) -> str:
		return f"No existe información sobre el ticket_history con ID: {id}"


class InvalidStateTicketHistory:
	@classmethod
	@validate_call(config = ConfigDict(hide_input_in_errors = True))
	def get(cls, state: str) -> str:
		return f"TicketHistory: 'state' invalido = {state}"
