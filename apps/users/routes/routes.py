
from fastapi import status
from fastapi import Depends
from fastapi import Response
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from apps.users.schemas import schemas
from apps.users.commands import commands
from apps.utils.token.token import validate_authorization


router = APIRouter(prefix = "/user")

STATUS_CODE_ERRORS = {
	400: status.HTTP_400_BAD_REQUEST,
	401: status.HTTP_401_UNAUTHORIZED,
	404: status.HTTP_404_NOT_FOUND,
	409: status.HTTP_409_CONFLICT,
}

@router.post(
	"/", 
	response_model = schemas.UserResponse,
	status_code=status.HTTP_201_CREATED
) 
def create_user(user: schemas.UserRequest) -> schemas.UserResponse:
	try:
		new_user = commands.command_create_user(user = user)
	except ValueError as e:
		message, status_code = e.args

		return JSONResponse(
			content = {"message": message},
			status_code = STATUS_CODE_ERRORS[status_code]
		)
		
	return new_user

@router.get("/{id}", 
	response_model = schemas.UserResponse, 
	status_code = status.HTTP_200_OK
)
def get_user(id: int, token: str = Depends(validate_authorization)) -> schemas.UserResponse:

	try:
		user = commands.command_get_user(user_id = id)
	except ValueError as e:
		message, status_code = e.args
		
		return JSONResponse(
			content = {"message": message},
			status_code = STATUS_CODE_ERRORS[status_code]
		)

	return user


@router.delete("/{id}")
def delete_user(id: int, token: str = Depends(validate_authorization)) -> Response:
	
	try:
		commands.command_delete_user(user_id = id)
	except ValueError as e:
		message, status_code = e.args
		
		return JSONResponse(
			content = {"message": message},
			status_code = STATUS_CODE_ERRORS[status_code]
		)

	return JSONResponse(
		content = {
			"message": f"Usuario: con id: '{id}' eliminado con exito",
		},
		status_code = status.HTTP_204_NO_CONTENT
	)


@router.put("/{id}/email", 
	status_code = status.HTTP_200_OK,
	response_model = schemas.UserEmailResponse
)
def update_email(id: int, user: schemas.UserEmail, token: str = Depends(validate_authorization)) -> schemas.UserEmailResponse:

	try:
		user = commands.command_update_email_user(user_id = id, infoUpdate = user) 
	except ValueError as e:
		message, status_code = e.args
		
		return JSONResponse(
			content = {"message": message},
			status_code = STATUS_CODE_ERRORS[status_code]
		)

	return user


@router.put("/{id}/password", 
	status_code = status.HTTP_200_OK,
	response_model = schemas.UserEmailResponse
)
def update_password(id: int, user: schemas.UserPassword, token: str = Depends(validate_authorization)) -> schemas.UserEmailResponse:

	try:
		user = commands.command_update_password_user(user_id = id, infoUpdate = user)
	except ValueError as e:
		message, status_code = e.args
		
		return JSONResponse(
			content = {"message": message},
			status_code = STATUS_CODE_ERRORS[status_code]
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
		message, status_code = e.args
		
		return JSONResponse(
			content = {"message": message},
			status_code = STATUS_CODE_ERRORS[status_code]
		)

	return user

@router.post("/login",
	status_code = status.HTTP_200_OK,
	response_model = schemas.UserLoginResponse
)
def login(user: schemas.UserLogin) -> schemas.UserLoginResponse:
	try:
		result = commands.command_login(infoLogin = user)
	except ValueError as e:
		message, status_code = e.args

		return JSONResponse(
			content = {"message": message},
			status_code = STATUS_CODE_ERRORS[status_code]
		)

	return result


@router.post("/refresh",
	status_code = status.HTTP_200_OK,
	response_model = schemas.TokensResponse
)
def refresh_token(token: schemas.TokenRefresh) -> schemas.TokensResponse:

	result = commands.command_refresh_token(token = token.token)

	if not result.get("auth", False):

		return JSONResponse(
			content = {"message": result.get("message")},
			status_code = status.HTTP_400_BAD_REQUEST
		)

	return result
