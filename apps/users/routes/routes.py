from typing import Dict
from typing import List

from fastapi import status
from fastapi import Depends
from fastapi import APIRouter
from fastapi import Response


from pydantic import ValidationError

from apps.users.schemas import schemas
from apps.users.commands import commands


router = APIRouter(prefix = "/user")

DB_USERS = []


@router.get("/hello")
def get_hello_word() -> Dict[str, str]:
	return {"message": "Hola mundo desde user"}


@router.post(
	"/", 
	response_model = schemas.UserResponse,
	status_code=status.HTTP_201_CREATED
) 
def create_user(user: schemas.UserRequest) -> schemas.UserResponse:
	print(user)
	try:
		
		new_user = commands.command_create_user(**user.model_dump())
		DB_USERS.append(new_user)
	except ValidationError as e:
		return Response(
			content = "Los datos ingresados son invalidos",
			status_code = status.HTTP_400_BAD_REQUEST
		)

	return new_user

@router.get("/{id}", 
	response_model = schemas.UserResponse, 
	status_code = status.HTTP_200_OK
)
def get_users(id: int) -> schemas.UserResponse:

	try:
		user = commands.command_get_user(db = DB_USERS, id = id)
	except ValueError as e:
		return Response(
			content = "No existe este usuario",
			status_code = status.HTTP_404_NOT_FOUND
		)

	return user


@router.delete("/{id}",
	status_code = status.HTTP_204_NO_CONTENT
)
def delete_user(id: int) -> Response:
	
	try:
		"""
		Todo esto es solo prueba mientras termino la DB
		"""
		result = commands.command_delete_user(db = DB_USERS, id = id)
		DB_USERS.clear()
		DB_USERS.extend(result) 
	except ValueError as e:
		return Response(
			content = "No existe este usuario",
			status_code = status.HTTP_404_NOT_FOUND
		)

	return Response(
		content = "Usuario eliminado con exito"
	)


@router.patch("/{id}/email", 
	status_code = status.HTTP_200_OK,
	response_model = schemas.UserEmailResponse
)
def update_email(id: int, user: schemas.UserEmail) -> schemas.UserEmailResponse:

	try:
		"""
		Todo esto es solo prueba mientras termino la DB
		"""
		result = commands.command_update_email_user(db = DB_USERS, id = id, userInfo = user)
		DB_USERS.clear()
		DB_USERS.extend(result[0]) 
	except ValueError as e:
		return Response(
			content = str(e),
			status_code = status.HTTP_404_NOT_FOUND
		)


	return result[1] 


@router.patch("/{id}/password", 
	status_code = status.HTTP_200_OK,
	response_model = schemas.UserEmailResponse
)
def update_password(id: int, user: schemas.UserPassword) -> schemas.UserEmailResponse:

	try:
		"""
		Todo esto es solo prueba mientras termino la DB
		"""
		result = commands.command_update_password_user(db = DB_USERS, id = id, userInfo = user)
		DB_USERS.clear()
		DB_USERS.extend(result[0]) 
	except ValueError as e:
		return Response(
			content = str(e),
			status_code = status.HTTP_404_NOT_FOUND
		)


	return result[1] 
