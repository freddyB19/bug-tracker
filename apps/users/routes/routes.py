from typing import Dict

from fastapi import Depends
from fastapi import APIRouter
from app.users.database
router = APIRouter(prefix = "/user")


@router.get("/")
def get_hello_word() -> Dict[str, str]:
	return {"message": "Hola mundo desde user"}