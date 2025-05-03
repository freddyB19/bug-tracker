import math

from typing import Any
from typing import List
from typing import Dict
from typing import Optional
from typing_extensions import Annotated

from pydantic import Field
from pydantic import BaseModel
from pydantic import validate_call
from pydantic import ConfigDict
from pydantic import PlainSerializer

from fastapi import Request


ListElements = Optional[List[Any]]

PageDefault = 1
PageLowerLimit = 1
PageSizeDefault = 10
PageSizeUpperLimit = 20
PageSizeLowerLimit = 1


class ListPagination(BaseModel):
	page: int = Field(ge = PageLowerLimit, default = PageDefault)
	pageSize: int = Field(ge = PageSizeLowerLimit, le = PageSizeUpperLimit, default = PageSizeDefault) #10


class ResponsePagination(BaseModel):
	previous: str | None
	next: str | None
	current: int


# Sirve para validar el parametro request en 'set_url_pagination'
class RequestContext(BaseModel):
	base_url: str = Field(min_length = 5)
	path: str = Field(min_length = 5)


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def add_params_to_url(params: Optional[Dict[str, int | str]] = None) -> Dict[str, str]:
	url = ""

	if params:
		for var, value in params.items():
			url += f"&{var}={value}"
	
	return {
		"url": url
	}

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def set_url_pagination(request: RequestContext, elements: ListElements, total_elements: int, page: int, pageSize: int, params: Optional[Dict[str, int | str]] = None) -> Dict[str, str]:
	url_params = add_params_to_url(params = params)

	url_base = f"{request.base_url}{request.path}"

	url_next = f"{url_base}?page={page + 1}&pageSize={pageSize}{url_params['url']}"
	url_previous = f"{url_base}?page={page - 1}&pageSize={pageSize}{url_params['url']}"

	pages = math.ceil(total_elements / pageSize)
	
	has_previous = url_previous if (page > 1) and elements else None
	has_next = url_next if page < pages else None

	return {
		"previous": has_previous,
		"next": has_next
	}


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def get_url_from_request(request: Annotated[Any, Request]) -> Dict[str, str]:
	
	if not isinstance(request, Request):
		raise ValueError("el objecto debe ser de tipo 'Request'")

	return {"base_url": str(request.base_url), "path": request.url.path[1:]}


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def calculate_start_pagination(page: int = PageDefault, pageSize:int = PageSizeDefault):
	if page < PageDefault:
		raise ValueError(f"El número de la página no es correcto [{page}]")

	if pageSize < PageSizeLowerLimit or pageSize > PageSizeUpperLimit:
		raise ValueError(f"El tamaño de la página no es el correcto [{pageSize}]")
	
	start = (page - 1) * pageSize

	return start