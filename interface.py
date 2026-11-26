"""Interface gráfica (Tkinter) do sistema de senhas."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .excecoes import ErroClinica, FilaVaziaError
from .gerenciador import GerenciadorSenhas, formatar_minutos
from .modelos import Categoria, Senha

TODAS = "Todas as especialidades"


class AplicacaoClinica:
    def __init__(self, raiz: tk.Tk, gerenciador: GerenciadorSenhas | None = None) -> None:
        self.raiz = raiz
        self.g = gerenciador or GerenciadorSenhas()
        self._siglas = {e.nome: e.sigla for e in self.g.especialidades}
        self._nomes = list(self._siglas)

        raiz.title("Clínica - Gerenciamento de Senhas")
        raiz.geometry("1120x760")
        raiz.minsize(980, 660)
        raiz.columnconfigure(0, weight=1)
        raiz.rowconfigure(1, weight=3)
        raiz.rowconfigure(2, weight=2)

        self._estilos()
        self._montar_painel()
        self._montar_corpo()
        self._montar_historico()
        self._status = tk.StringVar(value="Sistema pronto.")
        ttk.Label(raiz, textvariable=self._status, relief="sunken", anchor="w").grid(
            row=3, column=0, sticky="ew"
        )
        self.atualizar()

    # ------------------------------------------------------------ construção
    def _estilos(self) -> None:
        estilo = ttk.Style(self.raiz)
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 11, "bold"))
        estilo.configure("Senha.TLabel", font=("Segoe UI", 44, "bold"), foreground="#0b5394")
        estilo.configure("Info.TLabel", font=("Segoe UI", 12))

    def _montar_painel(self) -> None:
        painel = ttk.LabelFrame(self.raiz, text=" Painel de atendimento ", padding=10)
        painel.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        painel.columnconfigure(1, weight=1)

        esquerda = ttk.Frame(painel)
        esquerda.grid(row=0, column=0, padx=(0, 30))
        ttk.Label(esquerda, text="Última senha chamada", style="Titulo.TLabel").pack()
        self.v_codigo = tk.StringVar(value="---")
        ttk.Label(esquerda, textvariable=self.v_codigo, style="Senha.TLabel").pack()

        direita = ttk.Frame(painel)
        direita.grid(row=0, column=1, sticky="w")
        self.v_esp = tk.StringVar()
        self.v_cat = tk.StringVar()
        self.v_hora = tk.StringVar()
        self.v_total = tk.StringVar()
        for linha, (rot, var) in enumerate(
            [("Especialidade:", self.v_esp), ("Categoria:", self.v_cat),
             ("Chamada às:", self.v_hora), ("Total aguardando:", self.v_total)]
        ):
            ttk.Label(direita, text=rot, style="Titulo.TLabel").grid(row=linha, column=0, sticky="w")
            ttk.Label(direita, textvariable=var, style="Info.TLabel").grid(
                row=linha, column=1, sticky="w", padx=8
            )

        resumo = ttk.Frame(painel)
        resumo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.v_resumo: dict[str, tk.StringVar] = {}
        for col, esp in enumerate(self.g.especialidades):
            resumo.columnconfigure(col, weight=1)
            var = tk.StringVar()
            self.v_resumo[esp.sigla] = var
            ttk.Label(resumo, textvariable=var, relief="groove", padding=6, anchor="center").grid(
                row=0, column=col, sticky="ew", padx=3
            )

    def _montar_corpo(self) -> None:
        corpo = ttk.Frame(self.raiz)
        corpo.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        corpo.columnconfigure(1, weight=1)
        corpo.rowconfigure(0, weight=1)

        # Controles (esquerda)
        controles = ttk.Frame(corpo)
        controles.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        emissao = ttk.LabelFrame(controles, text=" Emitir senha ", padding=10)
        emissao.pack(fill="x")
        ttk.Label(emissao, text="Especialidade:").pack(anchor="w")
        self.cb_emissao = ttk.Combobox(emissao, values=self._nomes, state="readonly", width=24)
        self.cb_emissao.current(0)
        self.cb_emissao.pack(fill="x", pady=(0, 6))
        ttk.Label(emissao, text="Categoria:").pack(anchor="w")
        self.v_categoria = tk.StringVar(value=Categoria.NORMAL.name)
        for cat in (Categoria.NORMAL, Categoria.PREFERENCIAL):
            ttk.Radiobutton(emissao, text=cat.rotulo, value=cat.name, variable=self.v_categoria).pack(anchor="w")
        ttk.Button(emissao, text="Emitir senha", command=self.emitir).pack(fill="x", pady=(8, 0))

        guiche = ttk.LabelFrame(controles, text=" Guichê de atendimento ", padding=10)
        guiche.pack(fill="x", pady=(12, 0))
        ttk.Label(guiche, text="Especialidade:").pack(anchor="w")
        self.cb_guiche = ttk.Combobox(guiche, values=self._nomes, state="readonly", width=24)
        self.cb_guiche.current(0)
        self.cb_guiche.pack(fill="x", pady=(0, 6))
        ttk.Button(guiche, text="Chamar próxima", command=self.chamar).pack(fill="x")
        ttk.Button(guiche, text="Rechamar última", command=self.rechamar).pack(fill="x", pady=(6, 0))

        # Fila de espera (direita)
        espera = ttk.LabelFrame(corpo, text=" Senhas em espera ", padding=8)
        espera.grid(row=0, column=1, sticky="nsew")
        espera.columnconfigure(0, weight=1)
        espera.rowconfigure(1, weight=1)

        topo = ttk.Frame(espera)
        topo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        ttk.Label(topo, text="Filtrar:").pack(side="left")
        self.cb_filtro = ttk.Combobox(topo, values=[TODAS] + self._nomes, state="readonly", width=26)
        self.cb_filtro.current(0)
        self.cb_filtro.pack(side="left", padx=6)
        self.cb_filtro.bind("<<ComboboxSelected>>", lambda _e: self.atualizar())
        ttk.Label(
            topo, text="Ordem de atendimento: preferenciais primeiro; FIFO em cada categoria.",
            foreground="#555",
        ).pack(side="right")

        colunas = ("pos", "senha", "esp", "cat", "emissao", "espera")
        self.tv_espera = ttk.Treeview(espera, columns=colunas, show="headings", height=8)
        for col, titulo, larg in [
            ("pos", "Posição", 70), ("senha", "Senha", 90), ("esp", "Especialidade", 150),
            ("cat", "Categoria", 110), ("emissao", "Emitida às", 90), ("espera", "Espera estimada", 130),
        ]:
            self.tv_espera.heading(col, text=titulo)
            self.tv_espera.column(col, width=larg, anchor="center")
        self.tv_espera.tag_configure("pref", background="#fff2cc")
        self.tv_espera.grid(row=1, column=0, sticky="nsew")
        barra = ttk.Scrollbar(espera, orient="vertical", command=self.tv_espera.yview)
        self.tv_espera.configure(yscrollcommand=barra.set)
        barra.grid(row=1, column=1, sticky="ns")

    def _montar_historico(self) -> None:
        quadro = ttk.LabelFrame(self.raiz, text=" Histórico de atendimentos ", padding=8)
        quadro.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        quadro.columnconfigure(0, weight=1)
        quadro.rowconfigure(0, weight=1)
        colunas = ("hora", "senha", "esp", "cat", "espera")
        self.tv_hist = ttk.Treeview(quadro, columns=colunas, show="headings", height=5)
        for col, titulo, larg in [
            ("hora", "Chamada às", 90), ("senha", "Senha", 90), ("esp", "Especialidade", 160),
            ("cat", "Categoria", 110), ("espera", "Espera real", 110),
        ]:
            self.tv_hist.heading(col, text=titulo)
            self.tv_hist.column(col, width=larg, anchor="center")
        self.tv_hist.grid(row=0, column=0, sticky="nsew")
        barra = ttk.Scrollbar(quadro, orient="vertical", command=self.tv_hist.yview)
        self.tv_hist.configure(yscrollcommand=barra.set)
        barra.grid(row=0, column=1, sticky="ns")

    # --------------------------------------------------------------- ações
    def _sigla(self, combo: ttk.Combobox) -> str:
        return self._siglas.get(combo.get(), "")  # vazio -> o gerenciador rejeita

    def _tratar(self, erro: ErroClinica) -> None:
        if isinstance(erro, FilaVaziaError):
            messagebox.showwarning("Fila vazia", str(erro))
        else:
            messagebox.showerror("Operação inválida", str(erro))
        self._status.set(f"Erro: {erro}")

    def emitir(self) -> None:
        try:
            senha = self.g.emitir(self._sigla(self.cb_emissao), Categoria[self.v_categoria.get()])
            a_frente = self.g.pacientes_a_frente(senha)
            espera = formatar_minutos(self.g.estimar_espera(senha))
        except (ErroClinica, KeyError) as erro:
            self._tratar(erro if isinstance(erro, ErroClinica) else ErroClinica("Categoria inválida."))
            return
        self._status.set(f"Senha {senha} emitida.")
        self.atualizar()
        messagebox.showinfo(
            "Senha emitida",
            f"Senha: {senha}\nEspecialidade: {senha.especialidade.nome}\n"
            f"Categoria: {senha.categoria.rotulo}\n\n"
            f"Pacientes à frente: {a_frente}\nEspera estimada: {espera}",
        )

    def chamar(self) -> None:
        try:
            senha = self.g.chamar_proxima(self._sigla(self.cb_guiche))
        except ErroClinica as erro:
            self._tratar(erro)
            return
        self._status.set(f"Chamando {senha} - {senha.especialidade.nome}.")
        self.atualizar()

    def rechamar(self) -> None:
        try:
            senha = self.g.rechamar_ultima()
        except ErroClinica as erro:
            self._tratar(erro)
            return
        self._status.set(f"Rechamando {senha} - {senha.especialidade.nome}.")

    # --------------------------------------------------------- atualização
    def atualizar(self) -> None:
        ultima = self.g.ultima_chamada
        if ultima is None:
            self.v_codigo.set("---")
            self.v_esp.set("-")
            self.v_cat.set("-")
            self.v_hora.set("-")
        else:
            self.v_codigo.set(ultima.codigo)
            self.v_esp.set(ultima.especialidade.nome)
            self.v_cat.set(ultima.categoria.rotulo)
            self.v_hora.set(ultima.chamada_em.strftime("%H:%M:%S"))
        self.v_total.set(str(self.g.total_em_espera()))

        for esp in self.g.especialidades:
            p = self.g.quantidade(esp.sigla, Categoria.PREFERENCIAL)
            n = self.g.quantidade(esp.sigla, Categoria.NORMAL)
            self.v_resumo[esp.sigla].set(f"{esp.nome}: {p + n} aguardando (P: {p} | N: {n})")

        self._preencher_espera()
        self._preencher_historico()

    def _preencher_espera(self) -> None:
        self.tv_espera.delete(*self.tv_espera.get_children())
        filtro = self._siglas.get(self.cb_filtro.get())
        siglas = [filtro] if filtro else [e.sigla for e in self.g.especialidades]
        for sigla in siglas:
            for pos, s in enumerate(self.g.em_espera(sigla), start=1):
                self.tv_espera.insert(
                    "", "end",
                    values=(f"{pos}º", s.codigo, s.especialidade.nome, s.categoria.rotulo,
                            s.emitida_em.strftime("%H:%M:%S"),
                            formatar_minutos(self.g.estimar_espera(s))),
                    tags=("pref",) if s.categoria is Categoria.PREFERENCIAL else (),
                )

    def _preencher_historico(self) -> None:
        self.tv_hist.delete(*self.tv_hist.get_children())
        for s in reversed(self.g.historico):
            espera = int((s.chamada_em - s.emitida_em).total_seconds())
            self.tv_hist.insert(
                "", "end",
                values=(s.chamada_em.strftime("%H:%M:%S"), s.codigo, s.especialidade.nome,
                        s.categoria.rotulo, f"{espera // 60}min {espera % 60:02d}s"),
            )
