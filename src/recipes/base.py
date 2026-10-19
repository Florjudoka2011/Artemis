"""
Protocolo base para todas las recetas paramétricas de Artemis.

Contrato:
- Recibe un BaseModel validado (capa 1 ya pasada).
- Devuelve un cq.Workplane con el sólido construido.
- No tiene efectos secundarios (función pura).
- Lanza ValueError para violaciones geométricas (capa 2).
"""

from typing import Protocol, runtime_checkable

import cadquery as cq
from pydantic import BaseModel


@runtime_checkable
class Receta(Protocol):
    def __call__(self, params: BaseModel) -> cq.Workplane:
        """Construye y retorna el sólido 3D a partir de los parámetros validados."""
        ...
