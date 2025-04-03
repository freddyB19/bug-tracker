from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

from sqlalchemy  import String
from sqlalchemy.orm  import Mapped 
from sqlalchemy.orm  import mapped_column

Model = declarative_base()


class User(Model):
	__tablename__ = "user"
	id: Mapped[int] = mapped_column(primary_key = True, index = True, nullable=False, unique=True)
	name: Mapped[str] = mapped_column(String(20), insert_default="")
	email: Mapped[str] = mapped_column(String, unique=True)
	username: Mapped[str] = mapped_column(String(20), unique=True)
	password: Mapped[str] = mapped_column(String)