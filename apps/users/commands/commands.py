from random import randint
from typing import List
from typing import Dict
from typing import Optional

from sqlalchemy import select
from sqlalchemy import or_

from pydantic import validate_call

from apps import get_db
from apps.users.schemas import schemas
from apps.users.models import User
from .utils.password import HashPassword
from .utils.password import ValidateHashedPassword
from .utils.utils import user_serializer
from apps.utils.token.token import create_token
from apps.utils.token.token import verify_token
from apps.utils.token.token import decode_token
from apps.utils.token.token import create_refresh_token

from apps.utils.token.token import TokenDecode
from apps.utils.token.token import TokenCreate
from apps.utils.token.token import TokenRefresh


@validate_call
def command_create_user(user: schemas.UserRequest)-> User:
	db = next(get_db())

	validate_user = db.query(
		User
	).filter(or_(
			User.username == user.username, 
			User.email == user.email
		)
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
def command_delete_user(user_id: int) -> None:
	db = next(get_db())

	user = db.get(User, user_id)

	if user is None:
		raise ValueError(f"No existe información sobre el usuario '{user_id}'")

	db.delete(user)
	db.commit()

@validate_call
def command_update_email_user(user_id: int, infoUpdate: schemas.UserEmail) -> User:
	db = next(get_db())

	user = db.get(User, user_id)

	if user is None:
		raise ValueError(f"No existe información sobre el usuario '{user_id}'")

	if user.email == infoUpdate.email:
		raise ValueError("Tu nuevo email debe ser diferente al que posees actualmente")

	if db.query(User).filter(User.email == infoUpdate.email).one_or_none() is not None:
		raise ValueError(f"Ya existe un usuario con ese email: '{infoUpdate.email}'")

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

	passwordPlainText = infoUpdate.password
	user.password = HashPassword.getHash(password = passwordPlainText)

	db.commit()
	db.refresh(user)

	return user


@validate_call
def command_update_username_user(user_id: int, infoUpdate: schemas.UserUsername) -> User:
	db = next(get_db())

	user = db.get(User, user_id)

	if user is None:
		raise ValueError(f"No existe información sobre el usuario '{user_id}'")

	if user.username == infoUpdate.username:
		raise ValueError("Tu nuevo nombre de usuario debe ser diferente al que posees actualmente.")

	if db.query(User).filter(User.username == infoUpdate.username).one_or_none() is not None:
		raise ValueError(f"Ya existe un usuario con ese username: '{infoUpdate.username}'")

	passwordHashed = user.password
	passwordPlainText = infoUpdate.password

	if not ValidateHashedPassword.is_validate(passwordPlainText, passwordHashed):
		raise ValueError("Credencial invalida, la contraseña no coincide.")

	user.username = infoUpdate.username

	db.commit()
	db.refresh(user)

	return user


@validate_call
def command_login(infoLogin: schemas.UserLogin) -> Dict[str, str | int]:
	db = next(get_db())

	userResult = db.scalar(
		select(User)
		.where(User.email == infoLogin.email)
	)

	if userResult is None:
		raise ValueError(f"Credencial invalida, no exite un usuario con ese email: {infoLogin.email}")

	passwordHashed = userResult.password
	passwordPlainText = infoLogin.password

	if not ValidateHashedPassword.is_validate(passwordPlainText, passwordHashed):
		raise ValueError("Credencial invalida, la contraseña no coincide.")

	user = user_serializer(user = userResult)
	
	if user is None:
		raise ValueError("Ha ocurrido un error interno al momento de serializar User")
	
	token = TokenCreate.main(data = user)
	refresh_token = TokenRefresh.main(data = user)

	user.update({
		'auth': {
			"token": token,
			"refresh": refresh_token
		}
	})

	return user


@validate_call
def command_refresh_token(token: str)-> Dict[str, str | bool]:
	token_validation = verify_token(token)

	if not token_validation.state:
		return token_validation.model_dump()

	user = TokenDecode.main(token = token)

	if not user.state:
		return user.model_dump()

	token = TokenCreate.main(data = user.data)
	refresh_token = TokenRefresh.main(data = user.data)
	
	tokens =  {
		'auth': {
			"token": token,
			"refresh": refresh_token
		}
	}

	return tokens