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

class ListPagination(BaseModel):
	page: int = Field(ge = 0, default = 0)
	pageSize: int = Field(ge = 1, le = 20, default = 10) #10


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

	elements_per_page = page + pageSize

	return {
		"previous": url_previous if (page >= 1 ) and elements else None,
		"next": url_next if (elements_per_page < total_elements) and elements else None,
	}


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def get_url_from_request(request: Annotated[Any, Request]) -> Dict[str, str]:
	
	if not isinstance(request, Request):
		raise ValueError("el objecto debe ser de tipo 'Request'")

	return {"base_url": str(request.base_url), "path": request.url.path[1:]}

