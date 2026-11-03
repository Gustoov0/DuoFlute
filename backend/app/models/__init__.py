# Importe aqui TODOS os modelos. É isso que permite ao Alembic enxergar as tabelas.
from app.models.user import User  # noqa: F401
from app.models.learning import Section, Unit, Lesson, Exercise  # noqa: F401
from app.models.music import Note, Fingering  # noqa: F401