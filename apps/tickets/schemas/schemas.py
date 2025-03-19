from typing import List
from typing import Optional

from datetime import datetime
from typing_extensions import Annotated

from pydantic import BaseModel
from pydantic import AfterValidator
from pydantic import PlainValidator
from pydantic import ValidationInfo

from apps.projects.schemas.schemas import ProjectSimpleResponse
from apps.tickets.models import ChoicesType
from apps.tickets.models import ChoicesState
from apps.tickets.models import ChoicesPrority

MIN_LENGTH_TITLE = 5
MAX_LENGTH_TITLE = 30

MIN_LENGTH_DESCRIPTION = 5
MAX_LENGTH_DESCRIPTION = 200

def set_choice_priority(value: str) -> str:
	str_choices = [choice.name for choice in ChoicesPrority]
	if value not in str_choices:
		raise ValueError(f"La prioridad elegida es incorrecta, debe ser: {str_choices} alguna de estás opciones.")
	return value

def set_choice_state(value: str) -> str:
	str_choices = [choice.name for choice in ChoicesState]
	if value not in str_choices:
		raise ValueError(f"El estado elegido es incorrecto, debe ser: {str_choices} alguna de estás opciones.")

	return value

def set_choice_type(value: str) -> str:
	str_choices = [choice.name for choice in ChoicesType]
	if value not in str_choices:
		raise ValueError(f"El estado elegido es incorrecto, debe ser: {str_choices} alguna de estás opciones.")

	return value

def check_title(value: str) -> str:
	if value <= MIN_LENGTH_TITLE:
		raise ValueError(f"El titulo es demasiado corto, debe ser mayor o igual a {MIN_LENGTH_TITLE} caracteres")

	if value > MAX_LENGTH_TITLE:
		raise ValueError(f"El titulo es demasiado largo, debe ser menor o igual a {MAX_LENGTH_TITLE} caracteres")

	return value

def check_description(value: str) -> str:
	if value <= MIN_LENGTH_DESCRIPTION:
		raise ValueError(f"La descripción es demasiado corto, debe ser mayor o igual a {MIN_LENGTH_DESCRIPTION} caracteres")

	if value > MAX_LENGTH_DESCRIPTION:
		raise ValueError(f"La descripción  es demasiado largo, debe ser menor o igual a {MAX_LENGTH_DESCRIPTION} caracteres")

	return value


def check_length_value(value: str, info: ValidationInfo) -> str:
	fields_validations = {
		"title" : check_title,
		"description" : check_description
	}

	if info.field_name not in fields_validations.keys():
		raise ValueError(f"Error, no existe este validación para este campo: {info.field_name}")


	validation = fields_validations[info.field_name]

	return validation(value = value)

SetLowerChoices = Annotated[
	str,
	PlainValidator(
		lambda value: value.lower()
	)
]


TypeField = Annotated[SetLowerChoices, AfterValidator(set_choice_type)]
StateField = Annotated[SetLowerChoices, AfterValidator(set_choice_state)]
PriorityField = Annotated[SetLowerChoices, AfterValidator(set_choice_priority)]
LenValidationField = Annotated[str, AfterValidator(check_length_value)]

class TicketSchema(BaseModel):
	title: str
	priority: int
	state: int
	type: int
	description: Optional[str] = None
	

class TicketRequest(TicketSchema):
	project_id: int
	state: Optional[StateField] = ChoicesState.nuevo.name
	priority: Optional[PriorityField] = ChoicesPrority.normal.name
	type: Optional[TypeField] = ChoicesType.abierto.name
	description: Optional[LenValidationField] = None


class TicketFilter(BaseModel):
	state: Optional[StateField] = None
	priority: Optional[PriorityField] = None
	type: Optional[TypeField] = None


class TicketResponse(TicketSchema):
	id: int
	created: datetime
	updated: datetime

	project: ProjectSimpleResponse


class ListTicketsResponse(BaseModel):
	tickets: Optional[List[TicketResponse]]