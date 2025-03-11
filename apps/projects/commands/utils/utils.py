from typing import Any
from typing_extensions import Annotated

from pydantic import validate_call

from apps.projects.models import Project
from apps.projects.schemas import schemas


@validate_call
def update_title_project(project: Annotated[Any, Project], title: str | None) -> None:
	if project.title != title:
		project.title = project.title if title is None else title

@validate_call
def update_description_project(project: Annotated[Any, Project], description: str | None) -> None:
	if project.description != description:
		project.description = project.description if description is None else description

@validate_call
def update_priority_project(project: Annotated[Any, Project], priority: str | None) -> None:
	if project.priority != priority:
		project.priority = project.priority if priority is None else priority
	

@validate_call
def update_project(project: Annotated[Any, Project], infoUpdate: schemas.ProjectUpdate) -> Project:
	
	update_title_project(project = project, title = infoUpdate.title)
	
	update_description_project(project = project, description = infoUpdate.description)

	update_priority_project(project = project, priority = infoUpdate.priority)
	
	return project
