# Sistema de Gerenciamento de Senhas para Clínica Médica

Aplicação desktop em **Python + Tkinter** para emitir, organizar, consultar e chamar senhas de atendimento em uma clínica, aplicando os conceitos de **Estrutura de Dados II**: filas FIFO (lista encadeada), fila de prioridade, modularização e tratamento de exceções.

> Disciplina: Estrutura de Dados II · Equipe: _(preencher nomes dos integrantes)_ · Vídeo de demonstração: _(colar link)_

## Funcionalidades

- 3 especialidades: **Clínica Geral (CG)**, **Cardiologia (CA)** e **Ortopedia (OR)**.
- Emissão de senhas **Normal (N001, N002…)** e **Preferencial (P001, P002…)**.
- Numeração independente por especialidade e categoria; o código exibido inclui a sigla da especialidade para evitar ambiguidade (ex.: `CG-N001`, `CA-N001`, `OR-P002`).
- Filas independentes por especialidade e categoria (6 filas FIFO no total).
- Chamada da próxima senha por especialidade, com registro no histórico e opção de rechamar a última.
- Painel com: última senha chamada, especialidade, categoria, total de pacientes aguardando (geral e por especialidade/categoria) e lista de senhas em espera com a espera estimada.
- Tratamento de erros: fila vazia, nenhuma senha chamada para rechamar, especialidade/categoria inválida e senha que já saiu da fila.

## Como executar

Requisitos: Python 3.9+ com Tkinter (já incluído no instalador oficial para Windows/macOS; no Linux: `sudo apt install python3-tk`).

```bash
python main.py
```

Testes automatizados (não precisam de interface gráfica):

```bash
python -m unittest discover -v
```

## Regra de prioridade adotada

Dentro de **cada especialidade**:

1. **Preferenciais sempre são chamados antes dos normais.**
2. Dentro de cada categoria vale a **ordem de chegada (FIFO)**.

As especialidades não interferem entre si: uma chamada em Cardiologia não altera as filas de Ortopedia.

### Demonstração

Emissões em Clínica Geral, nesta ordem: `CG-N001`, `CG-N002`, `CG-P001`, `CG-N003`, `CG-P002`.

| Chamada | Senha chamada | Motivo |
|---|---|---|
| 1ª | `CG-P001` | Preferencial mais antigo |
| 2ª | `CG-P002` | Ainda há preferencial na fila |
| 3ª | `CG-N001` | Sem preferenciais; normal mais antigo |
| 4ª | `CG-N002` | FIFO entre normais |
| 5ª | `CG-N003` | FIFO entre normais |

Esse comportamento é verificado em `tests/test_sistema.py` (`test_chamada_respeita_prioridade`).

## Tempo estimado de espera

```
espera estimada = pacientes à frente × 30 minutos
```

"À frente" é calculado na **ordem real de atendimento** (preferenciais primeiro), então a estimativa já considera a política de prioridade.

Hipóteses adotadas:

- Cada especialidade tem **um profissional** atendendo, com tempo médio de **30 min** por paciente.
- A estimativa considera apenas quem está na fila no momento; se novos preferenciais chegarem depois, os normais podem esperar mais que o estimado.
- O paciente em atendimento no momento não é somado à espera.

Exemplo: fila de CG com `P001`, `N001`, `N002` → `P001` = sem espera, `N001` = 30 min, `N002` = 1h.

## Estrutura do projeto

```
sistema-senhas-clinica/
├── main.py                  # ponto de entrada
├── clinica/
│   ├── excecoes.py          # exceções do domínio
│   ├── modelos.py           # Categoria, Especialidade, Senha
│   ├── fila.py              # FilaFIFO (lista encadeada) e FilaPrioridade
│   ├── gerenciador.py       # regras: emitir, chamar, prioridade, estimativa
│   └── interface.py         # interface Tkinter
└── tests/
    └── test_sistema.py      # testes unitários
```

Separação de responsabilidades: `interface.py` só cuida da tela; toda a regra de negócio está em `gerenciador.py`, apoiada pelas estruturas de `fila.py`.

## Estruturas de dados

- **`FilaFIFO`**: lista encadeada com ponteiros de início e fim; `enfileirar` e `desenfileirar` em O(1).
- **`FilaPrioridade`**: conjunto de `FilaFIFO`, uma por nível, consultadas em ordem de prioridade (preferencial → normal). Também fornece a ordem real de atendimento usada na lista de espera e na estimativa.
- **`GerenciadorSenhas`**: um dicionário de `FilaPrioridade` por especialidade, contadores por (especialidade, categoria) e lista de histórico.
