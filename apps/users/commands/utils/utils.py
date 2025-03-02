from typing import Dict

from pydantic import ValidationError

from apps.users.models import User
from apps.users.schemas import schemas
from .password import decodePassword

def user_properties_serializer(user: User) -> Dict[str, str | int]:
	try:
		serializer = schemas.UserResponse(
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