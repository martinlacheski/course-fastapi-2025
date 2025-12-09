# Importamos las librerias de os y dotenv
import os
from dotenv import load_dotenv

from logging.config import fileConfig

# importamos create_engine de sqlalchemy
from sqlalchemy import create_engine, engine_from_config
from sqlalchemy import pool

from alembic import context


# Importamos SQLModel
from sqlmodel import SQLModel

# Importamos los modelos
from app.api.auth.model import User
from app.api.label.model import Label, NoteLabelLink
from app.api.note.model import Note
from app.api.share.model import NoteShare, LabelShare


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

# Cargamos las variables de entorno
load_dotenv()

# Obtenemos la URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

# Obtenemos el metadata de la base de datos
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url")
    # Obtenemos la URL de la base de datos de las variables de entorno
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,  # Comparamos el tipo de datos
        compare_server_default=True,  # Comparamos el valor por defecto
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # connectable = engine_from_config(
    #     config.get_section(config.config_ini_section, {}),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )

    # Creamos el engine de la base de datos
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
        future=True,  # Usamos el futuro de SQLAlchemy
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            compare_type=True,  # Comparamos el tipo de datos
            compare_server_default=True  # Comparamos el valor por defecto
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
