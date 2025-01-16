# types.py
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.types import JSON


class JSONField(TypeEngine):
    pass


# Compiladores específicos para cada dialecto
@compiles(JSONField, "postgresql")
def compile_postgresql_jsonfield(type_, compiler, **kw):
    return compiler.visit_JSONB(JSONB())


@compiles(JSONField, "sqlite")
def compile_sqlite_jsonfield(type_, compiler, **kw):
    return compiler.visit_JSON(JSON())
