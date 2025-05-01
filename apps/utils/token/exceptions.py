import jwt


GENERIC_ERROR_MESSAGE = 'token error'


class TokenExpiredError(Exception):

	def __init__(self, message:str = "El token a expirado") -> None:
		self.message = message

		super().__init__(self.message)


	def __str__(self):
		return f"Token invalido: {self.message}"


class TokenInvalidError(Exception):

	def __init__(self, message: str = "Firma del token no valida") -> None:
		self.message = message
		super().__init__(self.message)

	def __str__(self):
		return f"Firma invalida: {self.message}"


class TokenImmatureError(Exception):

	def __init__(self, message: str = "Error en la estimación del tiempo del token") -> None:
		self.message = message

		super().__init__(self.message)

	def __str__(self):
		return f"Error en el Token: {self.message}"


class TokenDecodeError(Exception):

	def __init__(self, message: str = "No hay suficientes segmentos en el token") -> None:
		self.message = message

		super().__init__(self.message)

	def __str__(self):
		return f"Token invalido: {self.message}"
