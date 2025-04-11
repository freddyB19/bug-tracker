from typing import List

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.orm import joinedload

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

	if db.query(Project).filter(Project.id == project_id).one_or_none() is None:
		raise ValueError(f"No existe información sobre el proyecto.")

	sql = (
		select(Project)
		.options(joinedload(Project.user))
		.where(Project.id == project_id)
	)

	project = db.scalar(sql)

	return project


@validate_call
def command_update_project(project_id: int, infoUpdate: schemas.ProjectUpdate) -> Project:
	db = next(get_db())

	user = infoUpdate.model_dump(include = ['user_id'])
	values = infoUpdate.model_dump(exclude_defaults = True, exclude = ['user_id'])

	if db.query(Project).filter(Project.id == project_id, Project.user_id == user['user_id']).one_or_none() is None:
		raise ValueError(f"No existe información sobre este proyecto o no le pertenece a este usuario.'{project_id}'")

	sql = (
		update(Project)
		.where(Project.id == project_id)
		.where(Project.user_id == user['user_id'])
		.values(**values)
		.returning(Project)
	)

	project = db.scalar(sql)

	db.commit()
	db.refresh(project)
	
	db.close()
	return project

@validate_call
def command_delete_project(project_id: int) -> None:
	db = next(get_db())

	project = db.get(Project, project_id)

	if project is None:
		raise ValueError(f"No existe información sobre el proyecto con ID:'{project_id}'")

	db.delete(project)
	db.commit()

@validate_call
def command_get_projects_user(page: int, pageSize: int, user_id: int) -> List[Project]:
	db = next(get_db())

	start = page * pageSize

	sql = (
		select(Project)
		.join(User)
		.where(Project.user_id == user_id)
		.offset(start)
		.limit(pageSize)
	)

	projects = db.scalars(sql).all()

	return projects

@validate_call
def command_get_total_project_user(user_id: int) -> int:
	db = next(get_db())

	sql = (
		select(func.count())
		.select_from(Project)
		.where(Project.user_id == user_id)
	)

	total = db.scalar(sql)

	return total
