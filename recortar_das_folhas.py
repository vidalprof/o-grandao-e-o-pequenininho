# -*- coding: utf-8 -*-
u"""
============================================================
 RECORTAR AS FIGURAS DAS FOLHAS DE PAPEL — O Grandão e o Pequenininho (2º ano)

 ⭐ A REGRA QUE MANDA AQUI (Marcos, 14/set/2026): *"procure na internet, nada de
    imagem gerada por IA, utilize das atividades"*. Toda figura deste caderno sai
    de uma das SEIS folhas que o crivo (`_sequencias/POTE-AUMDIM2.md` §4) chamou
    de mina de figuras — e neste assunto a figura não é enfeite: **o par de
    tamanhos É o conceito**. A criança vê o sapo pequeno ao lado do sapo grande e
    entende "sapinho / sapão" antes de qualquer regra.

   · d39 — *"ESCREVA OS NOMES DAS FIGURAS NO DIMINUTIVO E AUMENTATIVO"*: quatro
     PARES do mesmo desenho em dois tamanhos (sapo, gato, bolo, sapato). É a
     folha que abre o caderno.
   · d40 — *"DÊ O DIMINUTIVO E O AUMENTATIVO DE CADA PALAVRA"*: quatro TRIOS
     (casa, gato, livro, rato) — pequeno · normal · grande. É a folha dos três
     graus, e os três tamanhos lado a lado são o que a tabela sozinha não mostra.
   · d14 — *"LIGUE AS FIGURAS AO SEU DIMINUTIVO"*: seis desenhos a traço limpo
     (folha, elefante, botão, panela, anel, funil). São eles que ensinam o
     **-ZINHO**: anelzinho, funilzinho, botãozinho.
   · d34 — *"DIMINUINDO E AUMENTANDO"*: rato, cachorro, ovo, flor, avião.
   · d02 — *"PREENCHA OS ESPAÇOS…"*: urso, abelha, vaca, leão, girafa (a cores).
   · d12 — *"PREENCHA AS LACUNAS!"*: macaco, rato, cobra, pássaro (a cores).

 ⚠️ AS CAIXAS FORAM MEDIDAS, NÃO CHUTADAS: saem de uma varredura de ILHAS DE
    TINTA em cada folha (`scipy.ndimage.label` sobre os pixels escuros e os
    coloridos, com dilatação para juntar os pedaços do mesmo desenho), impressa e
    lida antes de dar nome a cada uma. Onde a ilha veio grudada na moldura da
    tabela ou no retângulo de resposta — foi o caso dos TRIOS da d40 e do sapato
    grande da d39 —, a caixa foi lida numa prancha com régua desenhada por cima,
    não adivinhada.

 ⚠️ E O NOME TEM DE BATER COM O DESENHO. Trocar um nome aqui não dá erro nenhum:
    só faz a criança ver um livro onde a palavra diz CASA. Conferir OLHANDO a
    folha de contato que este script gera.

 ⚠️ O QUE FICOU DE FORA, de propósito:
    · o quinto par da d39 (o bicho grande com a flor na mão) — não dá para dizer
      com honestidade se é cachorro, lobo ou raposa, e figura cujo nome eu não
      sei é figura que ensina errado;
    · o trio dos RATOS da d40 — os três se tocam (o rabo de um passa por cima do
      vizinho) e não há corte que os separe sem cortar rabo de rato;
    · a VACA da d02, e esta ensinou uma coisa nova: ela é um desenho claro SEM
      contorno, então o branco do corpo e o branco do papel são a MESMA mancha —
      a água do `limpa_fundo` entra pela perna e come metade do bicho (o portão
      do halo acusou 6,7% de quase-branco grudado na silhueta, que era isso).
      Desenho claro sem contorno precisa de outro recorte, e este caderno não
      depende dela;
    · abelha, macaco, rato colorido, ovo, avião e o gato grande do trio — bons
      recortes, mas nenhuma folha os usa. Figura que ninguém usa é peso que a
      criança baixa à toa.

 Uso:  python3 _aumdim2/recortar_das_folhas.py
============================================================
"""
from __future__ import print_function

import io
import json
import os
import sys

try:
    from PIL import Image
except ImportError as e:                                   # pragma: no cover
    print(u"preciso de Pillow (%s)" % e)
    sys.exit(2)

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(RAIZ, u"_padrao"))
from recorte_folha import (limpa_fundo, tira_halo, aperta,          # noqa: E402
                           tira_linha_impressa)

