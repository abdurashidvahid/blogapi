from sqlalchemy import ForeignKey,create_engine,String
from sqlalchemy.orm import Session,sessionmaker,Mapped,mapped_column,DeclarativeBase,relationship




class Base(DeclarativeBase):
   pass
class User(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(primary_key=True)
    username:Mapped[str] = mapped_column()
    email:Mapped[str] = mapped_column(unique=True)
    hashed_password:Mapped[str]
    posts:Mapped[list["Post"]] = relationship(back_populates="user") 

class Post(Base):
    __tablename__ = "posts"
    id:Mapped[int] = mapped_column(primary_key=True)
    content:Mapped[str]
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"))
    user:Mapped["User"] = relationship(back_populates="posts")
    


engine = create_engine("sqlite:///practice.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind= engine)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()