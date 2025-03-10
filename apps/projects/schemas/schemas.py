from typing import Optional

from typing_extensions import Annotated

from pydantic import Field
from pydantic import BaseModel
from pydantic import AfterValidator
from pydantic import PlainValidator
from pydantic import field_validator


from apps.projects.models import ChoicesPrority
from apps.users.schemas.schemas import UserResponse

MAX_LENGTH_TITLE = 30
MIN_LENGTH_TITLE = 5 

MAX_LENGTH_DESCRIPTION = 200
MIN_LENGTH_DESCRIPTION = 5 


def set_choice_priority(value:str) -> str:
	CHOICES = [i.name for i in ChoicesPrority]

	if value not in CHOICES:
		raise ValueError(f"Prioridad: '{value}' invalida, eliga una correcta: {CHOICES}")
	
	return value


LowerProrityField = Annotated[str, PlainValidator(
	lambda value: value.lower()
)]
ChoiceProrityField = Annotated[LowerProrityField, AfterValidator(set_choice_priority)]


class ProjectBase(BaseModel):
	title: str
	priority: int


class ProjectRequest(ProjectBase):
	user_id:int
	description: Optional[str | None] = Field(
		max_length = MAX_LENGTH_DESCRIPTION, 
		min_length = MIN_LENGTH_DESCRIPTION
	)
	priority: ChoiceProrityField

	@field_validator('title')
	@classmethod
	def validate_title(cls, data:str) -> str:
		if len(data) > MAX_LENGTH_TITLE:
			raise ValueError(f"El titulo es demasiado largo, debe ser menor o igual a {MAX_LENGTH_TITLE} caracteres")

		if len(data) <= MIN_LENGTH_TITLE:
			raise ValueError(f"El titulo es demasiado corto, debe ser mayor a {MIN_LENGTH_TITLE} caracteres")

		return data

class ProjectResponse(ProjectBase):
	id: int
	user: UserResponse