import pytest

from sqlalchemy.exc import IntegrityError

from tests import ENGINE
from tests import SESSION

from apps import Model
from apps.users.models import User
from apps.projects.models import Project


class TestProjectDB:

	def setup_method(self):
		Model.metadata.drop_all(ENGINE)
		Model.metadata.create_all(ENGINE)

		self.db = SESSION

		user = user = User(
			name = 'bolivar',
			email = 'bolivar@gmail.com',
			username = 'bolivar19',
			password = '12345'
		)

		self.db.add(user)
		self.db.commit()
		self.db.refresh(user)

		self.project = Project(
			title = "Proyecto de tests",
			description = "Proyecto para hacer tests",
			user_id = user.id
		)

		self.user = user


	def teardown_method(self):
		self.db.rollback()
		self.db.close()


	def test_create_project(self):
		""" Validar que se cree un nuevo proyecto """
		
		new_project = self.project
		
		self.db.add(new_project)
		self.db.commit()
		self.db.refresh(new_project)

		assert new_project.id == 1
		assert new_project.title == self.project.title
		assert new_project.user_id == self.project.user_id
		assert new_project.priority == self.project.priority
		assert new_project.description == self.project.description


	@pytest.mark.xfail(reason = "Datos incompletos", raises = IntegrityError)
	def test_create_project_with_incomplete_data(self):
		""" 
			Intantar crear un proyecto con datos incompletos
		"""
		project = Project(
			user_id = self.user.id
		)

		self.db.add(project)
		self.db.commit()

	@pytest.mark.xfail(reason = "Sin titulo", raises = IntegrityError)
	def test_create_project_without_title(self):
		"""
			Intenar crear un proyecto sin 'titulo'
		"""
		project = Project(
			description = "descripción de un proyecto",
			user_id = self.user.id
		)

		self.db.add(project)
		self.db.commit()
		self.db.refresh(project)

		assert project.id == 2

	@pytest.mark.xfail(reason = "Sin descripción", raises = IntegrityError)
	def test_create_project_without_description(self):
		"""
			Intenar crear un proyecto sin 'descripción'
		"""
		
		project = Project(
			title = "titulo de un proyecto",
			user_id = self.user.id
		)

		self.db.add(project)
		self.db.commit()
		self.db.refresh(project)

		assert project.id == 2


	def test_create_project_with_wrong_title(self):
		"""
			Intentar crear un proyecto con un 'titulo' mayor
			a la restricción indicada en la tabla. 
		"""
		titulo = """
			Lorem ipsum dolor sit amet consectetur adipisicing elit. 
			Aspernatur, magni nostrum est deserunt officia quas illo quis, 
			aliquam unde animi quod debitis voluptates recusandae ut minima, 
			eos dicta molestiae accusamus?
		"""
		project = Project(
			title = titulo,
			description = "descripción del proyecto",
			user_id = self.user.id
		)
		self.db.add(project)
		self.db.commit()

		assert project.id == 1
		"""
		Se debe crear una validación que impida que se cree 
		un proyecto con una titulo que supere el limite
		de longitud establecido en la tabla
		"""

	
	def test_create_project_with_wrong_description(self):
		"""
			Intentar crear un proyecto con una 'descripción' mayor
			a la restricción indicada en la tabla. 
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
		project = Project(
			title = "titulo de proyecto",
			description = descripcion,
			user_id = self.user.id
		)
		self.db.add(project)
		self.db.commit()

		assert project.id == 1

		"""
		Se debe crear una validación que impida que se cree 
		un proyecto con una descripción que supere el limite
		de longitud establecido en la tabla
		"""

	@pytest.mark.xfail(reason = "Opción erronea de prioridad", raises = (KeyError, LookupError))
	def test_create_project_with_wrong_priority(self):
		"""
			Intentar crear un proyecto con una 'prioridad'
			distinta a las opciones disponibles
		"""
		prioridad = "ahora" 
		
		project = Project(
			title = "titulo de proyecto",
			description = "descripción del proyecto",
			priority = prioridad,
			user_id = self.user.id
		)
		self.db.add(project)
		self.db.commit()

	
	def test_create_project_without_user(self):
		"""
			Intentar crear un proyecto sin usuario
		"""
		project = Project(
			title = "titulo de proyecto",
			description = "descripción del proyecto",
		)
		self.db.add(project)
		self.db.commit()
		self.db.refresh(project)

		assert project.id == 1
		assert project.user_id == None

		"""
		Se debe tener una validación que impida que se cree un
		proyecto sin usuario
		"""
