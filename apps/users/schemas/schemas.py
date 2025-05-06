from typing import Union
from typing import Optional

from typing_extensions import Annotated


from pydantic import Field
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import StrictBytes
from pydantic import field_validator
from pydantic import ValidationInfo
from pydantic import WrapValidator



def len_string_field(value:str, handler, info: ValidationInfo):
	if len(value) >= 4 and len(value) <= 20:
		return value

	message_error = f"La logitud debe ser entre 4 y 20 caracteres"
	message_error += f" en ({info.field_name})"

	raise ValueError(message_error)

def validate_password(value:str, handler, info: ValidationInfo):
	message_error = ""

	if len(value) > 4:
		return value

	message_error = "La contraseña debe ser mayor a cuatro caracteres"

	raise ValueError(message_error)



def check_passwords_match(value: str, handler, info: ValidationInfo) -> str:
	password = info.data.get('password', None)
	if password is None:
		return ""

	if value == password:
		return value
	
	raise ValueError('Las contraseñas no coinciden')
	

LenStringField = Annotated[str, WrapValidator(len_string_field)]
ValidatePasswordField = Annotated[str, WrapValidator(validate_password)]
CheckPasswordMatchField = Annotated[str, WrapValidator(check_passwords_match)]


class UserBase(BaseModel):
	name: LenStringField
	email: str
	username: LenStringField
	

class UserRequest(UserBase):
	password: ValidatePasswordField
	password_repeat: CheckPasswordMatchField

	@field_validator('email')
	@classmethod
	def validate_email(cls, data: str):
		user_email, symbol, service = data.partition('@')
		if  user_email and symbol and service:

			type_service = service.split(".")

			if len(type_service) == 2:
				if len(type_service[1]) <= 3:
					return data

		raise ValueError(f"Debe ingresar un Email valido: email: {data}")


class UserResponse(UserBase):
	id: int


class UserEmail(BaseModel):
	email: str
	password: str


class UserEmailResponse(BaseModel):
	model_config = ConfigDict(extra='ignore') 
	
	id: int
	email: str


class UserPassword(BaseModel):
	password: ValidatePasswordField
	password_repeat: CheckPasswordMatchField


class UserUsername(BaseModel):
	username: LenStringField
	password: str

class UserUsernameResponse(BaseModel):
	id: int
	username: str

class UserLogin(BaseModel):
	email: str
	password: str 


class AuthUserSchema(BaseModel):
	token: str
	refresh: str

class TokenRefresh(BaseModel):
	token: str

class TokensResponse(BaseModel):
	auth: AuthUserSchema

class UserLoginResponse(UserResponse):
	auth: AuthUserSchema