FOLHAS = os.path.join(RAIZ, u"_sequencias", u"folhas_aumdim2")
DEST = os.path.join(AQUI, u"img")
PREFIXO = u"gp_"

MAIOR = 300        # a régua de resolução do `_qa/leiaute_mao.js` reprova figura
                   # mostrada acima de 1,35× da própria altura. 300 px é o teto
                   # que as folhas aguentam sem borrar: a d02 tem 743 px de
                   # largura e os bichos dela medem ~90 px no papel.

# ---------------------------------------------------------------------------
# AS CAIXAS, MEDIDAS NA FOLHA — (arquivo, x1, y1, x2, y2)
# ---------------------------------------------------------------------------
D39 = u"d39_25edc6.jpg"
D40 = u"d40_b28a39.jpg"
D14 = u"d14_497fc0.jpg"
D34 = u"d34_d57d7d.jpg"
D02 = u"d02_543967.jpg"
D12 = u"d12_fd43cf.png"

# ⭐ A COLUNA `grupo` NÃO É ARRUMAÇÃO: é o conceito. O par e o trio são
#    reduzidos pelo MESMO fator, senão o "sapinho" e o "sapão" chegam à tela do
#    mesmo tamanho e a folha deixa de ensinar o que se propõe. Peça de grupo
#    `None` é reduzida sozinha.
PECAS = [
    # --- d39: os PARES, pequeno e grande do mesmo desenho ------------------
    (u"sapo_p",    D39,   75, 370,  265, 572, u"sapo"),
    (u"sapo_g",    D39,  290, 248,  580, 552, u"sapo"),
    (u"gato_p",    D39,  105, 710,  295, 956, u"gatopar"),
    (u"gato_g",    D39,  342, 606,  605, 950, u"gatopar"),
    (u"bolo_p",    D39,   84,1120,  300,1302, u"bolo"),
    (u"bolo_g",    D39,  332,1031,  648,1296, u"bolo"),
    (u"sapato_p",  D39,   78,1390,  278,1556, u"sapato"),
    (u"sapato_g",  D39,  266,1318,  624,1560, u"sapato"),

    # --- d40: os TRIOS, pequeno · normal · grande --------------------------
    # ⚠️ o `y2` de cada um para ANTES do retângulo de resposta e da plaquinha
    #    impressa (CASA, GATO, LIVRO, RATO): o riscozinho que liga a figura à
    #    plaquinha faz a tinta ficar contínua, então cortar é a única saída.
    (u"casa1",     D40,  218, 658,  340, 768, u"casa"),
    (u"casa2",     D40,  340, 619,  528, 768, u"casa"),
    (u"casa3",     D40,  530, 550,  800, 772, u"casa"),
    (u"gato1",     D40,  862, 654,  982, 820, u"gatotrio"),
    (u"gato2",     D40,  986, 596, 1178, 822, u"gatotrio"),
    (u"livro1",    D40,  215,1199,  335,1272, u"livro"),
    (u"livro2",    D40,  332,1150,  534,1298, u"livro"),
    (u"livro3",    D40,  540,1140,  808,1320, u"livro"),
    # ⚠️ O TRIO DOS RATOS FICOU DE FORA e está registrado por quê: os três
    #    ratinhos da d40 se TOCAM — o rabo de um passa por cima do vizinho —,
    #    então nem o corte nem o `so_a_maior_ilha` os separam sem cortar rabo de
    #    rato. Três trios limpos (casa, gato, livro) já cobrem os três graus, e
    #    o rato do caderno vem da d34, inteiro.

    # --- d14: o traço limpo, que ensina o -ZINHO ---------------------------
    (u"folha",     D14,   62, 210,  258, 344, None),
    (u"elefante",  D14,   54, 371,  226, 500, None),
    (u"botao",     D14,   78, 546,  219, 648, None),
    (u"panela",    D14,   81, 708,  244, 819, None),
    (u"anel",      D14,   75, 869,  237, 973, None),
    (u"funil",     D14,  113,1007,  233,1172, None),

    # --- d34 ---------------------------------------------------------------
    (u"rato",      D34,  455, 338,  686, 521, None),
    (u"cachorro",  D34,  464, 567,  661, 746, None),
    (u"flor",      D34,  458,1035,  677,1232, None),

    # --- d02: a cores ------------------------------------------------------
    # ⚠️ AS CAIXAS DAQUI FORAM ABERTAS DEPOIS DE UM CORTE: a primeira versão
    #    parava no y da varredura de tinta, e a VACA saiu sem as pernas — os
    #    cascos pretos ficam 10 px abaixo e a perna, sendo branca, não conta
    #    como tinta na varredura. Quem acusou foi o portão do halo (8,75% de
    #    quase-branco na silhueta: era o corte reto, não um halo). Em bicho
    #    claro sobre papel branco, a varredura mede MENOS do que o desenho tem.
    (u"urso",      D02,  318, 388,  425, 520, None),
    (u"leao",      D02,  318, 752,  425, 876, None),
    (u"girafa",    D02,  318, 872,  428,1025, None),

    # --- d12: a cores ------------------------------------------------------
    (u"cobra",     D12,  607,1322,  803,1550, None),
    (u"passaro",   D12,  607,1646,  803,1836, None),
]

