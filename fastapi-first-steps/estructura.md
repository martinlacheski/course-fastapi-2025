app/
├── main.py # Punto de entrada de la aplicación
├── core/
│ ├── config.py # Settings generales (env, etc.)
│ ├── db.py # Session, Base de SQLAlchemy/SQLModel
│ ├── security.py # Seguridad (hash, etc.)
│ ├── middleware.py # Middleware (logging, etc.)
│ └── utils.py # Utilidades generales
├── api/
│ ├── auth/
│ │ ├── **init**.py
│ │ ├── router.py # Rutas de autenticación
│ │ ├── schemas.py # Esquemas Pydantic (Token, TokenData, UserPublic, etc.)
│ ├── post/
│ │ ├── **init**.py
│ │ ├── models.py # Modelos ORM de Post
│ │ ├── schemas.py # Esquemas Pydantic (PostCreate, PostRead, etc.)
│ │ ├── repository.py # Acceso a datos (queries a la BD)
│ │ ├── service.py # Lógica de negocio específica de posts
│ │ └── routes.py # FastAPI router para /posts
│ ├── tag/
│ │ ├── **init**.py
│ │ ├── models.py # Modelos ORM de Tag
│ │ ├── schemas.py # Esquemas Pydantic (TagCreate, TagRead, etc.)
│ │ ├── repository.py # Acceso a datos (queries a la BD)
│ │ ├── service.py # Lógica de negocio específica de tags
│ │ └── routes.py # FastAPI router para /tags
│ └── user/
│ ├── **init**.py
│ ├── models.py # Modelos ORM de User  
│ ├── schemas.py # Esquemas Pydantic (UserCreate, UserRead, etc.)
│ ├── repository.py # Acceso a datos (queries a la BD)
│ ├── service.py # Lógica de negocio específica de users
│ └── routes.py # FastAPI router para /users
├── services/
│ ├── file_storage.py # Almacenamiento de archivos
│ ├── pagination.py # Paginación de resultados
├── seeds/
│ ├── **init**.py
│ ├── user.py # Semillas de users
│ ├── post.py # Semillas de posts
│ └── tag.py # Semillas de tags
├── utils/
│ ├── **init**.py
│ ├──
│ └──
├── migrations/
│ └── **init**.py
└── tests/
└── **init**.py
