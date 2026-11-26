"""Modelos de dados: categorias, especialidades e senhas."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Categoria(Enum):
    """Categoria de atendimento. O valor é (prefixo da senha, rótulo)."""

    PREFERENCIAL = ("P", "Preferencial")
    NORMAL = ("N", "Normal")

    @property
    def prefixo(self) -> str:
        return self.value[0]

    @property
    def rotulo(self) -> str:
        return self.value[1]


@dataclass(frozen=True)
class Especialidade:
    sigla: str
    nome: str


ESPECIALIDADES_PADRAO = (
    Especialidade("CG", "Clínica Geral"),
    Especialidade("CA", "Cardiologia"),
    Especialidade("OR", "Ortopedia"),
)


@dataclass
class Senha:
    """Senha de atendimento.

    O código inclui a sigla da especialidade para evitar ambiguidade, já que
    cada especialidade tem sua própria numeração (ex.: CG-N001, CA-P002).
    """

    especialidade: Especialidade
    categoria: Categoria
    numero: int
    emitida_em: datetime = field(default_factory=datetime.now)
    chamada_em: datetime | None = None

    @property
    def codigo(self) -> str:
        return f"{self.especialidade.sigla}-{self.categoria.prefixo}{self.numero:03d}"

    def __str__(self) -> str:
        return self.codigo
