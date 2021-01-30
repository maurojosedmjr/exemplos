from dataclasses import dataclass
from typing import Optional, Union, Dict
from datetime import datetime


class DataClassModel:
    def __post_init__(self):
        for k, t in self.__annotations__.items():
            if not isinstance(getattr(self, k), v):
                raise Exception(f"Tipo de dado inválido campo <{k}> aceita tipo <{t}>, foi passado: {self.__getattribute__(k)}")

@dataclass
class InputClient(DataClassModel):
    name: str

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name")
        self.__post_init__()
    
    def get(self, field: str):
        return getattr(self, field, None)
    
    def set(self, field: str, value: Optional[Union[str, datetime]]):
        self.__setattr__(field, value)
