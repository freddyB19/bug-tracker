from typing import Dict
from typing import List

from typing_extensions import Annotated

from fastapi import Body
from fastapi import status
from fastapi import Depends
from fastapi import Response
from fastapi import APIRouter
from fastapi import HTTPException

from apps.users.schemas import schemas
from apps.users.commands import commands
from apps.utils.token.token import validate_authorization


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
	try:
		new_user = commands.command_create_user(user = user)
	except ValueError as e:
		return Response(
			content = str(e) if str(e) else "Los datos ingresados son invalidos",
			status_code = status.HTTP_400_BAD_REQUEST
		)
		
	return new_user

@router.get("/{id}", 
	response_model = schemas.UserResponse, 
	status_code = status.HTTP_200_OK
)
def get_user(id: int) -> schemas.UserResponse:

	try:
		user = commands.command_get_user(user_id = id)
	except ValueError as e:
		return Response(
			content = str(e),
			status_code = status.HTTP_404_NOT_FOUND
		)

	return user


@router.delete("/{id}",
	status_code = status.HTTP_204_NO_CONTENT
)
def delete_user(id: int, token: str = Depends(validate_authorization)) -> Response:
	
	try:
		username = commands.command_delete_user(user_id = id)
	except ValueError as e:
		return Response(
			content = str(e),
			status_code = status.HTTP_404_NOT_FOUND
		)

	return Response(
		content = f"Usuario: '{username}' eliminado con exito"
	)


@router.patch("/{id}/email", 
	status_code = status.HTTP_200_OK,
	response_model = schemas.UserEmailResponse
)
def update_email(id: int, user: schemas.UserEmail, token: str = Depends(validate_authorization)) -> schemas.UserEmailResponse:

	try:
		user = commands.command_update_email_user(user_id = id, infoUpdate = user) 
	except ValueError as e:
		return Response(
			content = str(e),
			status_code = status.HTTP_404_NOT_FOUND
		)

	return user


@router.patch("/{id}/password", 
	status_code = status.HTTP_200_OK,
	response_model = schemas.UserEmailResponse
)
def update_password(id: int, user: schemas.UserPassword, token: str = Depends(validate_authorization)) -> schemas.UserEmailResponse:

	try:
		user = commands.command_update_password_user(user_id = id, infoUpdate = user)
	except ValueError as e:
		return Response(
			content = str(e),
			status_code = status.HTTP_404_NOT_FOUND
		)

	return user


@router.put("/{id}/username",
	status_code = status.HTTP_200_OK,
	response_model = schemas.UserUsernameResponse
)

def update_username(id: int, user: schemas.UserUsername,token: str = Depends(validate_authorization)) -> schemas.UserUsernameResponse:
	try:
		user = commands.command_update_username_user(user_id = id, infoUpdate = user)
	except ValueError as e:
		return Response(
			content = str(e),
			status_code = status.HTTP_404_NOT_FOUND
		)

	return user

@router.post("/login",
	status_code = status.HTTP_200_OK,
	response_model = schemas.UserLoginResponse
)
def login(user: schemas.UserLogin) -> schemas.UserLoginResponse:
	try:
		result = commands.command_login(infoLogin = user)
	except Exception as e:
		return Response(
			content = str(e),
			status_code = status.HTTP_400_BAD_REQUEST
		)

	return result


@router.post("/refresh",
	status_code = status.HTTP_200_OK,
	response_model = schemas.TokensResponse
)
def refresh_token(token: schemas.TokenRefresh) -> schemas.TokensResponse:

	result = commands.command_refresh_token(token = token.token)

	if not result.get("auth", False):

		return Response(
			content = result.get("message"),
			status_code = status.HTTP_400_BAD_REQUEST
		)

	return result