# de qual folha veio cada uma — vira `img/ORIGEM.json`, que o portão 1i5 lê
DE_ONDE = {
    D39: u"d39 — ESCREVA OS NOMES DAS FIGURAS NO DIMINUTIVO E AUMENTATIVO",
    D40: u"d40 — DÊ O DIMINUTIVO E O AUMENTATIVO DE CADA PALAVRA",
    D14: u"d14 — LIGUE AS FIGURAS AO SEU DIMINUTIVO",
    D34: u"d34 — DIMINUINDO E AUMENTANDO, COMPLETE DE ACORDO",
    D02: u"d02 — PREENCHA OS ESPAÇOS COLOCANDO O AUMENTATIVO E O DIMINUTIVO",
    D12: u"d12 — PREENCHA AS LACUNAS!",
}


def so_a_maior_ilha(c):
    u"""Fica só com a MAIOR mancha de tinta do recorte.

    ⚠️ Nasceu dos trios da d40: as três figuras estão lado a lado e o rabo do
       vizinho entra na caixa da peça ao lado. Ele é uma mancha SOLTA — não
       encosta na figura —, então some aqui sem tocar no desenho. (É a mesma
       ideia do `so_o_desenho` do `_sinon2`, escrita para este caso.)"""
    import numpy as np
    from scipy import ndimage as nd
    a = np.asarray(c)
    alfa = a[..., 3] > 24
    if not alfa.any():
        return c
    rot, n = nd.label(nd.binary_dilation(alfa, np.ones((3, 3), bool)))
    if n < 2:
        return c
    tam = nd.sum(alfa, rot, range(1, n + 1))
    guarda = int(np.argmax(tam)) + 1
    px = c.load()
    for y, x in zip(*np.where(alfa & (rot != guarda))):
        r, g, b, _ = px[int(x), int(y)]
        px[int(x), int(y)] = (r, g, b, 0)
    return c


def tira_rabicho(c, fino=8, maximo=45):
    u"""Corta o RISQUINHO que liga a figura à plaquinha impressa.

    ⚠️ Ele é fino (2 px) e ENCOSTA no desenho, então nem o `so_a_maior_ilha` nem
       o `tira_linha_impressa` o alcançam — os dois trabalham por mancha solta. A
       medida que o separa é outra: uma linha de tinta com no máximo `fino`
       colunas pintadas não é desenho, é risco. Anda de baixo para cima e de
       cima para baixo, no máximo `maximo` px de cada lado, para nunca comer a
       pata do gato nem o pé do funil."""
    import numpy as np
    a = np.asarray(c)
    alfa = a[..., 3] > 24
    if not alfa.any():
        return c
    H = alfa.shape[0]
    largura = (alfa.sum(axis=1))
    topo, base = 0, H
    while base - 1 > topo and largura[base - 1] <= fino and (H - base) < maximo:
        base -= 1
    while topo < base - 1 and largura[topo] <= fino and topo < maximo:
        topo += 1
    if topo == 0 and base == H:
        return c
    return c.crop((0, topo, c.width, base))


