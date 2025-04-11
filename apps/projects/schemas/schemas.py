from typing import List
from typing import Optional

from datetime import datetime
from typing_extensions import Annotated

from pydantic import Field
from pydantic import BaseModel
from pydantic import AfterValidator
from pydantic import PlainValidator
from pydantic import field_validator

from apps.projects.models import ChoicesPrority
from apps.users.schemas.schemas import UserResponse
from apps.utils.pagination import pagination as pg


MAX_LENGTH_TITLE = 30
MIN_LENGTH_TITLE = 5 

MAX_LENGTH_DESCRIPTION = 200
MIN_LENGTH_DESCRIPTION = 5 


def set_choice_priority(value:str) -> str:
	CHOICES = [i.name for i in ChoicesPrority]

	if value not in CHOICES:
		raise ValueError(f"Prioridad: '{value}' invalida, eliga una correcta: {CHOICES}")
	
	return value


def check_length_title(value: str) -> str:
	if len(value) > MAX_LENGTH_TITLE:
		raise ValueError(f"El titulo es demasiado largo, debe ser menor o igual a {MAX_LENGTH_TITLE} caracteres")

	if len(value) <= MIN_LENGTH_TITLE:
		raise ValueError(f"El titulo es demasiado corto, debe ser mayor a {MIN_LENGTH_TITLE} caracteres")

	return value


LowerProrityField = Annotated[str, PlainValidator(
	lambda value: value.lower()
)]
ChoiceProrityField = Annotated[LowerProrityField, AfterValidator(set_choice_priority)]
LengthTitleField = Annotated[str, AfterValidator(check_length_title)]


class ProjectBase(BaseModel):
	title: str
	priority: int


class ProjectRequest(ProjectBase):
	user_id:int
	description: Optional[str | None] = Field(
		max_length = MAX_LENGTH_DESCRIPTION, 
		min_length = MIN_LENGTH_DESCRIPTION
	)
	priority: ChoiceProrityField = Field(default = ChoicesPrority.normal.name)
	title: LengthTitleField


class ProjectResponse(ProjectBase):
	id: int
	user: UserResponse
	created: datetime
	updated: datetime


class ProjectUpdate(BaseModel):
	user_id: int
	description: Optional[str | None] = None
	title: Optional[LengthTitleField | None] = None
	priority: Optional[ChoiceProrityField | None] = None


class ProjectDelete(BaseModel):
	user_id: int


class ProjectSimpleResponse(ProjectBase):
	id: int
	created: datetime
	updated: datetime
	description: str | None


class ListProjects(BaseModel):
	total: int
	projects: Optional[List[ProjectSimpleResponse]]


class ProjectsByUser(pg.ResponsePagination):
	user: UserResponse
	content: ListProjects

class ProjectsPagination(pg.ListPagination):
	user_id: int