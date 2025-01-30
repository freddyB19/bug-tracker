from typing_extensions import Annotated

from pydantic import Field
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import StrictBytes
from pydantic import field_validator
from pydantic import ValidationInfo


class UserBase(BaseModel):
	name: str
	email: str
	username: str
	

class UserRequest(UserBase):
	password: str
	password_repeat: str

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

	@field_validator("password")
	@classmethod
	def validate_password(cls, data: str):
		message_error = ""
		
		if len(data) > 4:
			return data
		
		message_error = "La contraseña debe ser mayor a cuatro caracteres"

		raise ValueError(message_error)

	@field_validator('password_repeat', mode="after")
	@classmethod
	def check_passwords_match(cls, value: str, info: ValidationInfo) -> str:
		if value != info.data['password']:
			raise ValueError('Las contraseñas no coinciden')
		return value


class UserResponse(UserBase):
	id: int
	password: StrictBytes | str



class UserEmail(BaseModel):
	email: str



class UserEmailResponse(BaseModel):
	model_config = ConfigDict(extra='ignore') 
	
	id: int
	email: str
