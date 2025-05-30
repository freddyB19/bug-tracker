from typing import List
from typing import Optional

from datetime import datetime
from typing_extensions import Annotated

from pydantic import Field
from pydantic import BaseModel
from pydantic import AfterValidator
from pydantic import PlainValidator
from pydantic import ValidationInfo
from pydantic import PlainSerializer

from apps.projects.schemas.schemas import ProjectSimpleResponse
from apps.tickets.models import ChoicesType
from apps.tickets.models import ChoicesState
from apps.tickets.models import ChoicesPrority
from apps.tickets.models import StateTicketHistory
from apps.utils.pagination import pagination as pg

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
	if len(value) <= MIN_LENGTH_TITLE:
		raise ValueError(f"El titulo es demasiado corto, debe ser mayor o igual a {MIN_LENGTH_TITLE} caracteres")

	if len(value) > MAX_LENGTH_TITLE:
		raise ValueError(f"El titulo es demasiado largo, debe ser menor o igual a {MAX_LENGTH_TITLE} caracteres")

	return value

def check_description(value: str) -> str:
	if len(value) <= MIN_LENGTH_DESCRIPTION:
		raise ValueError(f"La descripción es demasiado corto, debe ser mayor o igual a {MIN_LENGTH_DESCRIPTION} caracteres")

	if len(value) > MAX_LENGTH_DESCRIPTION:
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

TypeStrField = Annotated[int, PlainSerializer(
	lambda value: ChoicesType(value).name, return_type = str
)]
StateStrField = Annotated[int, PlainSerializer(
	lambda value: ChoicesState(value).name, return_type = str
)]
PriorityStrField = Annotated[int, PlainSerializer(
	lambda value: ChoicesPrority(value).name, return_type = str
)]
HistoryTicketStateStrField = Annotated[int, PlainSerializer(
	lambda value: StateTicketHistory(value).name, return_type = str
)]


class TicketSchema(BaseModel):
	title: str
	priority: int
	state: int
	type: int
	description: Optional[str] = None
	

class TicketRequest(BaseModel):
	project_id: int
	title: LenValidationField
	priority: Optional[PriorityField] = ChoicesPrority.normal.name
	description: Optional[LenValidationField] = None


class TicketFilter(BaseModel):
	state: Optional[StateField] = None
	priority: Optional[PriorityField] = None
	type: Optional[TypeField] = None


class TicketFilterPagination(pg.ListPagination, TicketFilter):
	pass


class TicketByTitle(BaseModel):
	title: str = Field(max_length = MAX_LENGTH_TITLE)


class TicketUpdate(BaseModel):
	title: Optional[LenValidationField] = None
	description: Optional[LenValidationField] = None
	type: Optional[TypeField] = None
	state: Optional[StateField] = None
	priority: Optional[PriorityField] = None


class TicketResponse(TicketSchema):
	id: int
	created: datetime
	updated: datetime
	type: TypeStrField
	state: StateStrField
	priority: PriorityStrField
	project: ProjectSimpleResponse

class TicketSimpleResponse(TicketSchema):
	id: int
	project_id: int
	created: datetime
	updated: datetime
	type: TypeStrField
	state: StateStrField
	priority: PriorityStrField


class TicketBasicResponse(TicketSchema):
	id: int


class ListTickets(BaseModel):
	total: int
	tickets: Optional[List[TicketSimpleResponse]]


class SimpleListTickets(BaseModel):
	tickets: Optional[List[TicketSimpleResponse]]


class TicketsByProjectResponse(pg.ResponsePagination):
	project: ProjectSimpleResponse
	content: ListTickets


class TicketPagination(pg.ListPagination):
	project_id: int


class TicketsHistorySchema(BaseModel):
	id: int
	created: datetime
	message: str
	state: str


class TicketsHistorySimpleResponse(TicketsHistorySchema):
	ticket_id: int
	state: HistoryTicketStateStrField


class TicketsHistoryResponse(TicketsHistorySchema):
	ticket: TicketSimpleResponse
	state: HistoryTicketStateStrField
	


class ListTicketsHistory(BaseModel):
	total: int
	histories: Optional[List[TicketsHistorySimpleResponse]]

class TicketsHistoryByTicketResponse(pg.ResponsePagination):
	ticket: TicketSimpleResponse
	content: ListTicketsHistory