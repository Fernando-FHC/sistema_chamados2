# -*- coding: utf-8 -*-
"""
Módulo de segurança: geração e verificação de hash de senhas.

Senhas nunca devem ser guardadas em texto puro no banco. Aqui, em vez
de salvar a senha digitada pelo usuário, salvamos o resultado de uma
função de hash (SHA-256) aplicada à senha. Um hash não pode ser
"desfeito" para se descobrir a senha original — por isso, para
verificar o login, recalculamos o hash da senha digitada e
comparamos com o que está salvo no banco, em vez de comparar as
senhas diretamente.

Também usamos um "salt": um texto aleatório gerado para cada usuário
e guardado junto com o hash. Ele é concatenado com a senha antes de
calcular o hash. Isso garante que, mesmo que duas pessoas usem a
mesma senha, os hashes salvos sejam diferentes.
"""

import hashlib
import random
import string


def gerar_salt(tamanho=8):
    """Gera um texto aleatório (letras e números) para ser usado como salt."""
    caracteres = string.ascii_letters + string.digits
    return "".join(random.choice(caracteres) for _ in range(tamanho))


def gerar_hash_senha(senha: str):
    """
    Gera um salt aleatório e calcula o hash da senha (já com o salt).

    Retorna uma tupla (hash, salt), ambos como texto, prontos para
    serem salvos nas colunas do banco.
    """
    salt = gerar_salt()
    texto = senha + salt
    hash_senha = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    return hash_senha, salt


def verificar_senha(senha: str, hash_armazenado: str, salt_armazenado: str) -> bool:
    """
    Recalcula o hash da senha informada usando o mesmo salt que foi
    salvo no banco, e compara com o hash armazenado.
    """
    texto = senha + salt_armazenado
    hash_calculado = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    return hash_calculado == hash_armazenado
