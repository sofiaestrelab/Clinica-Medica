"""Estruturas de dados: fila FIFO (lista encadeada) e fila de prioridade."""
from __future__ import annotations

from typing import Any, Hashable, Iterable, Iterator

from .excecoes import CategoriaInvalidaError, FilaVaziaError


class _No:
    __slots__ = ("valor", "proximo")

    def __init__(self, valor: Any) -> None:
        self.valor = valor
        self.proximo: _No | None = None


class FilaFIFO:
    """Fila FIFO implementada com lista encadeada (enfileirar/desenfileirar em O(1))."""

    def __init__(self) -> None:
        self._inicio: _No | None = None
        self._fim: _No | None = None
        self._tamanho = 0

    def enfileirar(self, valor: Any) -> None:
        no = _No(valor)
        if self._fim is None:
            self._inicio = self._fim = no
        else:
            self._fim.proximo = no
            self._fim = no
        self._tamanho += 1

    def desenfileirar(self) -> Any:
        if self._inicio is None:
            raise FilaVaziaError("A fila está vazia.")
        no = self._inicio
        self._inicio = no.proximo
        if self._inicio is None:
            self._fim = None
        self._tamanho -= 1
        return no.valor

    def espiar(self) -> Any:
        if self._inicio is None:
            raise FilaVaziaError("A fila está vazia.")
        return self._inicio.valor

    def esta_vazia(self) -> bool:
        return self._tamanho == 0

    def __len__(self) -> int:
        return self._tamanho

    def __iter__(self) -> Iterator[Any]:
        atual = self._inicio
        while atual is not None:
            yield atual.valor
            atual = atual.proximo


class FilaPrioridade:
    """Fila de prioridade por níveis.

    Cada nível é uma FilaFIFO independente. Os níveis são informados em ordem
    decrescente de prioridade: o primeiro nível é sempre atendido antes dos
    demais, e dentro de cada nível vale a ordem de chegada (FIFO).
    """

    def __init__(self, niveis: Iterable[Hashable]) -> None:
        self._niveis = list(niveis)
        if not self._niveis:
            raise ValueError("É necessário ao menos um nível de prioridade.")
        self._filas = {nivel: FilaFIFO() for nivel in self._niveis}

    def fila(self, nivel: Hashable) -> FilaFIFO:
        if nivel not in self._filas:
            raise CategoriaInvalidaError(f"Nível de prioridade inválido: {nivel!r}.")
        return self._filas[nivel]

    def enfileirar(self, valor: Any, nivel: Hashable) -> None:
        self.fila(nivel).enfileirar(valor)

    def desenfileirar(self) -> Any:
        for nivel in self._niveis:
            fila = self._filas[nivel]
            if not fila.esta_vazia():
                return fila.desenfileirar()
        raise FilaVaziaError("Não há ninguém aguardando.")

    def esta_vazia(self) -> bool:
        return len(self) == 0

    def __len__(self) -> int:
        return sum(len(f) for f in self._filas.values())

    def __iter__(self) -> Iterator[Any]:
        """Itera na ordem real de atendimento."""
        for nivel in self._niveis:
            yield from self._filas[nivel]
