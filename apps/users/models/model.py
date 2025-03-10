from typing import List

from sqlalchemy  import ForeignKey
from sqlalchemy  import String
from sqlalchemy.orm  import Mapped 
from sqlalchemy.orm  import mapped_column
from sqlalchemy.orm  import relationship

from apps import Model
from apps.projects.models.model import Project


class User(Model):
	__tablename__ = "user"
	id: Mapped[int] = mapped_column(primary_key = True, index = True, nullable=False, unique=True)
	name: Mapped[str] = mapped_column(String(20), insert_default="")
	email: Mapped[str] = mapped_column(String, unique=True)
	username: Mapped[str] = mapped_column(String(20), unique=True)
	password: Mapped[str] = mapped_column(String)

	projects: Mapped[List[Project]] = relationship(back_populates = "user")


	def __repr__(self):
		return f"User(id={self.id}, name={self.name}, email={self.email}, username={self.username})"



