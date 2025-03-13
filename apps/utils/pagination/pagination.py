from typing import Any
from typing import List
from typing import Dict
from typing import Optional
from typing_extensions import Annotated

from fastapi import Request
from pydantic import validate_call

from apps.projects.models import Project


ListProjects = Optional[List[Annotated[Any, Project]]]


@validate_call
def add_params_to_url(url_next: str, url_previous: str, params: Optional[Dict[str, int]] = None) -> Dict[str, str]:


	if params:
		for var, value in params.items():
			url_previous += f"&{var}={value}"
			url_next += f"&{var}={value}"

	return {
		"url_previous": url_previous,
		"url_next": url_next
	}

@validate_call
def set_url_pagination(request: Annotated[Any, Request], elements: ListProjects, total_elements: int, page: int, pageSize: int, params: Optional[Dict[str, int]] = None) -> Dict[str, str]:
	url = f"{request.base_url}{request.url.path[1:]}"

	elements_per_page = page + pageSize

	url_previous = f"{url}?page={page - 1}&pageSize={pageSize}"
	url_next = f"{url}?page={page + 1}&pageSize={pageSize}"

	urls = add_params_to_url(
		params = params,
		url_next = url_next,
		url_previous = url_previous
	)

	return {
		"previous": urls["url_previous"] if (page >= 1 ) and elements else None,
		"next": urls["url_next"] if (elements_per_page < total_elements) and elements else None,
	}