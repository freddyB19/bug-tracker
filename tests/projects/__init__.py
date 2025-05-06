from apps.projects.models import Project
from apps.projects.schemas import schemas
from apps.projects.models import ChoicesPrority


CHOICES = [choice.name for choice in ChoicesPrority]

def set_project(title = None, description = None, priority = None, user_id = None):
	set_title = title if title else "Proyecto de tests"
	set_description = description if description else "Proyecto para hacer tests"
	set_priority = priority if priority in CHOICES else ChoicesPrority.normal.name
	set_user_id = user_id if user_id else 1

	return Project(
		title = set_title,
		description = set_description,
		priority = set_priority,
		user_id = set_user_id
	)

def set_project_schema(title = None, description = None, priority = None, user_id = None):
	set_title = title if title else "Proyecto de tests"
	set_description = description if description else "Proyecto para hacer tests"
	set_priority = priority if priority in CHOICES else ChoicesPrority.normal.name
	set_user_id = user_id if user_id else 1

	return schemas.ProjectRequest(
		title = set_title,
		description = set_description,
		priority = set_priority,
		user_id = set_user_id
	)
