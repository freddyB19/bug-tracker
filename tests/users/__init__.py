from apps.users.models import User
from apps.users.schemas import schemas
from apps.users.commands.utils.password import HashPassword

NAME = "Freddy"
EMAIL = "freddy19@gmail.com"
USERNAME = "freddy19"
PASSWORD = "12345"

def set_new_user(name: str = None, email: str = None, username: str = None, password: str = None) -> User:
	set_name = name if name is not None else NAME
	set_email = email if email is not None else EMAIL
	set_username = username if username is not None else USERNAME
	set_password = password if password is not None else PASSWORD

	return User(
		name = set_name,
		username = set_username,
		email = set_email,
		password = HashPassword.getHash(password = set_password),
	)


def set_user_schema(name: str = None, email: str = None, username: str = None, password: str = None) -> schemas.UserRequest:
	set_name = name if name is not None else NAME
	set_email = email if email is not None else EMAIL
	set_username = username if username is not None else USERNAME
	set_password = password if password is not None else PASSWORD
	set_password_repeat = set_password


	return schemas.UserRequest(
		name = set_name,
		username = set_username ,
		email = set_email,
		password = set_password,
		password_repeat = set_password_repeat
	)
