"""Regras de negócio: emissão, chamada, prioridade e estimativa de espera."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .excecoes import (
    CategoriaInvalidaError,
    EspecialidadeInvalidaError,
    FilaVaziaError,
    OperacaoInvalidaError,
)
from .fila import FilaPrioridade
from .modelos import ESPECIALIDADES_PADRAO, Categoria, Especialidade, Senha

TEMPO_MEDIO_MINUTOS = 30


def formatar_minutos(minutos: int) -> str:
    """Formata minutos como '45 min' ou '1h 30min'."""
    if minutos <= 0:
        return "sem espera"
    horas, resto = divmod(minutos, 60)
    if horas == 0:
        return f"{resto} min"
    return f"{horas}h {resto:02d}min" if resto else f"{horas}h"


class GerenciadorSenhas:
    """Controla as filas de todas as especialidades.

    Política de prioridade (por especialidade):
      1. Preferenciais são sempre chamados antes dos normais.
      2. Dentro de cada categoria vale a ordem de chegada (FIFO).
    Cada especialidade tem um profissional (hipótese) e as filas são independentes.
    """

    def __init__(
        self,
        especialidades: Iterable[Especialidade] = ESPECIALIDADES_PADRAO,
        tempo_medio: int = TEMPO_MEDIO_MINUTOS,
    ) -> None:
        if tempo_medio <= 0:
            raise ValueError("O tempo médio de atendimento deve ser positivo.")
        self.tempo_medio = tempo_medio
        self._especialidades = {e.sigla: e for e in especialidades}
        if not self._especialidades:
            raise ValueError("É necessário ao menos uma especialidade.")
        ordem = [Categoria.PREFERENCIAL, Categoria.NORMAL]  # maior -> menor prioridade
        self._filas = {sigla: FilaPrioridade(ordem) for sigla in self._especialidades}
        self._contadores = {
            (sigla, cat): 0 for sigla in self._especialidades for cat in Categoria
        }
        self._historico: list[Senha] = []
        self._ultima: Senha | None = None

    # ---------- consultas básicas ----------
    @property
    def especialidades(self) -> list[Especialidade]:
        return list(self._especialidades.values())

    @property
    def historico(self) -> list[Senha]:
        return list(self._historico)

    @property
    def ultima_chamada(self) -> Senha | None:
        return self._ultima

    def especialidade(self, sigla: str) -> Especialidade:
        if not isinstance(sigla, str) or sigla not in self._especialidades:
            raise EspecialidadeInvalidaError("Selecione uma especialidade válida.")
        return self._especialidades[sigla]

    # ---------- operações ----------
    def emitir(self, sigla: str, categoria: Categoria) -> Senha:
        esp = self.especialidade(sigla)
        if not isinstance(categoria, Categoria):
            raise CategoriaInvalidaError("Selecione uma categoria de atendimento válida.")
        self._contadores[(sigla, categoria)] += 1
        senha = Senha(esp, categoria, self._contadores[(sigla, categoria)])
        self._filas[sigla].enfileirar(senha, categoria)
        return senha

    def chamar_proxima(self, sigla: str) -> Senha:
        esp = self.especialidade(sigla)
        fila = self._filas[sigla]
        if fila.esta_vazia():
            raise FilaVaziaError(f"Não há pacientes aguardando em {esp.nome}.")
        senha = fila.desenfileirar()
        senha.chamada_em = datetime.now()
        self._historico.append(senha)
        self._ultima = senha
        return senha

    def rechamar_ultima(self) -> Senha:
        if self._ultima is None:
            raise OperacaoInvalidaError("Nenhuma senha foi chamada ainda.")
        return self._ultima

    # ---------- filas ----------
    def em_espera(self, sigla: str | None = None) -> list[Senha]:
        """Senhas aguardando, na ordem de atendimento (por especialidade)."""
        if sigla is not None:
            self.especialidade(sigla)
            return list(self._filas[sigla])
        resultado: list[Senha] = []
        for s in self._especialidades:
            resultado.extend(self._filas[s])
        return resultado

    def quantidade(self, sigla: str, categoria: Categoria | None = None) -> int:
        self.especialidade(sigla)
        if categoria is None:
            return len(self._filas[sigla])
        return len(self._filas[sigla].fila(categoria))

    def total_em_espera(self) -> int:
        return sum(len(f) for f in self._filas.values())

    # ---------- estimativa ----------
    def pacientes_a_frente(self, senha: Senha) -> int:
        for posicao, s in enumerate(self.em_espera(senha.especialidade.sigla)):
            if s is senha:
                return posicao
        raise OperacaoInvalidaError(f"A senha {senha} não está mais na fila de espera.")

    def estimar_espera(self, senha: Senha) -> int:
        """Minutos de espera = pacientes à frente (na ordem real) x tempo médio.

        Hipótese: nenhum preferencial novo chega depois; se chegar, normais
        podem esperar mais que o estimado.
        """
        return self.pacientes_a_frente(senha) * self.tempo_medio
