from sqlalchemy import select

from pydantic import validate_call

from apps import get_db
from apps.users.models.model import User
from apps.projects.models import Project
from apps.projects.schemas import schemas
from apps.projects.models import ChoicesPrority


CHOICES:list = [choice.name for choice in ChoicesPrority]

@validate_call
def command_create_project(project: schemas.ProjectRequest) -> Project:
	db = next(get_db())
	user = db.get(User, project.user_id)

	if user is None:
		raise ValueError(f"No existe información sobre el usuario con ID:'{project.user_id}'")

	if project.priority not in CHOICES:
		raise ValueError(f"La prioridad indicada es incorrecta, debe ser entre {CHOICES}")

	new_project = Project(
		title = project.title, 
		description = project.description,
		priority = project.priority,
		user_id = project.user_id
	)

	db.add(new_project)
	db.commit()
	db.refresh(new_project)

	return new_project


@validate_call
def command_get_project(project_id: int) -> Project:
	db = next(get_db())
	project = db.get(Project, project_id)

	if project is None:
		raise ValueError(f"No existe información sobre el proyecto con ID:'{project_id}'")

	return project