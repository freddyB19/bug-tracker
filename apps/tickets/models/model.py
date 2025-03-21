import enum
from datetime import datetime

from sqlalchemy import Enum
from sqlalchemy import func
from sqlalchemy  import String
from sqlalchemy  import ForeignKey
from sqlalchemy.orm  import Mapped 
from sqlalchemy.orm import DynamicMapped
from sqlalchemy.orm  import relationship
from sqlalchemy.orm  import mapped_column

from apps import Model

class ChoicesPrority(enum.Enum):
	baja = 0
	normal = 1
	alta = 2
	inmediata = 3 

class ChoicesState(enum.Enum):
	nuevo = 0
	desarrollo = 1
	prueba = 2
	revisión = 3
	terminado = 4

class ChoicesType(enum.Enum):
	abierto = 0
	archivado = 1
	cerrado = 2

class StateTicketHistory(enum.Enum):
	crear = 0
	actualizar = 1


class Ticket(Model):
	__tablename__ = "ticket"
	
	id: Mapped[int] = mapped_column(primary_key = True, index = True, nullable=False, unique=True)
	title: Mapped[str] = mapped_column(String(30))
	description: Mapped[str | None] = mapped_column(String(200))
	priority: Mapped[Enum] = mapped_column(
		Enum(ChoicesPrority), 
		insert_default=ChoicesPrority.baja
	)
	created: Mapped[datetime] = mapped_column(insert_default = func.now())
	updated: Mapped[datetime] = mapped_column(insert_default = func.now(), onupdate=func.now())
	state: Mapped[Enum] = mapped_column(
		Enum(ChoicesState), 
		insert_default=ChoicesState.nuevo
	)
	type: Mapped[Enum] = mapped_column(
		Enum(ChoicesType), 
		insert_default=ChoicesType.abierto
	)
	project_id: Mapped[int] = mapped_column(
		ForeignKey(
			'project.id',
			ondelete = "CASCADE",
			onupdate = "CASCADE"
		)
	)

	project: Mapped['Project'] = relationship(back_populates = "tickets")
	history: DynamicMapped['TicketHistory'] = relationship(back_populates = 'ticket')

	def __repr__(self):
		return f"Ticket(id={self.id}, title={self.title}, priority={self.priority}, state={self.state}, type={self.type})"


class TicketHistory(Model):
	__tablename__ = "ticket_history"
	
	id: Mapped[int] = mapped_column(primary_key = True, index = True, nullable=False, unique=True)
	created: Mapped[datetime] = mapped_column(insert_default = func.now())
	message: Mapped[str] = mapped_column(String(250))
	state: Mapped[Enum] = mapped_column(
		Enum(StateTicketHistory), 
		insert_default=StateTicketHistory.crear
	)
	ticket_id: Mapped[int | None] = mapped_column(
		ForeignKey(
			'ticket.id',
			ondelete = "CASCADE",
			onupdate = "CASCADE"
		)
	)

	ticket: Mapped[Ticket] = relationship(back_populates = 'history')
	
	def __repr__(self):
		return f"TicketHistory(id={self.id}, title={self.title}, priority={self.priority}, state={self.state}, type={self.type})"