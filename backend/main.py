# -*- coding: utf-8 -*-
"""
Ponto de entrada do Sistema de Abertura, Controle e Fechamento de
Chamados de Informática, Telefonia e Manutenção Geral.

Para executar: python main.py
"""

import sys

from menu import Aplicacao


def main():
    # Em alguns terminais do Windows (cmd.exe com a página de código
    # antiga), imprimir acentos pode gerar UnicodeEncodeError e encerrar
    # o programa de forma abrupta. Esta linha força a saída em UTF-8
    # para evitar esse tipo de erro. Se necessário, no cmd.exe rode antes
    # o comando "chcp 65001", ou utilize o terminal do VSCode.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    aplicacao = Aplicacao()
    aplicacao.executar()


if __name__ == "__main__":
    main()
