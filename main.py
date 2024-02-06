from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Conexion a la base de datos
DATABASE_URL = "mysql+mysqlconnector://root@localhost:3306/revista"
engine = create_engine(DATABASE_URL, echo=False)

# Clase base para trabajar con SQLAlchemy
Base = declarative_base()

# Relacion M:M
association_table = Table('user_group_association', Base.metadata,
                          Column('user_id', Integer, ForeignKey('users.id')),
                          Column('group_id', Integer, ForeignKey('groups.id'))
                          )

# Relacion 1:1
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    address = relationship("Address", uselist=False, back_populates="user")
    articles = relationship("Article", back_populates="author", uselist=True)
    groups = relationship("Group", secondary=association_table, back_populates="users", uselist=True)

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
    author_id = Column(Integer, ForeignKey('users.id'))
    author = relationship("User", back_populates="articles", uselist=True)

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    users = relationship("User", secondary=association_table, back_populates="groups", uselist=True)

# Crear estructuras en la base de datos
Base.metadata.create_all(engine)

# Sesion de base de datos
Session = sessionmaker(bind=engine)
session = Session()

# Insertar datos 1:1
user1 = User(username='petra')
address1 = Address(email='petra@ejemplo.com', user=user1)
user1.address = address1

# Insertar datos 1:M
user2 = User(username='calixtra')
articulo1 = Article(title='Articulo X', content='Contenido de articulo X', author_id=user2.id)
articulo2 = Article(title='Articulo Y', content='Contenido de articulo Y', author_id=user2.id)

# Insertar datos M:M
user3 = User(username='susana')
user4 = User(username='toribia')
group1 = Group(name="deudoras", users=[user3, user4])

session.add_all([user1, address1, user2, articulo1, articulo2, user3, user4, group1])

session.commit()

# Consultar todos los registros
print("Relacion 1:1")
users = session.query(User).all()
for user in users:
    print(user.username)

print("Relacion 1:M")
articles = session.query(Article).all()
for article in articles:
    print(article.title)

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
article_query = session.query(Article).join(User).filter(User.username == 'calixtra').all()
for article in article_query:
    print(article.title, article.content)

session.close()