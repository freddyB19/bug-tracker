import pytest

from pydantic import ValidationError

from apps.tickets.commands.utils.utils import message_create
from apps.tickets.commands.utils.utils import message_update
from apps.tickets.commands.utils.utils import validate_choice
from apps.tickets.commands.utils.utils import set_message_ticket_history

from apps.tickets.models import ChoicesType
from apps.tickets.models import ChoicesState
from apps.tickets.models import ChoicesPrority
from apps.tickets.models import StateTicketHistory


class TestCommandUtilTicket:

	def test_message_create(self):
		"""
			Validar que genera el mensaje esperado
		"""
		ticket_id = 12
		
		message = message_create(ticket_id = ticket_id)

		assert message
		assert message == f"Se ha creado un nuevo ticket con ID: {ticket_id}"


	@pytest.mark.xfail(reason = "Ticket id con valores incorrectos", raises = ValidationError)
	@pytest.mark.parametrize("ticket_id", [
		12.41212,
		"absdc1232",
		None,
		[1,2],
		(23,),
		{"id": 45}
	])
	def test_message_create_with_wrong_value_ticket_id(self, ticket_id):
		"""
			Pasar como parametro valores del ticket_id incorrectos
		"""
		message = message_create(ticket_id = ticket_id)


	@pytest.mark.xfail(reason = "Ausencia de ticket_id", raises = ValidationError)
	def test_message_create_without_ticket_id(self):
		"""
			Invocar la función sin pasar como parametro ticket_id
		"""

		message = message_create()


	def test_message_update(self):
		"""
			Validar que genera el mensaje esperado
		"""
		ticket_id = 12
		message = message_update(
			ticket_id = ticket_id, 
			data = {"priority":"alta", "state": "desarrollo"}
		)

		assert message
		assert message == f"Se han actualizado los campos: [priority='alta' state='desarrollo'] del ticket con ID {ticket_id}"


	def test_message_update_without_data(self):
		"""
			Intener generar el mensaje sin pasar como parametro 'data'
		"""
		ticket_id = 12
		message = message_update(
			ticket_id = ticket_id
		)

		assert not message
		assert len(message) == 0 

	@pytest.mark.xfail(reason = "Ausencia de ticket_id", raises = ValidationError)
	def test_message_update_without_ticket_id(self):
		"""
			Intener generar el mensaje sin pasar como parametro 'ticket_id'
		"""
		message = message_update(
			data = {"priority":"alta", "state": "desarrollo"}
		)

	@pytest.mark.xfail(reason = "Ausencia de ticket_id y data", raises = ValidationError)
	def test_message_update_without_params(self):
		"""
			Intentar generar el mensaje sin pasar algún parametro
		"""

		message = message_update()


	@pytest.mark.xfail(reason = "Ticket id con valores incorrectos", raises = ValidationError)
	@pytest.mark.parametrize("ticket_id", [
		6.222,
		[1],
		(12,10),
		"hola",
		{"id": 12}
	])
	def test_message_update_with_wrong_value_ticket_id(self, ticket_id):
		"""
			Pasar como parametro valores del 'ticket_id' incorrectos
		"""

		message = message_update(
			ticket_id = ticket_id, 
			data = {"priority":"alta", "state": "desarrollo"}
		)

	@pytest.mark.xfail(reason = "Parametro Data con valores incorrectos", raises = ValidationError)
	@pytest.mark.parametrize("data", [
		6.222,
		[1],
		(12,10),
		"hola",
		{"id": None},
		{"data": [1,2,3]},
	])
	def test_message_update_with_wrong_value_data(self, data):
		"""
			Pasar como parametro valores del 'data' incorrectos
		"""
		ticket_id = 12
		message = message_update(
			ticket_id = ticket_id, 
			data = data
		)

	def test_validate_choice(self):
		"""
			Validar que se ha elegido la opción correcto 
			de posibles opciones.
		"""

		# Type (tipo)

		result_type_abierto = validate_choice(options = ChoicesType, choice = "abierto")
		result_type_archivado = validate_choice(options = ChoicesType, choice = "archivado")
		result_type_cerrado = validate_choice(options = ChoicesType, choice = "cerrado")
		result_type_oculto = validate_choice(options = ChoicesType, choice = "oculto")

		# State (estado)

		result_state_nuevo = validate_choice(options = ChoicesState, choice = "nuevo")
		result_state_desarrollo = validate_choice(options = ChoicesState, choice = "desarrollo")
		result_state_prueba = validate_choice(options = ChoicesState, choice = "prueba")
		result_state_terminado = validate_choice(options = ChoicesState, choice = "terminado")
		result_state_repaso = validate_choice(options = ChoicesState, choice = "repaso")
		result_state_documentado = validate_choice(options = ChoicesState, choice = "documentado")

		# Priority (prioridad)

		result_priority_baja = validate_choice(options = ChoicesPrority, choice = "baja")
		result_priority_normal = validate_choice(options = ChoicesPrority, choice = "normal")
		result_priority_alta = validate_choice(options = ChoicesPrority, choice = "alta")
		result_priority_inmediata = validate_choice(options = ChoicesPrority, choice = "inmediata")
		result_priority_ahora = validate_choice(options = ChoicesPrority, choice = "ahora")
		
		# State Ticket History (historial del ticket)

		result_history_crear = validate_choice(options = StateTicketHistory, choice = "crear")
		result_history_actualizar = validate_choice(options = StateTicketHistory, choice = "actualizar")
		result_history_eliminar = validate_choice(options = StateTicketHistory, choice = "eliminar")

		assert result_type_abierto
		assert result_type_archivado
		assert result_type_cerrado
		assert not result_type_oculto

		assert result_state_nuevo
		assert result_state_desarrollo
		assert result_state_prueba
		assert result_state_terminado
		assert result_state_repaso
		assert not result_state_documentado

		assert result_priority_baja
		assert result_priority_normal
		assert result_priority_alta
		assert result_priority_inmediata
		assert not result_priority_ahora

		assert result_history_crear
		assert result_history_actualizar
		assert not result_history_eliminar


	@pytest.mark.xfail(reason = "Opciones de tipo invalida", raises = ValidationError)
	def test_validate_choice_with_wrong_options(self):
		"""
			Validar que no se accepten opciones que
			no sean validas, opciones que no sea de tipo 'enum'
		"""
		options = ["nuevo", "prueba", "desarrollo"]
		result_option = validate_choice(options = options, choice = "nuevo")


	@pytest.mark.xfail(reason = "Elección no recibida", raises = ValidationError)
	def test_validate_choice_without_select_choice(self):
		"""
			Validar que se reciba siempre una opción
		"""
		result_option = validate_choice(options = ChoicesPrority)


	@pytest.mark.xfail(reason = "Opciones no recibidas", raises = ValidationError)
	def test_validate_choice_without_choices(self):
		"""
			Validar que se reciba siempre las
			opciones a seleccionar
		"""
		result_option = validate_choice(choice = "nuevo")

		assert result_option


	def test_message_ticket_history(self):
		"""
			Validar que se genere un mensaje
			sobre el historial de un ticket
		"""
		ticket_id = 12
		
		message_crear = set_message_ticket_history(
			ticket_id = ticket_id,
			state = "crear",
		)

		message_actualizar = set_message_ticket_history(
			ticket_id = ticket_id,
			state = "actualizar",
			data = {"title": "Proyecto A", "state": "desarrollo"}
		)


		assert message_crear == f"Se ha creado un nuevo ticket con ID: {ticket_id}"
		assert message_actualizar == f"Se han actualizado los campos: [title='Proyecto A' state='desarrollo'] del ticket con ID {ticket_id}"


	@pytest.mark.xfail(reason = "Tipo de dato para ticket_id incorrecto", raises = ValidationError)
	@pytest.mark.parametrize("ticket_id", [
		12.1,
		"abc",
		None,
		[1,2,3],
		{"id": 1}
	])
	def test_message_ticket_history_with_wrong_ticket_id(self, ticket_id):
		"""
			Validar que el ticket_id sea un numero entero
		"""
		message = set_message_ticket_history(
			ticket_id = ticket_id,
			state = "crear",
		)


	@pytest.mark.xfail(reason = "Falta ticket_id", raises = ValidationError)
	def test_message_ticket_history_without_ticket_id(self):
		"""
			Validar que se reciba el ticket_id
		"""

		message = set_message_ticket_history(
			state = "crear",
			data = {"title": "Proyecto A", "state": "desarrollo"}
		)

	@pytest.mark.xfail(reason = "Opción para state invalida", raises = ValueError)
	def test_message_ticket_history_with_wrong_state(self):
		"""
			Validar que el 'state' recibido sea de un tipo valido
		"""
		ticket_id = 12

		message = set_message_ticket_history(
			ticket_id = ticket_id,
			state = "eliminar",
		)

		assert message != f"Se ha creado un nuevo ticket con ID: {ticket_id}"


	@pytest.mark.xfail(reason = "Falta state", raises = ValidationError)
	def test_message_ticket_history_without_state(self):
		"""
			Validar que se reciba el 'state'
		"""
		ticket_id = 12

		message = set_message_ticket_history(
			ticket_id = ticket_id,
		)

		assert message != f"Se ha creado un nuevo ticket con ID: {ticket_id}"


	@pytest.mark.xfail(reason = "Tipo de dato para state incorrecto", raises = ValidationError)
	@pytest.mark.parametrize("state", [
		10,
		{"nombre": "carlos"},
		None,
		[1,2,3]
	])
	def test_message_ticket_history_with_wrong_type_state(self, state):
		"""
			Validar que el tipo de dato recibido para state sea
			valido
		"""
		ticket_id = 12

		message = set_message_ticket_history(
			ticket_id = ticket_id,
			state = state
		)