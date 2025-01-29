from sqlalchemy  import ForeignKey
from sqlalchemy  import String
from sqlalchemy.orm  import Mapped 
from sqlalchemy.orm  import mapped_column
from sqlalchemy.orm  import relationship

from apps import Model



class User(Model):
	__tablename__ = "user"

	id: Mapped[int] = mapped_column(primaty_key=True, index=True)
	name: Mapped[str] = mapped_column(String(20), insert_default="")
	email: Mapped[str] = mapped_column(String, unique=True)
	username: Mapped[str] = mapped_column(String, unique=True)
	password: Mapped[str] = mapped_column(String)


	projects: Mapped[List["Projects"]] = relationship(
		back_populates = "user" 
	)

	def __repr__(self):
		return f"User(id={self.id}, name={self.name}, email={self.email}, username={self.username})"



