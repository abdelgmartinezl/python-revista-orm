from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import mysql.connector

# Conexion a la base de datos
DATABASE_URL = "mysql+mysqlconnector://root@localhost:3306/revista"
engine = create_engine(DATABASE_URL, echo=False)

# Clase base para trabajar con SQLAlchemy
Base = declarative_base()

# Relacion 1:1
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    address = relationship("Address", uselist=False, back_populates="user")

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    email = Column(String(50))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="address")

# Relacion 1:M
class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    content = Column(String(150))
    author_id = Column(Integer, ForeignKey('users_one_to_many.id'))
    author = relationship("UserOneToMany", back_populates="articles")

class UserOneToMany(Base):
    __tablename__ = "users_one_to_many"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    articles = relationship("Article", back_populates="author")

# Relacion M:M
association_table = Table('user_group_association', Base.metadata,
                          Column('user_id', Integer, ForeignKey('users_many_to_many.id')),
                          Column('group_id', Integer, ForeignKey('groups.id'))
                          )

class UserManyToMany(Base):
    __tablename__ = "users_many_to_many"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    groups = relationship("Group", secondary=association_table, back_populates="users")

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    users = relationship("UserManyToMany", secondary=association_table, back_populates="groups")

# Crear estructuras en la base de datos
Base.metadata.create_all(engine)

# Sesion de base de datos
Session = sessionmaker(bind=engine)
session = Session()

# Insertar datos 1:1
user_one_to_one = User(username='petra')
address_one_to_one = Address(email='petra@ejemplo.com', user=user_one_to_one)
user_one_to_one.address = address_one_to_one

# Insertar datos 1:M
user_one_to_many = UserOneToMany(username='calixtra',
                                 articles=[
                                     Article(title='Articulo X', content='Contenido de articulo X'),
                                     Article(title='Articulo Y', content='Contenido de articulo Y')
                                 ])

# Insertar datos M:M
user_many_to_many_1 = UserManyToMany(username="susana")
user_many_to_many_2 = UserManyToMany(username="toribia")
group = Group(name="deudoras",
              users=[user_many_to_many_1,user_many_to_many_2])

session.add_all([user_one_to_one, user_one_to_many,
                 user_many_to_many_1, user_many_to_many_2,
                 group])

session.commit()

# Consultar todos los registros
print("Relacion 1:1")
users = session.query(User).all()
for user in users:
    print(user.username)

print("Relacion 1:M")
articles = session.query(UserOneToMany).all()
for article in articles:
    print(article.username)

print("Relacion M:M")
groups = session.query(Group).all()
for group in groups:
    print(group.name)

# Consultar con filtro
print("Consulta con Filtro")
user_query = session.query(User).filter_by(username='petra').first()
print(user_query.username)

# Consultar con join
print("Consulta con Join")
article_query = session.query(Article).join(UserOneToMany).filter(UserOneToMany.username == 'calixtra').all()
for article in article_query:
    print(article.title, article.content)

session.close()