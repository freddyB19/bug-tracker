import enum
from typing import List

from datetime import datetime
from sqlalchemy import Enum
from sqlalchemy  import String
from sqlalchemy import func
from sqlalchemy  import ForeignKey
from sqlalchemy.orm  import Mapped 
from sqlalchemy.orm  import relationship
from sqlalchemy.orm  import mapped_column

from apps import Model


class ChoicesPrority(enum.Enum):
	baja = 0
	normal = 1
	alta = 2
	inmediata = 3

class Project(Model):
	__tablename__ = "project"
	
	id: Mapped[int] = mapped_column(primary_key = True, index = True, nullable=False, unique=True)
	title: Mapped[str] = mapped_column(String(30), nullable=False)
	priority: Mapped[Enum] = mapped_column(Enum(ChoicesPrority), insert_default=ChoicesPrority.baja)
	description: Mapped[str] = mapped_column(String(200))
	created: Mapped[datetime] = mapped_column(insert_default = func.now())
	updated: Mapped[datetime] = mapped_column(insert_default = func.now(), onupdate=func.now())
	user_id: Mapped[int] = mapped_column(
		ForeignKey(
			'user.id',
			ondelete = 'CASCADE',
			onupdate = 'CASCADE'
		)
	)

	user: Mapped['User'] = relationship(back_populates = "projects")
	tickets: Mapped[List['Ticket']] = relationship(back_populates = "project")


	def __repr__(self):
		return f"Project(id={self.id}, title={self.title}, priority={self.priority})"
