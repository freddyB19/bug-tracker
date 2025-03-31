from typing import Any
from typing import Dict
from typing import Annotated

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import ValidationError
from pydantic import BeforeValidator
from pydantic import validate_call

from apps.users.models import User
from .password import decodePassword

def is_validate(value: User) -> User:
	if not isinstance(value, User):
		raise ValueError("El objeto no es del tipo 'User'")

	return value

TypeData = Annotated[Any, User]
UserType = Annotated[TypeData, BeforeValidator(is_validate)]


class UserSerializer(BaseModel):
	id: int
	name: str
	email: str
	username: str

@validate_call(config = ConfigDict(hide_input_in_errors = True))
def user_serializer(user: UserType) -> Dict[str, str | int]:
	try:
		serializer = UserSerializer(
			id = user.id,
			name = user.name,
			email = user.email,
			username = user.username,
		)
	except ValidationError as e:
		return None

	userDict = serializer.model_dump()
	userDict.update({
		"password": decodePassword.dump_python(user.password)
	})

	return userDict