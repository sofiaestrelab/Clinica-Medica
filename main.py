"""Ponto de entrada do sistema de senhas da clínica."""
import tkinter as tk

from clinica.interface import AplicacaoClinica


def main() -> None:
    raiz = tk.Tk()
    AplicacaoClinica(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