def recorta(folha, x1, y1, x2, y2, limpar=False):
    u"""Recorta e limpa — SEM reduzir. A redução é depois, por grupo."""
    c = folha.crop((x1, y1, x2, y2))
    c = limpa_fundo(c)
    c = tira_halo(c)
    c = aperta(c)
    # ⚠️ A PAUTA DA FOLHA ENTRA EM TODO RECORTE, e o portão 1i6 mede: cinco das
    #    37 saíram com um risquinho solto pendurado (a linha da tabela na casa3,
    #    a borda da moldura no sapato grande). O `tira_linha_impressa` é a peça
    #    da casa para isso — roda em TODAS, não só nas de tabela.
    if c is not None:
        c = aperta(tira_linha_impressa(c))
    if c is not None and limpar:
        c = aperta(tira_rabicho(so_a_maior_ilha(c)))
    return c


def main():
    if not os.path.isdir(FOLHAS):
        print(u"⛔ não achei %s" % FOLHAS)
        return 2
    abertas, feitas, origem = {}, [], {}
    if os.path.exists(os.path.join(DEST, u"ORIGEM.json")):
        origem = json.load(io.open(os.path.join(DEST, u"ORIGEM.json"),
                                   encoding=u"utf-8"))

    # 1ª passada: recortar e limpar, guardando o tamanho de papel de cada peça
    cortes = []
    for nome, arq, x1, y1, x2, y2, grupo in PECAS:
        if arq not in abertas:
            abertas[arq] = Image.open(os.path.join(FOLHAS, arq)).convert(u"RGB")
        c = recorta(abertas[arq], x1, y1, x2, y2, limpar=(arq == D40))
        if c is None:
            print(u"  ⚠️  %-10s saiu VAZIA (caixa só com papel?)" % nome)
            continue
        cortes.append((nome, arq, grupo, c))

    # 2ª passada: UM fator por grupo — é o que guarda a diferença de tamanho
    maior_do_grupo = {}
    for nome, arq, grupo, c in cortes:
        if grupo:
            maior_do_grupo[grupo] = max(maior_do_grupo.get(grupo, 0), max(c.size))

    for nome, arq, grupo, c in cortes:
        teto = maior_do_grupo[grupo] if grupo else max(c.size)
        if teto > MAIOR:
            f = float(MAIOR) / teto
            c = c.resize((max(1, int(c.width * f)), max(1, int(c.height * f))),
                         Image.LANCZOS)
        alvo = PREFIXO + nome + u".png"
        c.save(os.path.join(DEST, alvo), optimize=True)
        origem[alvo] = u"folha:%s" % DE_ONDE[arq]
        feitas.append((alvo, c.size))
        print(u"  ✓ %-16s %3dx%-3d  <- %s %s"
              % (alvo, c.width, c.height, arq[:3],
                 (u"[%s]" % grupo) if grupo else u""))
    io.open(os.path.join(DEST, u"ORIGEM.json"), u"w", encoding=u"utf-8").write(
        json.dumps(origem, indent=1, sort_keys=True, ensure_ascii=False))
    print(u"\n%d figuras, todas recortadas de folha de papel." % len(feitas))
    folha_de_contato(feitas)
    return 0


def folha_de_contato(feitas):
    u"""A prancha que se OLHA — é aqui que se pega o nome trocado, e esse defeito
    portão nenhum acha: ele não dá erro, só ensina errado."""
    from PIL import ImageDraw
    COLS, CEL, LAB = 6, 170, 26
    linhas = (len(feitas) + COLS - 1) // COLS
    W = COLS * (CEL + 10) + 10
    H = linhas * (CEL + LAB + 10) + 10
    p = Image.new(u"RGB", (W, H), (250, 250, 248))
    d = ImageDraw.Draw(p)
    for i, (alvo, _) in enumerate(feitas):
        im = Image.open(os.path.join(DEST, alvo)).convert(u"RGBA")
        im.thumbnail((CEL, CEL))
        x = 10 + (i % COLS) * (CEL + 10)
        y = 10 + (i // COLS) * (CEL + LAB + 10)
        d.rectangle([x, y, x + CEL, y + CEL], outline=(215, 215, 210))
        fundo = Image.new(u"RGBA", im.size, (255, 255, 255, 255))
        fundo.alpha_composite(im)
        p.paste(fundo.convert(u"RGB"),
                (x + (CEL - im.width) // 2, y + (CEL - im.height) // 2))
        d.text((x + 3, y + CEL + 6), alvo[len(PREFIXO):-4], fill=(40, 44, 52))
    cam = os.path.join(AQUI, u"_contato.png")
    p.save(cam, optimize=True)
    print(u"folha de contato: %s  — OLHAR antes de seguir" % cam)


if __name__ == u"__main__":
    sys.exit(main())
