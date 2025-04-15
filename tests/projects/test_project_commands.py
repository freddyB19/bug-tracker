import pytest
from unittest.mock import patch

from pydantic import ValidationError

from tests import ENGINE
from tests import SESSION
from tests import get_db

from apps import Model
from apps.users.models import User
from apps.projects.models import Project
from apps.projects.schemas import schemas
from apps.projects.commands import commands
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


class TestCommandsProject:

	def setup_method(self):
		Model.metadata.drop_all(ENGINE)
		Model.metadata.create_all(ENGINE)

		self.db = SESSION

		user = User(
			name = 'bolivar',
			email = 'bolivar@gmail.com',
			username = 'bolivar19',
			password = '12345'
		)

		self.db.add(user)
		self.db.commit()
		self.db.refresh(user)

		self.user = user

		project = set_project(user_id = self.user.id)
		
		self.db.add(project)
		self.db.commit()
		self.db.refresh(project)

		self.project = project


	def teardown_method(self):
		self.db.rollback()
		self.db.close()


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_create_new_project(self):
		""" Validar que se crea un nuevo proyecto """
		
		schema_project = set_project_schema(
			user_id = self.user.id
		)

		project = commands.command_create_project(project = schema_project)

		assert project.id == 2
		assert project.title == schema_project.title
		assert project.description == schema_project.description
		assert project.priority.name == schema_project.priority
		assert project.user_id == schema_project.user_id

	@pytest.mark.xfail(reason = "No existe este usuario", raises = ValueError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_create_project_with_no_existent_user(self):
		""" 
			Intenar que no se cree un proyecto con un usuario
			que no esta registrado
		"""
		schema_project = set_project_schema(
			user_id = 100
		)

		project = commands.command_create_project(project = schema_project)


	@pytest.mark.xfail(reason = "Parametro 'priority' incorrecto", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_create_project_with_wrong_priority(self):
		"""
			Intentar que no se cree un proyecto con una prioridad
			incorrecta.
		"""
		schema_project = set_project_schema(
			user_id = self.user.id
		)

		project = commands.command_create_project(project = {
			"title": "Proyecto A",
			"description": "descripción del proyecto A",
			"priority": "ahora",
			"user_id": 1,
		})

	@pytest.mark.xfail(reason = "Logitud de 'description' muy larga", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_create_project_with_too_long_description(self):
		"""
			Intentar que no se cree un proyecto con una descripción
			muy larga
		"""
		descripcion = """
			Lorem ipsum dolor sit amet consectetur adipisicing elit. 
			Aspernatur, magni nostrum est deserunt officia quas illo quis, 
			aliquam unde animi quod debitis voluptates recusandae ut minima, 
			eos dicta molestiae accusamus?
			Lorem ipsum dolor sit amet consectetur adipisicing elit. 
			Aspernatur, magni nostrum est deserunt officia quas illo quis, 
			aliquam unde animi quod debitis voluptates recusandae ut minima, 
			eos dicta molestiae accusamus?
			Lorem ipsum dolor sit amet consectetur adipisicing elit. 
			Aspernatur, magni nostrum est deserunt officia quas illo quis, 
			aliquam unde animi quod debitis voluptates recusandae ut minima, 
			eos dicta molestiae accusamus?
			Lorem ipsum dolor sit amet consectetur adipisicing elit. 
			Aspernatur, magni nostrum est deserunt officia quas illo quis, 
			aliquam unde animi quod debitis voluptates recusandae ut minima, 
			eos dicta molestiae accusamus?
			Lorem ipsum dolor sit amet consectetur adipisicing elit. 
			Aspernatur, magni nostrum est deserunt officia quas illo quis, 
			aliquam unde animi quod debitis voluptates recusandae ut minima, 
			eos dicta molestiae accusamus?
			Lorem ipsum dolor sit amet consectetur adipisicing elit. 
			Aspernatur, magni nostrum est deserunt officia quas illo quis, 
			aliquam unde animi quod debitis voluptates recusandae ut minima, 
			eos dicta molestiae accusamus?
			Lorem ipsum dolor sit amet consectetur adipisicing elit. 
			Aspernatur, magni nostrum est deserunt officia quas illo quis, 
			aliquam unde animi quod debitis voluptates recusandae ut minima, 
			eos dicta molestiae accusamus?
		"""
		project = commands.command_create_project(project = {
			"title": "Proyecto A",
			"description": descripcion,
			"user_id": 1,
		})


	@pytest.mark.xfail(reason = "Logitud de 'description' muy corto", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_create_project_with_very_short_description(self):
		"""
			Intentar que no se cree un proyecto con una descripción
			muy corta
		"""
		project = commands.command_create_project(project = {
			"title": "Proyecto A",
			"description": "info",
			"user_id": 1,
		})


	@pytest.mark.xfail(reason = "Logitud de 'title' muy largo", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_create_project_with_too_long_title(self):
		"""
			Intentar que no se cree un proyecto con un titulo
			muy largo
		"""
		title = """
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		"""

		project = commands.command_create_project(project = {
			"title": title,
			"description": "descripción del proyecto",
			"user_id": 1,
		})



	@pytest.mark.xfail(reason = "Logitud de 'title' muy corto", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_create_project_with_very_short_title(self):
		"""
			Intentar que no se cree un proyecto con un titulo
			muy corto
		"""
		project = commands.command_create_project(project = {
			"title": "app",
			"description": "descripción del proyecto",
			"user_id": 1,
		})


	@pytest.mark.xfail(reason = "Sin parametro 'description' ", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_create_project_without_description(self):
		"""
			Intentar que no se cree un proyecto sin una descripción
		"""
		project = commands.command_create_project(project = {
			"title": "Proyecto A",
			"user_id": 1,
		})


	@pytest.mark.xfail(reason = "Sin parametro 'title' ", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_create_project_without_title(self):
		"""
			Intentar que no se cree un proyecto sin un titulo
		"""
		project = commands.command_create_project(project = {
			"description": "descripción del proyecto",
			"user_id": 1,
		})


	@pytest.mark.xfail(reason = "Sin parametro 'user_id' ", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_create_project_without_user_id(self):
		"""
			Intentar que no se cree un proyecto sin un usuario
		"""
		project = commands.command_create_project(project = {
			"title": "Proyecto A",
			"description": "descripción del proyecto",
		})


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_project_by_id(self):
		""" 
			Obtener un proyecto por us ID
		"""
		project_id = 1

		project = commands.command_get_project(project_id = project_id)

		assert project.id == self.project.id
		assert project.title == self.project.title
		assert project.description == self.project.description
		assert project.priority == self.project.priority
		assert project.created == self.project.created
		assert project.updated == self.project.updated
		assert project.user_id == self.project.user_id


	@pytest.mark.xfail(reason = "No existe el proyecto ", raises = ValueError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_no_existent_project(self):
		"""
			Intentar obtener un proyecto por una ID que no existe
		"""
		project_id = 100

		project = commands.command_get_project(project_id = project_id)

		assert project.id == self.project.id


	@pytest.mark.xfail(reason = "Sin parametro", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_project_without_params(self):
		"""
			Intentar obtener un proyecto por una ID que no existe
		"""
		project = commands.command_get_project()

		assert project.id == self.project.id


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_update_project(self):
		"""
			Validar la actualición de un proyecto
		"""
		infoUpdate = schemas.ProjectUpdate(
			user_id = self.user.id,
			title = "Actualizando Proyecto A",
			description = "Una app para hacer test",
			priority = "alta"
		)

		project_updated = commands.command_update_project(
			project_id = self.project.id,
			infoUpdate = infoUpdate
		)

		assert project_updated.id == self.project.id
		assert project_updated.title != self.project.title
		assert project_updated.priority.name != self.project.priority.name
		assert project_updated.description != self.project.description

		assert project_updated.title == infoUpdate.title
		assert project_updated.priority.name == infoUpdate.priority
		assert project_updated.description == infoUpdate.description


	@pytest.mark.xfail(reason = "No existe este proyecto", raises = ValueError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_update_no_existent_project(self):
		"""
			Intentar actualizar un proyecto que no existe
		"""
		project_id = 100

		infoUpdate = schemas.ProjectUpdate(
			user_id = self.user.id,
			title = "Actualizando Proyecto A",
			description = "Una app para hacer test",
			priority = "alta"
		)

		project_updated = commands.command_update_project(
			project_id = project_id,
			infoUpdate = infoUpdate
		)


	@pytest.mark.xfail(reason = "No existe este usuario", raises = ValueError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_update_project_no_existent_user(self):
		"""
			Intentar actualizar un proyecto con un ID de usuario
			que no existe.
		"""
		user_id = 100
		
		infoUpdate = schemas.ProjectUpdate(
			user_id = user_id,
			title = "Actualizando Proyecto A",
			description = "Una app para hacer test",
			priority = "alta"
		)

		project_updated = commands.command_update_project(
			project_id = self.project.id,
			infoUpdate = infoUpdate
		)

		assert project_updated.id != self.project.id


	@pytest.mark.xfail(reason = "Usuario no autorizado", raises = ValueError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_update_project_with_unauthorized_user(self):
		"""
			Intentar actualizar un proyecto con el ID 
			de otro usuario.
		"""
		new_user = User(
			name = 'alejandro',
			email = 'alejandro@gmail.com',
			username = 'alejandro19',
			password = '12345'
		)

		self.db.add(new_user)
		self.db.commit()
		self.db.refresh(new_user)

		infoUpdate = schemas.ProjectUpdate(
			user_id = new_user.id,
			title = "Actualizando Proyecto A",
			description = "Una app para hacer test",
			priority = "alta"
		)

		project_updated = commands.command_update_project(
			project_id = self.project.id,
			infoUpdate = infoUpdate
		)


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_update_project_only_description(self):
		"""
			Intentar actualizar un valor del proyecto (description)
		"""
		infoUpdate = schemas.ProjectUpdate(
			user_id = self.user.id,
			description = "Una app para hacer test",
		)

		project_updated = commands.command_update_project(
			project_id = self.project.id,
			infoUpdate = infoUpdate
		)

		assert project_updated.id == self.project.id
		assert project_updated.title == self.project.title
		assert project_updated.description != self.project.description
		assert project_updated.priority.name == self.project.priority.name

		assert project_updated.description == infoUpdate.description


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_update_project_only_title(self):
		"""
			Intentar actualizar un valor del proyecto (title)
		"""
		infoUpdate = schemas.ProjectUpdate(
			user_id = self.user.id,
			title = "Actualizando Proyecto A",
		)

		project_updated = commands.command_update_project(
			project_id = self.project.id,
			infoUpdate = infoUpdate
		)

		assert project_updated.id == self.project.id
		assert project_updated.title != self.project.title
		assert project_updated.description == self.project.description
		assert project_updated.priority.name == self.project.priority.name

		assert project_updated.title == infoUpdate.title


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_update_project_only_priority(self):
		"""
			Intentar actualizar un valor del proyecto (priority)
		"""
		infoUpdate = schemas.ProjectUpdate(
			user_id = self.user.id,
			priority = "baja"
		)

		project_updated = commands.command_update_project(
			project_id = self.project.id,
			infoUpdate = infoUpdate
		)

		assert project_updated.id == self.project.id
		assert project_updated.title == self.project.title
		assert project_updated.description == self.project.description
		assert project_updated.priority.name != self.project.priority.name

		assert project_updated.priority.name == infoUpdate.priority

	@pytest.mark.xfail(reason = "Valor de 'priority' incorrecto", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_update_project_with_wrong_priority(self):
		"""
			Intentar actualizar la prioridad (priority) con
			un valor incorrecto
		"""
		project_updated = commands.command_update_project(
			project_id = self.project.id,
			infoUpdate = {
				"priority": "ahora",
				"user_id": self.user.id
			}
		)


	@pytest.mark.xfail(reason = "Descripción muy larga", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_update_project_with_too_long_description(self):
		"""
			Intentar actualizar la descripción (description) con
			un valor muy largo
		"""
		description = """
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?

		"""

		project_updated = commands.command_update_project(
			project_id = self.project.id,
			infoUpdate = {
				"user_id": self.user.id,
				"description": description
			}
		)


	@pytest.mark.xfail(reason = "Descripción muy corta", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_update_project_with_too_short_description(self):
		"""
			Intentar actualizar la descripción (description) con
			un valor muy corto
		"""
		description = "app"

		project_updated = commands.command_update_project(
			project_id = self.project.id,
			infoUpdate = {
				"user_id": self.user.id,
				"description": description
			}
		)


	@pytest.mark.xfail(reason = "Titulo muy largo", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_update_project_with_too_long_title(self):
		"""
			Intentar actualizar el titulo (title) con
			un valor muy largo
		"""
		title = """
		Lorem ipsum dolor sit amet consectetur adipisicing elit. 
		Aspernatur, magni nostrum est deserunt officia quas illo quis, 
		aliquam unde animi quod debitis voluptates recusandae ut minima, 
		eos dicta molestiae accusamus?
		"""

		project_updated = commands.command_update_project(
			project_id = self.project.id,
			infoUpdate = {
				"title": title,
				"user_id": self.user.id
			}
		)


	@pytest.mark.xfail(reason = "Titulo muy corto", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_update_project_with_too_short_title(self):
		"""
			Intentar actualizar el titulo (title) con
			un valor muy corto
		"""
		title = "app"

		project_updated = commands.command_update_project(
			project_id = self.project.id,
			infoUpdate = {
				"title": title,
				"user_id": self.user.id
			}
		)

	@pytest.mark.xfail(reason = "Sin parametro proyecto_id", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_update_project_without_project_id(self):
		"""
			Intentar actualizar el titulo (title) con
			un valor muy corto
		"""

		project_updated = commands.command_update_project(
			infoUpdate = {
				"title": "Una simple app",
				"user_id": self.user.id
			}
		)

	@pytest.mark.xfail(reason = "Sin datos para actualizar", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_update_project_without_data_project(self):
		"""
			Intentar actualizar el titulo (title) con
			un valor muy corto
		"""
		project_updated = commands.command_update_project(
			project_id = self.project.id
		)


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_delete_project(self):
		"""
			Validar que se elimine el proyecto
		"""
		project_id = self.project.id

		commands.command_delete_project(project_id = project_id)

		project = self.db.get(Project, project_id)

		assert project == None


	@pytest.mark.xfail(reason = "No existe este proyecto", raises = ValueError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_delete_no_existent_project(self):
		"""
			Intentar eliminar un proyecto que no existe
		"""
		project_id = 100

		commands.command_delete_project(project_id = project_id)

		project = self.db.get(Project, project_id)

		assert project != None


	@pytest.mark.xfail(reason = "Parametro con dato incorreto", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_delete_project_with_wrong_param(self):
		"""
			Intentar pasar como parametro un dato incorreto
		"""
		project_id = "ida12"

		commands.command_delete_project(project_id = project_id)

		project = self.db.get(Project, project_id)

		assert project != None

		"""
			Al usar validate_call, al parecer en este caso, si
			envias como valor en project_id un numero como str
			será tomado como valido.
			Por lo que, puede llevar o no una validación para que 
			solo acepte el tipo de dato indicado.
		"""
	

	@pytest.mark.xfail(reason = "Sin parametro", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_delete_project_without_param(self):
		"""
			Intentar pasar como parametro un dato incorreto
		"""
		commands.command_delete_project()

	
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_project_by_user(self):
		"""
			Obtener todos los proyectos que posee un usuario
		"""

		page = 0
		pageSize = 3
		user_id = self.user.id

		projects = commands.command_get_projects_user(
			page = page,
			pageSize = pageSize,
			user_id = user_id
		)

		assert projects
		assert len(projects) == 1

	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_project_with_no_existent_user(self):
		"""
			Intentar obtener la lista de proyectos
			de un usuario que no existe.
		"""

		page = 0
		pageSize = 3
		user_id = 100

		projects = commands.command_get_projects_user(
			page = page,
			pageSize = pageSize,
			user_id = user_id
		)

		assert not projects
		assert len(projects) == 0


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_project_by_user_with_default_page_and_pageSize(self):
		"""
			Obtener lista de proyectos de un usuario
			usando los valores por defecto de: 'page' y 'pageSize'
		"""
		user_id = 1

		projects = commands.command_get_projects_user(
			user_id = user_id
		)

		assert projects
		assert len(projects) == 1


	@pytest.mark.xfail(reason = "Sin parametro user_id", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_project_by_user_without_user_id(self):
		"""
			Obtener lista de proyectos pero sin pasar como
			parametro 'user_id'
		"""
		page = 0
		pageSize = 3

		projects = commands.command_get_projects_user(
			page = page,
			pageSize = pageSize
		)

		assert projects


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_project_by_user_with_too_big_page(self):
		"""
			Obtener lista de proyectos pero pasando como
			valor de 'page' un valor muy alto
		"""
		page = 10
		pageSize = 3
		user_id = self.user.id

		projects = commands.command_get_projects_user(
			page = page,
			pageSize = pageSize,
			user_id = user_id
		)

		assert not projects
		assert len(projects) == 0


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_project_by_user_with_filter(self):
		"""
			Obtener todos los proyectos de un usuario pero,
			filtrando los proyectos por prioridad
		"""
		project1 = set_project(
			title = "Videojuego de Arcade",
			priority = "baja",
			description = "desarrollar un videojuego"
		)

		project2 = set_project(
			title = "App de mensajeria",
			priority = "baja",
			description = "aplicación movil de mensajes"
		)

		project3 = set_project(
			title = "Traductor AI",
			priority = "alta",
			description = "una app que usa la IA para traducir"
		)

		self.db.add_all([project1, project2, project3])
		self.db.commit()

		page = 0
		pageSize = 5
		user_id = 1
		search = {"priority": "baja"}

		projects = commands.command_get_projects_user(
			page = page,
			pageSize = pageSize,
			user_id = user_id,
			search = search
		)

		assert projects
		assert len(projects) == 2

		page = 0
		pageSize = 5
		user_id = 1
		search = {"priority": "alta"}

		projects = commands.command_get_projects_user(
			page = page,
			pageSize = pageSize,
			user_id = user_id,
			search = search
		)

		assert projects
		assert len(projects) == 1

		page = 0
		pageSize = 5
		user_id = 1
		search = {"priority": "normal"}

		projects = commands.command_get_projects_user(
			page = page,
			pageSize = pageSize,
			user_id = user_id,
			search = search
		)

		assert projects
		assert len(projects) == 1

		page = 0
		pageSize = 5
		user_id = 1
		search = {"priority": "inmediata"}

		projects = commands.command_get_projects_user(
			page = page,
			pageSize = pageSize,
			user_id = user_id,
			search = search
		)

		assert not projects
		assert len(projects) == 0


	@pytest.mark.xfail(reason = "Parametro de busqueda incorreto", raises = ValueError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_project_by_user_with_wrong_filter_value(self):
		"""
			Obtener todos los proyectos de un usuario pero,
			aplicando un valor de filtro incorrecto
		"""
		page = 0
		pageSize = 5
		user_id = self.user.id
		search = {"priority": "ahora"}

		projects = commands.command_get_projects_user(
			page = page,
			pageSize = pageSize,
			user_id = user_id,
			search = search
		)


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_total_project_by_user(self):
		"""
			Obtener el total de proyectos que tiene
			un usuario
		"""
		project1 = set_project(
			title = "Videojuego de Arcade",
			description = "desarrollar un videojuego"
		)

		project2 = set_project(
			title = "App de mensajeria",
			description = "aplicación movil de mensajes"
		)

		project3 = set_project(
			title = "Traductor AI",
			description = "una app que usa la IA para traducir"
		)

		self.db.add_all([project1, project2, project3])
		self.db.commit()

		total = commands.command_get_total_project_user(
			user_id = self.user.id
		)

		assert total == 4


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_total_project_by_user_with_filter(self):
		"""
			Obtener el total de proyectos que tiene
			un usuario pero, aplicando filtro por prioridad
			de los proyectos
		"""
		project1 = set_project(
			title = "Videojuego de Arcade",
			priority = "baja",
			description = "desarrollar un videojuego"
		)

		project2 = set_project(
			title = "App de mensajeria",
			priority = "baja",
			description = "aplicación movil de mensajes"
		)

		project3 = set_project(
			title = "Traductor AI",
			priority = "alta",
			description = "una app que usa la IA para traducir"
		)

		self.db.add_all([project1, project2, project3])
		self.db.commit()

		search = {"priority": "baja"}

		total = commands.command_get_total_project_user(
			user_id = self.user.id,
			search = search
		)

		assert total == 2

		search = {"priority": "alta"}

		total = commands.command_get_total_project_user(
			user_id = self.user.id,
			search = search
		)

		assert total == 1

		search = {"priority": "normal"}

		total = commands.command_get_total_project_user(
			user_id = self.user.id,
			search = search
		)

		assert total == 1

		search = {"priority": "inmediata"}

		total = commands.command_get_total_project_user(
			user_id = self.user.id,
			search = search
		)

		assert total == 0


	@pytest.mark.xfail(reason = "Parametro de busqueda incorreto", raises = ValueError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_total_project_by_user_with_wrong_filter_value(self):
		"""
			Obtener el total de proyectos que tiene
			un usuario pero, aplicando filtro por prioridad
			de los proyectos
		"""
		project1 = set_project(
			title = "Videojuego de Arcade",
			priority = "baja",
			description = "desarrollar un videojuego"
		)

		project2 = set_project(
			title = "App de mensajeria",
			priority = "baja",
			description = "aplicación movil de mensajes"
		)

		project3 = set_project(
			title = "Traductor AI",
			priority = "alta",
			description = "una app que usa la IA para traducir"
		)

		self.db.add_all([project1, project2, project3])
		self.db.commit()

		search = {"priority": "ahora"}

		total = commands.command_get_total_project_user(
			user_id = self.user.id,
			search = search
		)


	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_total_project_with_no_existent_user(self):
		"""
			Obtener el total de proyectos de un usuario
			que no existe
		"""
		user_id = 100

		total = commands.command_get_total_project_user(
			user_id = user_id
		)

		assert total == 0

	@pytest.mark.xfail(reason = "Sin parametro user_id", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_total_project_by_user_without_user_id(self):
		"""
			Intentar obtener el total de proyectos de un
			usuario pero, sin pasar por parametro 'user_id'
		"""
		total = commands.command_get_total_project_user()

		assert total == 0

	@pytest.mark.xfail(reason = "Parametro con dato incorrecto", raises = ValidationError)
	@patch("apps.projects.commands.commands.get_db", get_db)
	def test_get_total_project_by_user_with_wrong_param(self):
		"""
			Intentar obtener el total de proyectos de un
			usuario pero, sin pasar por parametro 'user_id'
		"""
		user_id = "1asb"

		total = commands.command_get_total_project_user(user_id = user_id)

		assert total == 0

