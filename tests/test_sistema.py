import unittest

from clinica.excecoes import (
    CategoriaInvalidaError, EspecialidadeInvalidaError, FilaVaziaError, OperacaoInvalidaError,
)
from clinica.fila import FilaFIFO, FilaPrioridade
from clinica.gerenciador import GerenciadorSenhas, formatar_minutos
from clinica.modelos import Categoria

P, N = Categoria.PREFERENCIAL, Categoria.NORMAL


class TestFilaFIFO(unittest.TestCase):
    def test_ordem_fifo(self):
        f = FilaFIFO()
        for x in (1, 2, 3):
            f.enfileirar(x)
        self.assertEqual([f.desenfileirar() for _ in range(3)], [1, 2, 3])

    def test_vazia(self):
        f = FilaFIFO()
        self.assertTrue(f.esta_vazia())
        with self.assertRaises(FilaVaziaError):
            f.desenfileirar()
        with self.assertRaises(FilaVaziaError):
            f.espiar()

    def test_reuso_apos_esvaziar(self):
        f = FilaFIFO()
        f.enfileirar("a")
        f.desenfileirar()
        f.enfileirar("b")
        self.assertEqual(list(f), ["b"])
        self.assertEqual(len(f), 1)


class TestFilaPrioridade(unittest.TestCase):
    def test_prioridade_e_fifo(self):
        fp = FilaPrioridade([P, N])
        for item, nivel in [("n1", N), ("p1", P), ("n2", N), ("p2", P)]:
            fp.enfileirar(item, nivel)
        self.assertEqual(list(fp), ["p1", "p2", "n1", "n2"])
        self.assertEqual([fp.desenfileirar() for _ in range(4)], ["p1", "p2", "n1", "n2"])
        with self.assertRaises(FilaVaziaError):
            fp.desenfileirar()


class TestGerenciador(unittest.TestCase):
    def setUp(self):
        self.g = GerenciadorSenhas()

    def test_numeracao_por_especialidade_e_categoria(self):
        self.assertEqual(self.g.emitir("CG", N).codigo, "CG-N001")
        self.assertEqual(self.g.emitir("CG", N).codigo, "CG-N002")
        self.assertEqual(self.g.emitir("CG", P).codigo, "CG-P001")
        self.assertEqual(self.g.emitir("CA", N).codigo, "CA-N001")

    def test_filas_independentes(self):
        self.g.emitir("CG", N)
        self.g.emitir("CA", N)
        self.assertEqual(self.g.quantidade("CG"), 1)
        self.assertEqual(self.g.quantidade("OR"), 0)
        self.assertEqual(self.g.total_em_espera(), 2)

    def test_chamada_respeita_prioridade(self):
        self.g.emitir("CG", N)   # N001
        self.g.emitir("CG", N)   # N002
        self.g.emitir("CG", P)   # P001
        self.g.emitir("CG", P)   # P002
        chamadas = [self.g.chamar_proxima("CG").codigo for _ in range(4)]
        self.assertEqual(chamadas, ["CG-P001", "CG-P002", "CG-N001", "CG-N002"])
        self.assertEqual([s.codigo for s in self.g.historico], chamadas)
        self.assertEqual(self.g.ultima_chamada.codigo, "CG-N002")

    def test_estimativa(self):
        n1 = self.g.emitir("CG", N)
        self.assertEqual(self.g.estimar_espera(n1), 0)
        p1 = self.g.emitir("CG", P)
        self.assertEqual(self.g.estimar_espera(p1), 0)      # passa na frente
        self.assertEqual(self.g.estimar_espera(n1), 30)     # 1 preferencial à frente
        n2 = self.g.emitir("CG", N)
        self.assertEqual(self.g.estimar_espera(n2), 60)

    def test_erros(self):
        with self.assertRaises(FilaVaziaError):
            self.g.chamar_proxima("CG")
        with self.assertRaises(EspecialidadeInvalidaError):
            self.g.emitir("XX", N)
        with self.assertRaises(EspecialidadeInvalidaError):
            self.g.emitir("", N)
        with self.assertRaises(CategoriaInvalidaError):
            self.g.emitir("CG", "N")
        with self.assertRaises(OperacaoInvalidaError):
            self.g.rechamar_ultima()

    def test_estimar_senha_ja_chamada(self):
        s = self.g.emitir("CG", N)
        self.g.chamar_proxima("CG")
        with self.assertRaises(OperacaoInvalidaError):
            self.g.estimar_espera(s)

    def test_formatar_minutos(self):
        self.assertEqual(formatar_minutos(0), "sem espera")
        self.assertEqual(formatar_minutos(30), "30 min")
        self.assertEqual(formatar_minutos(90), "1h 30min")
        self.assertEqual(formatar_minutos(120), "2h")


if __name__ == "__main__":
    unittest.main()
