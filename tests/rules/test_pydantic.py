from pycodegate.rules.pydantic import PydanticRules


def _run(source: str) -> list:
    return PydanticRules().check(source, "models.py")


def test_optional_no_default_flagged():
    source = """
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    name: str
    email: Optional[str]
"""
    diags = _run(source)
    assert any(d.rule == "pydantic-optional-no-default" for d in diags)


def test_optional_with_default_ok():
    source = """
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    name: str
    email: Optional[str] = None
"""
    diags = _run(source)
    assert not any(d.rule == "pydantic-optional-no-default" for d in diags)


def test_optional_union_none_no_default_flagged():
    source = """
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str | None
"""
    diags = _run(source)
    assert any(d.rule == "pydantic-optional-no-default" for d in diags)


def test_optional_union_none_with_default_ok():
    source = """
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str | None = None
"""
    diags = _run(source)
    assert not any(d.rule == "pydantic-optional-no-default" for d in diags)


def test_validator_no_return_flagged():
    source = """
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        assert len(v) > 0
"""
    diags = _run(source)
    assert any(d.rule == "pydantic-validator-no-return" for d in diags)


def test_validator_with_return_ok():
    source = """
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        assert len(v) > 0
        return v
"""
    diags = _run(source)
    assert not any(d.rule == "pydantic-validator-no-return" for d in diags)


def test_v1_validator_import_flagged():
    source = """
from pydantic import BaseModel, validator

class User(BaseModel):
    name: str

    @validator("name")
    @classmethod
    def validate_name(cls, v):
        return v
"""
    diags = _run(source)
    assert any(d.rule == "pydantic-v1-validator" for d in diags)


def test_v1_validator_import_ok():
    source = """
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return v
"""
    diags = _run(source)
    assert not any(d.rule == "pydantic-v1-validator" for d in diags)


def test_v1_config_flagged():
    source = """
from pydantic import BaseModel

class User(BaseModel):
    name: str

    class Config:
        orm_mode = True
"""
    diags = _run(source)
    assert any(d.rule == "pydantic-v1-config" for d in diags)


def test_v1_config_ok():
    source = """
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
"""
    diags = _run(source)
    assert not any(d.rule == "pydantic-v1-config" for d in diags)


def test_init_override_no_super_flagged():
    source = """
from pydantic import BaseModel

class User(BaseModel):
    name: str

    def __init__(self, **kwargs):
        self.custom = True
"""
    diags = _run(source)
    assert any(d.rule == "pydantic-init-override" for d in diags)


def test_init_override_with_super_ok():
    source = """
from pydantic import BaseModel

class User(BaseModel):
    name: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.custom = True
"""
    diags = _run(source)
    assert not any(d.rule == "pydantic-init-override" for d in diags)


def test_field_validator_no_classmethod_flagged():
    source = """
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str

    @field_validator("name")
    def validate_name(cls, v):
        return v
"""
    diags = _run(source)
    assert any(d.rule == "pydantic-validator-no-classmethod" for d in diags)


def test_field_validator_with_classmethod_ok():
    source = """
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return v
"""
    diags = _run(source)
    assert not any(d.rule == "pydantic-validator-no-classmethod" for d in diags)
