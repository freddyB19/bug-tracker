from random import randint
from typing import List
from typing import Dict
from typing import Optional

from pydantic import validate_call

from apps import get_db
from apps.users.schemas import schemas
from apps.users.models import User
from .utils.password import HashPassword
from .utils.password import ValidateHashedPassword
from .utils.password import user_properties_serializer
from apps.utils.token.token import create_token
from apps.utils.token.token import verify_token
from apps.utils.token.token import decode_token
from apps.utils.token.token import create_refresh_token


@validate_call
def command_create_user(user: schemas.UserRequest)-> User:
	db = next(get_db())

	validate_user = db.query(
		User
	).filter(
		User.name == user.name, 
		User.email == user.email
	).one_or_none()


	if validate_user is not None:
		raise ValueError("Ya existe un usuario con ese email o username")

	new_user = User(
		name = user.name, 
		email = user.email, 
		username = user.username,
		password = HashPassword.getHash(password = user.password),
	)

	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	
	return new_user

@validate_call
def command_get_user(user_id: int) -> User:
	
	db = next(get_db())

	user = db.get(User, user_id)

	if user is None:
		raise ValueError(f"No existe información sobre el usuario '{user_id}'")

	return user

@validate_call
def command_delete_user(user_id) -> bool:
	db = next(get_db())

	user = db.get(User, user_id)

	if user is None:
		raise ValueError(f"No existe información sobre el usuario '{user_id}'")

	db.delete(user)
	db.commit()

	return user.username

@validate_call
def command_update_email_user(user_id: int, infoUpdate: schemas.UserEmail) -> User:
	db = next(get_db())

	user = db.get(User, user_id)

	if user is None:
		raise ValueError(f"No existe información sobre el usuario '{user_id}'")
	
	passwordHashed = user.password
	passwordPlainText = infoUpdate.password

	if not ValidateHashedPassword.is_validate(passwordPlainText, passwordHashed):
		raise ValueError("Credencial invalida, la contraseña no coincide.")

	user.email = infoUpdate.email

	db.commit()
	db.refresh(user)

	return user

@validate_call
def command_update_password_user(user_id: int, infoUpdate: schemas.UserPassword) -> User:
	db = next(get_db())

	user = db.get(User, user_id)

	if user is None:
		raise ValueError(f"No existe información sobre el usuario '{user_id}'")

	passwordPlainText = infoUpdate.password_new
	user.password = HashPassword.getHash(password = passwordPlainText)

	db.commit()
	db.refresh(user)

	return user


@validate_call
def command_login(user, db:List[Dict] | None = None) -> Dict[str, int | str]: #User
	data = [userInfo for userInfo in db if userInfo["email"] == user.email]

	if not data:
		raise ValueError(f"Credencial invalida, no exite un usuario con ese email: {user.email}")

	userResult = data.pop()

	passwordHashed = userResult['password']
	passwordPlainText = user.password

	if not ValidateHashedPassword.is_validate(passwordPlainText, passwordHashed):
		raise ValueError("Credencial invalida, la contraseña no coincide.")

	user = user_properties_serializer(userResult)
	token = create_token(infoDict = user)
	refresh_token = create_refresh_token(infoDict = user)

	user.update({
		'auth': {
			"token": token,
			"refresh": refresh_token
		}
	})

	return user



@validate_call
def command_refresh_token(token: str)-> Dict[str, str]:
	token_validation = verify_token(token)

	if not token_validation.get("state"):
		return token_validation

	user = decode_token(token)
	
	token = create_token(infoDict = user)
	refresh_token = create_refresh_token(infoDict = user)

	tokens =  {
		'auth': {
			"token": token,
			"refresh": refresh_token
		}
	}

	return tokens