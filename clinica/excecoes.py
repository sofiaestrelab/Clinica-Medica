"""Exceções específicas do domínio da clínica."""


class ErroClinica(Exception):
    """Classe base para todos os erros do sistema."""


class FilaVaziaError(ErroClinica):
    """Operação de remoção/consulta em uma fila sem elementos."""


class EspecialidadeInvalidaError(ErroClinica):
    """Especialidade inexistente ou não informada."""


class CategoriaInvalidaError(ErroClinica):
    """Categoria de atendimento inexistente ou não informada."""


class OperacaoInvalidaError(ErroClinica):
    """Operação incompatível com o estado atual das filas."""
