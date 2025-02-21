from random import randint
from typing import List
from typing import Dict
from typing import Optional

from pydantic import validate_call

from apps.users.models import User
from apps.utils.token.token import create_token
from apps.utils.token.token import verify_token
from apps.utils.token.token import create_refresh_token
from apps.users.commands.utils.password import HashPassword
from apps.users.commands.utils.password import ValidateHashedPassword
from .utils.password import user_properties_serializer



@validate_call
def command_create_user(name: str, email: str, password: str, username: str, password_repeat: str) -> Dict[str, str]: # User
	new_user = {
		"id": randint(1, 60), 
		"name": name,
		"email": email,
		"password": HashPassword.getHash(password = password),
		"username": username
	}
	return new_user

@validate_call
def command_get_user(id: int, db:List[Dict] | None = None) -> Dict[str, str]:  #User
	
	user = [user for user in db if user["id"] == id]

	if not user:
		raise ValueError("Not Found")

	return user.pop()

@validate_call
def command_delete_user(id, db:List[Dict] | None = None) -> bool:
	user = command_get_user(id = id, db = db)
	
	newTable = [user for user in db if user['id'] != id]

	return newTable


@validate_call
def command_update_email_user(id, userInfo, db:List[Dict] | None = None) -> bool:
	user = command_get_user(id = id, db = db)

	passwordHashed = user['password']
	passwordPlainText = userInfo.password

	if not ValidateHashedPassword.is_validate(passwordPlainText, passwordHashed):
		raise ValueError("Credencial invalida, la contraseña no coincide.")


	user['email'] = userInfo.email
	
	newTable = [user for user in db if user['id'] != id]

	newTable.append(user)

	return (newTable, user)



@validate_call
def command_update_password_user(id, userInfo, db: List[Dict] | None = None) -> tuple:
	user = command_get_user(id = id, db = db)

	passwordPlainText = userInfo.password_new

	user["password"] = HashPassword.getHash(password = passwordPlainText)

	newTable = [user for user in db if user['id'] != id]
	newTable.append(user)
	return (newTable, user)

@validate_call
def command_update_user(id, userInfo, db: List[Dict] | None = None) -> tuple:
	user = command_get_user(id = id, db = db)

	new_name = userInfo.name if userInfo.name else False
	new_email = userInfo.email if userInfo.email else False 
	new_username = userInfo.username if userInfo.username else False
	new_password = userInfo.password if userInfo.password else False


	user['name'] = user['name'] if not new_name else new_name
	user['email'] = user['email'] if not new_email else new_email
	user['username'] = user['username'] if not new_username else new_username
	user['password'] = user['password'] if not new_password else HashPassword.getHash(new_password)


	newTable = [user for user in db if user['id'] != id]

	newTable.append(user)

	return (newTable, user)

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





















