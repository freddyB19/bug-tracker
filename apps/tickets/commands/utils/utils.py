from enum import Enum
from typing import List
from typing import Any
from typing_extensions import Annotated

from pydantic import validate_call


@validate_call
def validate_choice(choice: str, options: Annotated[Any, Enum]) -> bool:
	str_choices = [option.name for option in options]

	if choice not in str_choices:
		return False

	return True
