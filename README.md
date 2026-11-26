# Sistema de Gerenciamento de Senhas para Clínica Médica

Aplicação em **Python + Tkinter** para emitir, organizar, consultar e chamar senhas de atendimento em uma clínica, aplicando os conceitos de **Estrutura de Dados II**: filas FIFO (lista encadeada), fila de prioridade, modularização e tratamento de exceções.

> Disciplina: Estrutura de Dados II · Aluna: Sofia Estrela Bernardes · Link vídeo: https://youtu.be/UhBWugdk8Fc

## Objetivo
 
Informatizar o gerenciamento de senhas de atendimento de uma clínica médica, melhorando a organização das filas, reduzindo o tempo de espera e garantindo o atendimento prioritário. O projeto demonstra, na prática, o uso de **filas FIFO**, **filas de prioridade**, **modularização** e **tratamento de exceções**, com interface gráfica em **Tkinter**.
 
## Funcionalidades desenvolvidas
 
- **Três especialidades:** Clínica Geral (CG), Cardiologia (CA) e Ortopedia (OR).
- **Emissão de senhas** nas categorias Normal (N001, N002…) e Preferencial (P001, P002…). A numeração é independente por especialidade e categoria, e o código exibido inclui a sigla da especialidade para evitar ambiguidade (ex.: `CG-N001`, `CA-N001`, `OR-P002`).
- **Filas independentes** para cada especialidade e categoria (6 filas FIFO no total).
- **Atendimento prioritário**, conforme a regra descrita mais abaixo.
- **Chamada de senhas** por especialidade, com identificação da especialidade, da categoria e do número. A senha chamada sai da fila de espera e é registrada no histórico. Também é possível rechamar a última senha.
- **Painel de atendimento** com: última senha chamada, especialidade, categoria, quantidade de pacientes aguardando (total e por especialidade/categoria) e relação de senhas em espera.
- **Tempo estimado de espera** com base em 30 minutos por atendimento (detalhes abaixo).
- **Tratamento de exceções:** fila vazia, ausência de pacientes aguardando, entradas inválidas (especialidade ou categoria não selecionada), rechamada sem nenhuma senha chamada e estimativa de uma senha que já saiu da fila. A interface exibe uma mensagem clara em cada caso.
## Estruturas de dados utilizadas
 
| Estrutura | Onde | Descrição |
|---|---|---|
| `FilaFIFO` | `clinica/fila.py` | Fila implementada com **lista encadeada**, com ponteiros de início e fim. `enfileirar` e `desenfileirar` em O(1). |
| `FilaPrioridade` | `clinica/fila.py` | Conjunto de `FilaFIFO`, uma por nível de prioridade, consultadas da maior para a menor prioridade. Também fornece a ordem real de atendimento. |
| Dicionário de filas | `clinica/gerenciador.py` | Uma `FilaPrioridade` por especialidade, acessada pela sigla. |
| Contadores | `clinica/gerenciador.py` | Dicionário indexado por (especialidade, categoria) que garante a numeração sequencial de cada senha. |
| Lista de histórico | `clinica/gerenciador.py` | Registro, em ordem de chamada, das senhas já atendidas. |
 
## Regra de prioridade
 
Dentro de **cada especialidade**:
 
1. **Pacientes preferenciais são sempre chamados antes dos normais.**
2. Dentro de cada categoria vale a **ordem de chegada (FIFO)**.
As especialidades são independentes: chamar uma senha em Cardiologia não altera as filas de Ortopedia.
 
### Demonstração
 
Senhas emitidas em Clínica Geral, nesta ordem: `CG-N001`, `CG-N002`, `CG-P001`, `CG-N003`, `CG-P002`.
 
| Chamada | Senha chamada | Motivo |
|---|---|---|
| 1ª | `CG-P001` | Preferencial mais antigo |
| 2ª | `CG-P002` | Ainda há preferencial aguardando |
| 3ª | `CG-N001` | Sem preferenciais; normal mais antigo |
| 4ª | `CG-N002` | FIFO entre normais |
| 5ª | `CG-N003` | FIFO entre normais |
 
Esse comportamento é verificado automaticamente em `tests/test_sistema.py` (`test_chamada_respeita_prioridade`).
 
### Tempo estimado de espera
 
```
espera estimada = pacientes à frente × 30 minutos
```
 
Os "pacientes à frente" são contados na **ordem real de atendimento** (preferenciais primeiro), portanto a estimativa já considera a política de prioridade.
 
Hipóteses adotadas:
 
- Cada especialidade tem **um profissional** atendendo, com tempo médio de **30 minutos** por paciente.
- A estimativa considera apenas quem está na fila no momento. Se novos preferenciais chegarem depois, os normais podem esperar mais que o estimado.
- O paciente que está sendo atendido no momento não entra na conta.
Exemplo: fila de Clínica Geral com `P001`, `N001`, `N002` → `P001`: sem espera; `N001`: 30 min; `N002`: 1h.
 
## Instalação e execução
 
**Requisitos:** Python 3.9 ou superior com Tkinter. Não há bibliotecas externas para instalar.
 
1. Verifique o Python e o Tkinter:
```bash
python --version
python -m tkinter
```
   O segundo comando deve abrir uma pequena janela de teste. No Windows e no macOS o Tkinter já vem com o instalador oficial do Python (python.org). No Linux (Debian/Ubuntu): `sudo apt install python3-tk`.
 
2. Clone o repositório e entre na pasta:
```bash
git clone https://github.com/sofiaestrelab/Clinica-Medica.git
cd Clinica-Medica
```
 
3. Execute a aplicação **a partir da pasta raiz do projeto**:
```bash
python main.py
```
 
4. (Opcional) Execute os testes automatizados, que não precisam de interface gráfica:
```bash
python -m unittest discover -v
```
 
### Como usar
 
1. Em **Emitir senha**, escolha a especialidade e a categoria e clique em **Emitir senha**. Uma janela mostra a senha, quantos pacientes estão à frente e a espera estimada.
2. Em **Guichê de atendimento**, escolha a especialidade e clique em **Chamar próxima**. A senha aparece no painel e vai para o histórico.
3. Use **Rechamar última** para repetir a chamada mais recente e o filtro da lista de espera para ver uma especialidade específica.
## Imagens da interface gráfica
 
 
## Estrutura do projeto
 
```
Clinica-Medica/
├── main.py                  # ponto de entrada
├── README.md
├── clinica/
│   ├── __init__.py
│   ├── excecoes.py          # exceções do domínio
│   ├── modelos.py           # Categoria, Especialidade, Senha
│   ├── fila.py              # FilaFIFO (lista encadeada) e FilaPrioridade
│   ├── gerenciador.py       # emissão, chamada, prioridade e estimativa
│   └── interface.py         # interface Tkinter
├── tests/
│   ├── __init__.py
│   └── test_sistema.py      # testes unitários
└── docs/
    └── imagens/             # capturas de tela usadas neste README
```
 
A interface (`interface.py`) só cuida da tela. Toda a regra de negócio fica em `gerenciador.py`, apoiada pelas estruturas de `fila.py`.
