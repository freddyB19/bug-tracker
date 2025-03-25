import os
import sys
from unittest.mock import patch 

import pytest

from pydantic import ValidationError
from fastapi import Request

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE)
sys.path.append(os.path.join(BASE, "apps"))

from apps.utils.pagination.pagination import add_params_to_url
from apps.utils.pagination.pagination import set_url_pagination
from apps.utils.pagination.pagination import get_url_from_request


@pytest.mark.parametrize(
	"data, url", 
	[
		(
			{
			"user_id": 1,
			"state": "normal",
			"priority": "alta"
			}, "&user_id=1&state=normal&priority=alta"
		),
		(
			{	
			"project_id": 21,
			"type": "abierto",
			}, "&project_id=21&type=abierto"
		)
	]
)
def test_valid_add_params_to_url(data, url):
	url_result = add_params_to_url(data)

	assert url_result['url'] == url


def test_valid_url_with_empty_parms():
	url_result = add_params_to_url({})

	assert url_result['url'] == ""


def test_valid_function_without_params():
	url_result = add_params_to_url()

	assert url_result['url'] == ""


@pytest.mark.xfail(reason = "Pasando por parametro un valor incorrecto", raises = ValidationError)
def test_ivalid_function_with_wrong_params():
	url_result = add_params_to_url(["project_id", 1, "type", "abierto"])

	assert url_result['url'] == ""


def test_valid_set_url_pagination():
	page = 0
	pageSize = 5
	elements = [1,2,3,4,5,6,7,8,9,10]
	
	pg = set_url_pagination(
		request = {"base_url": "http://127.0.0.1:8000", "path": "/ticket/23"},
		elements = elements,
		total_elements = len(elements),
		page = page,
		pageSize = pageSize
	)

	pg_next = f"http://127.0.0.1:8000/ticket/23?page={page + 1}&pageSize={pageSize}"

	page2 = 2
	pageSize2 = 2
	elements2 = [1,2,3,4,5,6,7,8,9,10]
	
	pg2 = set_url_pagination(
		request = {"base_url": "http://127.0.0.1:8000", "path": "/ticket/23"},
		elements = elements2,
		total_elements = len(elements2),
		page = page2,
		pageSize = pageSize2
	)

	pg_previous2 = f"http://127.0.0.1:8000/ticket/23?page={page2 - 1}&pageSize={pageSize2}"
	pg_next2 = f"http://127.0.0.1:8000/ticket/23?page={page2 + 1}&pageSize={pageSize2}"


	assert pg.get("previous") is None
	assert pg.get("next") == pg_next

	assert pg2.get("previous") == pg_previous2
	assert pg2.get("next") == pg_next2


@pytest.mark.xfail(reason = "Omitiendo el parametro request", raises = ValidationError)
def test_ivalid_set_url_pagination_with_error_in_param():

	pg = set_url_pagination(
		elements = [1,2,3,4,5,6,7,8,9,10],
		total_elements = len([1,2,3,4,5,6,7,8,9,10]),
		page = 0,
		pageSize = 5
	)


@pytest.mark.xfail(reason = "Parametro invalido en request", raises = ValidationError)
def test_ivalid_set_url_pagination_with_wrong_param():
	pg = set_url_pagination(
		request = ["hola", "mundo"],
		elements = [1,2,3,4,5,6,7,8,9,10],
		total_elements = len([1,2,3,4,5,6,7,8,9,10]),
		page = 0,
		pageSize = 5
	)


@pytest.mark.xfail(reason = "Error en la estructura del valor del request.", raises = ValidationError)
def test_ivalid_set_url_pagination_error_in_request_value():
	""" Request recibe un valor con estructura incorrecta
		
		El valor que debe recibir es: 
		Dict[str, str] = {"base_url": "...", "path": "..."}  
		
	"""
	pg = set_url_pagination(
		request = {"base": "http://127.0.0.1:8000", "pat": "/ticket/23"},
		elements = [1,2,3,4,5,6,7,8,9,10],
		total_elements = len([1,2,3,4,5,6,7,8,9,10]),
		page = 0,
		pageSize = 5
	)


def test_valid_get_url_from_request():
	"""Validando la obtención de las urls de request"""	
	result = get_url_from_request(request = Request(scope={
		"type": "http", 
		"server": ("127.0.0.1","8000"), 
		"headers": {},
		"path": "/ticket/1"

		}))

	assert isinstance(result, dict)
	assert len(result.keys()) == 2
	assert type(result['base_url']) == str
	assert result['base_url'] != ""
	assert type(result['path']) == str
	assert result['path'] != ""
	assert result['base_url'] == "http://127.0.0.1:8000/"
	assert result['path'] == "ticket/1"
	
@pytest.mark.parametrize("request_value", [
	[12,3,45],
	None,
	"Hola mundo",
	False,
	{"id": 1},
	123
])
@pytest.mark.xfail(reason = "Pasando un parametro incorrecto a request", raises = ValueError)
def test_invalid_url_from_request_with_wrong_param(request_value):
	""" Validando error al pasar un parametro errorneo"""
	result = get_url_from_request(request = request_value)

