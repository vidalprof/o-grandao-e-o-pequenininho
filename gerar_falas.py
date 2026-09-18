# -*- coding: utf-8 -*-
u"""
============================================================
 ESQUELETO — gerador das falas da folha viva

 ⚠️ REGRA DA CASA: o `falas.json` é a VERDADE. Texto escrito aqui = voz gravada.
    Texto mudou = voz regravada (o `entregar.yml` compara o carimbo sha1). É isto
    que acaba com "a tela diz uma coisa e a voz diz outra" — e atividade sem
    `falas.json` NÃO TEM COMO SER CONFERIDA, porque mp3 não se lê.

 ⚠️ UMA FONTE SÓ. As palavras, as frases e os textos moram no bloco
    `/*DADOS-INI*/` do `index.html` e são LIDOS daqui. Nada de segunda lista
    para desencontrar: já custou caro nesta casa um relatório sair zero com a
    folha inteira respondida.

 ⚠️ TODA TELA É NARRADA, e o alto-falante entra também em CADA RESPOSTA que a
    criança toca. Regra do Marcos: *"o alto-falante nas respostas também, para
    ajudar os alunos que não sabem ler"*. Sem isso a criança que ainda soletra
    escolhe pelo tamanho da palavra e a folha vira sorteio.

 ⚠️ A DICA NUNCA DIZ A RESPOSTA. Ela manda olhar uma pista, ou faz outra
    pergunta. Responder no segundo erro não é ajudar: é tirar da criança a única
    chance de pensar de novo.

 ⚠️ PALAVRAS QUE A VOZ ERRA (medido, e o portão `_qa/falas.py` reprova):
    "complete" vira "complite" — usar "preencha". Letra solta ("som S") sai como
    o NOME da letra: ancorar num exemplo ("o som de SAPO").

 Uso:  python3 <pasta>/gerar_falas.py
 Saída: reescreve os blocos FALAS e VOZOK do index.html, o `falas.json` e o
        `voz.txt`.
============================================================
"""
from __future__ import print_function

import collections
import io
import json
import os
import re
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
CAM = os.path.join(AQUI, u"index.html")
PREFIXO = u"gp_"                     # <- o prefixo desta atividade
VOZ = u"pt-BR-AntonioNeural"

D = io.open(CAM, encoding=u"utf-8").read()


def bloco(nome):
    u"""Lê um objeto do bloco DADOS do index.html. Uma fonte só.

    ⚠️ ELE CONTA AS CHAVES, e isso foi conserto de 15/set/2026. O esqueleto
       procurava o fim do objeto por uma marca de texto (`\n});`) — e QUALQUER
       objeto que não terminasse exatamente assim fazia a leitura passar
       adiante e engolir o bloco seguinte. No primeiro caderno do 2º ano os
       vinte e três blocos falharam de uma vez, todos com o mesmo erro, e a
       mensagem do json não dizia nada sobre a causa. Contar chave por chave
       (pulando as que estão DENTRO de texto) acha o fim de qualquer objeto.
    """
    i = D.find(u"var " + nome + u" = ")
    if i < 0:
        raise SystemExit(u"nao achei o bloco `var %s` no index.html" % nome)
    i = D.index(u"{", i)
    nivel, j, dentro, escapa = 0, i, False, False
    while j < len(D):
        c = D[j]
        if dentro:
            if escapa:
                escapa = False
            elif c == u"\\":
                escapa = True
            elif c == u'"':
                dentro = False
        else:
            if c == u'"':
                dentro = True
            elif c == u"{":
                nivel += 1
            elif c == u"}":
                nivel -= 1
                if nivel == 0:
                    j += 1
                    break
        j += 1
    txt = D[i:j]
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    txt = re.sub(r'"\s*\+\s*\n\s*"', "", txt)                 # junta "a" + "b"
    txt = re.sub(r'([\{,]\s*)"?([A-Za-zÀ-ÿ_0-9]+)"?\s*:', r'\1"\2":', txt)
    txt = re.sub(r",(\s*[\}\]])", r"\1", txt)
    return json.loads(txt)


# ⚠️⚠️ A ENTIDADE HTML TAMBÉM É MARCAÇÃO, e isto foi lição paga (15/set/2026,
#    caderno de inglês do 8º ano). O `lp` tirava as TAGS e deixava as
#    ENTIDADES, então a lista de ingredientes da pizza — escrita com `&middot;`
#    para virar o ponto que separa os itens — ia para a fila de gravação como
#    *"Oil and middot Tomato sauce and middot Some onions"*. O portão
#    `_qa/revisor.py` pegou; se não pegasse, a voz teria dito isso à criança.
_ENT = {u"&middot;": u",", u"&nbsp;": u" ", u"&amp;": u" e ", u"&mdash;": u" ",
        u"&ndash;": u" ", u"&hellip;": u" ", u"&quot;": u'"', u"&lt;": u"",
        u"&gt;": u"", u"&#39;": u"'", u"&apos;": u"'"}


def lp(s):
    u"""tira a marcação e deixa o texto do jeito que a voz vai dizer"""
    t = re.sub(r"<[^>]+>", " ", s or u"")
    for _e, _v in _ENT.items():
        t = t.replace(_e, _v)
    t = re.sub(r"\s+", u" ", t)
    # ⚠️ e a tag que vira espaco deixa um vao ANTES da pontuacao ("o cinema ."),
    #    que o `_qa/revisor.py` acusa — com razao: a voz faz a pausa no lugar
    #    errado. Cola a pontuacao de volta na palavra.
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)
    # ⚠️ E A VIRGULA DA PAUSA PODE ENCOSTAR NUMA QUE JA EXISTIA (15/set/2026):
    #    a frase "My dad, ___ travels a lot" virou "My dad,, travels a lot" —
    #    duas virgulas coladas, que o Edge TTS le como uma pausa estranha e
    #    longa demais. Uma so, sempre.
    t = re.sub(r",\s*,+", u",", t)
    return t.strip()


def ch(w):
    return re.sub(r"[^a-z]", "",
                  unicodedata.normalize("NFKD", w.lower())
                  .encode("ascii", "ignore").decode())


# ⚠️⚠️ A ENTIDADE HTML TAMBÉM É MARCAÇÃO, e isto foi lição paga (15/set/2026,
#    caderno de inglês do 8º ano). O `lp` tirava as TAGS e deixava as
#    ENTIDADES, então a lista de ingredientes da pizza — escrita com `&middot;`
#    para virar o ponto que separa os itens — ia para a fila de gravação como
#    *"Oil and middot Tomato sauce and middot Some onions"*. O portão
#    `_qa/revisor.py` pegou; se não pegasse, a voz teria dito isso à criança.
_ENT = {u"&middot;": u",", u"&nbsp;": u" ", u"&amp;": u" e ", u"&mdash;": u" ",
        u"&ndash;": u" ", u"&hellip;": u" ", u"&quot;": u'"', u"&lt;": u"",
        u"&gt;": u"", u"&#39;": u"'", u"&apos;": u"'"}


def lp(s):
    u"""tira a marcação e deixa o texto do jeito que a voz vai dizer"""
    t = re.sub(r"<[^>]+>", " ", s or u"")
    for _e, _v in _ENT.items():
        t = t.replace(_e, _v)
    t = re.sub(r"\s+", u" ", t)
    # ⚠️ e a tag que vira espaco deixa um vao ANTES da pontuacao ("o cinema ."),
    #    que o `_qa/revisor.py` acusa — com razao: a voz faz a pausa no lugar
    #    errado. Cola a pontuacao de volta na palavra.
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)
    # ⚠️ E A VIRGULA DA PAUSA PODE ENCOSTAR NUMA QUE JA EXISTIA (15/set/2026):
    #    a frase "My dad, ___ travels a lot" virou "My dad,, travels a lot" —
    #    duas virgulas coladas, que o Edge TTS le como uma pausa estranha e
    #    longa demais. Uma so, sempre.
    t = re.sub(r",\s*,+", u",", t)
    return t.strip()


def ch(w):
    return re.sub(r"[^a-z]", "",
                  unicodedata.normalize("NFKD", w.lower())
                  .encode("ascii", "ignore").decode())


F = collections.OrderedDict()


def p(k, v):
    u"""⚠️ TODA fala passa por aqui LIMPA. Não é enfeite: quando a frase perde o
    travessão do discurso direto (`— Socorro! — gritou`), sobram dois espaços; a
    pista `ele ___ (correr)` vira `ele lacuna , verbo correr`; e um texto que já
    acaba em ponto ganha outro e sai `ela..`. Os TRÊS aconteceram neste caderno e
    quem pegou foi o portão `0o` (`_qa/revisor.py`) — a criança OUVIRIA isso."""
    t = re.sub(r"\s+", u" ", (v or u"")).strip()
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)     # espaço antes da pontuação
    t = re.sub(r"([,.;:!?])\1+", r"\1", t)     # ".." e ",,"
    t = re.sub(r"\.\s*\.", u".", t)
    F[k] = t




# ---------------------------------------------------------------------------
# AS FALAS DO MOTOR — estas toda folha viva tem
# ---------------------------------------------------------------------------
p(u"capa", u"O Grandão e o Pequenininho. Trinta e cinco folhas sobre o tamanho das palavras: "
           u"a do pequenininho e a do grandão. Escreva o seu nome ali embaixo e toque em Começar.")
p(u"folhaPronta", u"Folha pronta! Muito bem.")
p(u"escreva", u"Escreva a palavra usando o teclado.")
p(u"ligue", u"Toque numa figura do lado esquerdo e depois na palavra do lado direito.")
p(u"toque_palavra", u"Primeiro toque numa palavra ali embaixo. Depois toque na gaveta dela.")
p(u"quase", u"Quase! Tente de novo.")
p(u"cacatoque", u"Toque primeiro na primeira letra da palavra.")
p(u"pegue_lapis", u"Primeiro pegue uma canetinha ali em cima. Depois toque na palavra.")
p(u"novoCaderno", u"Caderno novo! Escreva o seu nome e toque em Começar.")
p(u"vozOn", u"Narração ligada!")
p(u"fim", u"Você chegou ao fim! Agora uma curiosidade para levar: nem todo grandão termina em ÃO. Existe colheraça, que é uma colher enorme. Existe fogaréu, que é um fogo enorme. E existe mesona, que é uma mesa enorme. Procure outros por aí e traga para a aula.")


def cq(w):
    return ch(w)


def semLacuna(s):
    u"""⚠️ A LACUNA NÃO SE NARRA (regra da casa, `SEQUENCIAS-DIDATICAS §2c`), e
    aqui ela morde de um jeito próprio: as frases deste caderno são do tipo
    *"Uma bola pequena é uma ___"*, então trocar o traço pela palavra "lacuna"
    produzia *"é uma lacuna"* e *"é um lacuna"* — e o `_qa/revisor.py` acusou o
    segundo como erro de concordância, com razão. A frase fica em suspenso, com
    reticências, que é como um adulto leria: *"Uma bola pequena é uma…"*. A
    resposta certa diz a frase INTEIRA, aí sim."""
    return re.sub(r"\s*_{2,}\s*\.?", u"…", lp(s))


ENUN = [
 u"Olhe os dois desenhos. Um é pequeno, o outro é grande. Toque no nome do pequeno.",
 u"Agora o contrário: os mesmos desenhos, e você toca no nome do grande.",
 u"Cada palavra tem o seu desenho. Puxe a palavra até a figura, ou toque na palavra e depois na figura.",
 u"O filhote é o pequenininho do bicho. Toque no nome do filhote de cada um.",
 u"Do lado esquerdo estão os bichos. Do direito, o nome dos filhotes. Toque num e depois no outro para ligar.",
 u"As casinhas dizem quantas letras tem a palavra. Toque nelas e escreva, ou use o teclado de verdade.",
 u"Repare: para dizer que a coisa é pequena, a palavra ganha um fim novo. Toque na palavra que preenche a frase.",
 u"Mais seis. Antes de tocar, diga a palavra em voz alta com o fim novo e escute se soa certo.",
 u"Você já escolheu o pequenininho. Agora escreva você mesmo.",
 u"Algumas palavras pedem um Z antes do fim. Diga as duas em voz alta: só uma existe.",
 u"Ligue cada figura ao seu pequenininho. Três delas pedem o Z: preste atenção.",
 u"Leia a palavra. Ela só ganhou o INHO, ou precisou de um Z antes? Leve para a gaveta certa.",
 u"Cuidado! Algumas palavras terminam igualzinho e não falam de coisa pequena: rainha não é uma rã pequena. "
 u"Marque só as verdadeiras e toque em Conferir.",
 u"Agora ao contrário: a coisa é grande. A palavra também ganha um fim, outro fim. Toque nele.",
 u"Mais seis do grandão. Diga cada palavra em voz alta antes de escolher.",
 u"Agora escreva o grandão. O fim dele é sempre o mesmo, com o til em cima.",
 u"Agora são três tamanhos do mesmo desenho: o pequeno, o de sempre e o grande. Leve cada palavra ao seu.",
 u"Cada linha diz uma palavra e pede um tamanho. Leia com atenção: ora pede o pequeno, ora o grande.",
 u"Cada linha tem os três tamanhos e um está faltando. Leia os dois que estão lá e escreva o que falta.",
 u"Agora a palavra entra dentro de uma frase inteira. Leia tudo e escolha a que cabe.",
 u"As duas frases são quase iguais: só uma palavra muda. Toque na que fala do grande.",
 u"A primeira frase diz o tamanho com duas palavras. Escreva a palavra que faz o mesmo sozinha.",
 u"Leia o texto e toque nas palavras do pequenininho. Depois confira.",
 u"Agora o contrário: toque nas palavras do grandão. Depois confira.",
 u"Cuidado com as parecidas! Toque só nas palavras do pequenininho. Depois confira.",
 u"Ache na grade o pequenininho de cada palavra: toque na primeira letra e depois na última.",
 u"Agora os grandões. Na grade as palavras estão sem o til: procure PORTAO, não portão.",
 u"Toque numa pista, escute e escreva a palavra do tamanho que ela pede.",
 u"Leia a palavra. Ela fala de uma coisa pequena ou de uma coisa grande? Leve para a gaveta.",
 u"Agora são três gavetas. A mesma palavra aparece nos três tamanhos: separe cada uma.",
 u"As mesmas três gavetas, com palavras misturadas. Leia com calma antes de levar.",
 u"Agora é ao contrário de tudo o que você fez: a palavra já vem com tamanho, e você acha a do tamanho de sempre.",
 u"Agora o caminho de volta: leia o tamanho e escreva a palavra do tamanho de sempre.",
 u"Agora a palavra é sua. Pense numa coisa de verdade e escreva o nome dela no tamanho que a folha pede.",
 u"Você já sabe fazer tudo isto. Agora os nomes: leve cada palavra para a linha dela no cartaz."]
assert len(ENUN) == 35, len(ENUN)
for _i, _t in enumerate(ENUN):
    p(u"p%denun" % (_i + 1), _t)

ELOGIO = [u"Isso mesmo!", u"Muito bem!", u"Você acertou!", u"Boa!", u"Exatamente!", u"É isso aí!"]
DICAS_P = [u"Olhe o desenho menor. O nome dele fica mais comprido, e o fim muda.",
           u"Diga a palavra devagar, como se estivesse falando com um bebê. O fim aparece sozinho.",
           u"Pense no filhote do bicho: é assim que a palavra fica quando a coisa é pequena."]
DICAS_G = [u"Olhe o desenho maior. O nome dele termina com um som forte, de boca aberta.",
           u"Diga a palavra como se a coisa fosse enorme. Escute o fim.",
           u"O fim do grandão tem um til em cima: é o mesmo de todos eles."]


def elogio(n):
    return ELOGIO[n % len(ELOGIO)]


def dicaP(n):
    return DICAS_P[n % len(DICAS_P)]


def dicaG(n):
    return DICAS_G[n % len(DICAS_G)]


ITENS = bloco(u"ITENS")


def pote(pi):
    v = ITENS[u"p%d" % pi]
    return v[0] if v and isinstance(v[0], list) else v


def palavras(*ws):
    u"""⚠️ A CHAVE TRANSLITERA O ACENTO (`ch`), não o apaga — e neste caderno
    isso é o que separa `gatao` de `gato`. Com a chave que apaga, o
    alto-falante do grandão diria a palavra de sempre."""
    for _w in ws:
        if _w:
            _t = lp(_w)
            _t = _t[0].upper() + _t[1:]
            p(u"pal_" + ch(_w), _t if _t[-1:] in u".!?" else _t + u".")


# --- 1 e 2: o par de figuras -------------------------------------------------
PAR1 = bloco(u"PAR1")
for _n, _k in enumerate(pote(1)):
    _X = PAR1[_k]
    palavras(*_X[u"ops"])
    p(u"prg_" + _k, u"Como se chama o %s pequeno?" % _X[u"n"])
    p(u"certo1_" + _k, elogio(_n) + u" O %s pequeno é o %s." % (_X[u"n"], _X[u"r"]))
    p(u"dica1_" + _k, dicaP(_n))
PAR2 = bloco(u"PAR2")
for _n, _k in enumerate(pote(2)):
    _X = PAR2[_k]
    palavras(*_X[u"ops"])
    p(u"prg_" + _k, u"Você já sabe que o pequeno é o %s. E o grande?" % _X[u"pista"])
    p(u"certo2_" + _k, elogio(_n) + u" O %s grande é o %s." % (_X[u"n"], _X[u"r"]))
    p(u"dica2_" + _k, dicaG(_n))

# --- 3 e 17: puxe a palavra até a figura -------------------------------------
for _pi, _nome in ((3, u"SOLTA1"), (17, u"SOLTA2")):
    _D = bloco(_nome)
    for _n, _k in enumerate(pote(_pi)):
        _X = _D[_k]
        palavras(_X[u"rot"])
        p(u"fig_" + _k, _X[u"dz"])
        p(u"certo%d_%s" % (_pi, _k), elogio(_n) + u" " + _X[u"dz"] + u" " +
          _X[u"rot"].capitalize() + u".")
        p(u"dica%d_%s" % (_pi, _k), u"Olhe o tamanho do desenho e diga a palavra em voz alta. "
                                    u"Elas não combinam ainda.")

# --- 4, 7, 8, 10, 14, 15 e 20: a frase com lacuna ----------------------------
for _pi, _nome, _tipo in ((4, u"FILH", u"p"), (7, u"DIM1", u"p"), (8, u"DIM2", u"p"),
                          (10, u"ZIN1", u"z"), (14, u"AUM1", u"g"), (15, u"AUM2", u"g"),
                          (20, u"FRASE1", u"p")):
    _D = bloco(_nome)
    for _n, _k in enumerate(pote(_pi)):
        _X = _D[_k]
        palavras(*_X[u"ops"])
        p(u"fra_" + _k, semLacuna(_X[u"f"]))
        p(u"certo%d_%s" % (_pi, _k), elogio(_n) + u" " +
          lp(_X[u"f"]).replace(u"___", _X[u"r"]))
        if _tipo == u"z":
            p(u"dica%d_%s" % (_pi, _k),
              u"Diga as duas em voz alta. Uma delas não existe: a gente nunca fala assim. "
              u"A que existe tem um Z no meio, ou não tem?")
        else:
            p(u"dica%d_%s" % (_pi, _k), dicaP(_n) if _tipo == u"p" else dicaG(_n))

# --- 5 e 11: ligar a figura à palavra ----------------------------------------
for _pi, _nome in ((5, u"LIGF"), (11, u"LIGZ")):
    _D = bloco(_nome)
    for _n, _k in enumerate(pote(_pi)):
        _L = _D[_k]
        palavras(_L[u"b"])
        p(u"fig_" + _k, _L[u"n"].capitalize() + u".")
        p(u"certo%d_%s" % (_pi, _k), elogio(_n) + u" O pequenininho de %s é %s."
          % (_L[u"n"], _L[u"b"]))
        p(u"dica%d_%s" % (_pi, _k),
          u"Diga o nome da figura e depois cada palavra do lado direito. Só uma começa igual.")

# --- 6, 9, 16, 19, 22 e 33: escreva nas casinhas -----------------------------
for _pi, _nome in ((6, u"GRD1"), (9, u"GRD2"), (16, u"GRD3"),
                   (19, u"GRD4"), (22, u"GRD5"), (33, u"GRD6")):
    _D = bloco(_nome)
    for _n, _k in enumerate(pote(_pi)):
        _G = _D[_k]
        p(u"grd_" + _k, semLacuna(_G[u"p"]) + u" " + lp(_G[u"d"]))
        if _pi == 33:
            # ⚠️ na 33 a pista JÁ É a palavra com grau (não tem lacuna): sem este
            #    caso a fala do acerto saía só "Exatamente! portão", que não diz
            #    nada à criança — e é justamente a folha do caminho de volta.
            _c = u"%s vem de %s." % (_G[u"p"].capitalize(), _G[u"w"].lower())
        else:
            _c = lp(_G[u"p"]).replace(u"___", _G[u"w"].lower())
            _c = _c[0].upper() + _c[1:]          # "gatinho, gato, gatão" -> "Gatinho, …"
        p(u"certo%d_%s" % (_pi, _k), elogio(_n) + u" " + _c)
        p(u"dica%d_%s" % (_pi, _k),
          u"Conte as casinhas e diga a palavra bem devagar, letra por letra. "
          u"Comece pelo começo da palavra que está na frase.")

# --- 12, 29, 30 e 31: as gavetas ---------------------------------------------
GAV = bloco(u"GAV")
_GAVTXT = {u"i": u"Gaveta das palavras que só ganharam o INHO.",
           u"z": u"Gaveta das palavras que precisaram do Z.",
           u"p": u"Gaveta do pequenininho.",
           u"n": u"Gaveta do tamanho de sempre.",
           u"g": u"Gaveta do grandão."}
for _gk, _G in GAV.items():
    for _C in _G[u"cols"]:
        p(u"gav_%s_%s" % (_gk, _C[u"k"]), _GAVTXT[_C[u"k"]])
_GAVCERTO = {u"i": u" só ganhou o INHO.", u"z": u" precisou do Z.",
             u"p": u" fala de uma coisa pequena.", u"n": u" é do tamanho de sempre.",
             u"g": u" fala de uma coisa grande."}
_GAVDICA = {u"gA": u"Diga a palavra devagar. Você ouve um zê antes do fim, ou não?",
            u"gB": u"A coisa de que a palavra fala é pequena ou é grande? O fim da palavra conta isso.",
            u"gC": u"Compare as três da mesma família e ponha em fila: a menor, a de sempre e a maior.",
            u"gD": u"Leia só o fim da palavra. Ele é o fim do pequeno, o do grande, ou não é nem um nem outro?"}
for _pi, _gk in ((12, u"gA"), (29, u"gB"), (30, u"gC"), (31, u"gD")):
    for _n, _k in enumerate(pote(_pi)):
        _X = GAV[_gk][u"pal"][_k]
        p(u"diz2_%s_%s" % (_gk, _k), lp(_X[u"p"]).capitalize() + u".")
        p(u"certo%d_%s" % (_pi, _k), elogio(_n) + u" " +
          lp(_X[u"p"]).capitalize() + _GAVCERTO[_X[u"c"]])
        p(u"dica%d_%s" % (_pi, _k), _GAVDICA[_gk])

# --- 13: ⚠️ a armadilha das parecidas ----------------------------------------
MARQ = bloco(u"MARQ")
for _n, _k in enumerate(pote(13)):
    _M = MARQ[_k]
    palavras(*[_q[u"t"] for _q in _M[u"pecas"]])
    _ok = [_q[u"t"] for _q in _M[u"pecas"] if _q[u"ok"]]
    p(u"certo13_" + _k, elogio(_n) + u" As de coisa pequena são " + u", ".join(_ok) + u".")
    p(u"dica13_" + _k,
      u"Pergunte, uma por uma: existe a coisa grande dela? Existe casa, e a casinha é a casa pequena. "
      u"Mas não existe rã que vire rainha.")

# --- 18: os três tamanhos na palavra -----------------------------------------
TRES = bloco(u"TRES")
for _n, _k in enumerate(pote(18)):
    _X = TRES[_k]
    palavras(*_X[u"ops"])
    p(u"prg_" + _k, u"%s. E quando é %s?" % (_X[u"n"].capitalize(), _X[u"pede"]))
    p(u"certo18_" + _k, elogio(_n) + u" %s %s, quando é %s, é %s."
      % (_X[u"art"].upper(), _X[u"n"].lower(), _X[u"pede"], _X[u"r"]))
    p(u"dica18_" + _k, u"Leia de novo o que a linha pede: é o pequeno ou o grande? "
                       u"Depois olhe o fim de cada palavra.")

# --- 21: qual frase fala do grandão? -----------------------------------------
REESC = bloco(u"REESC")
for _n, _k in enumerate(pote(21)):
    _R = REESC[_k]
    p(u"ree_" + _k, lp(_R[u"f"]))
    p(u"frs_%s_c" % _k, lp(_R[u"certa"]))
    p(u"frs_%s_o" % _k, lp(_R[u"outra"]))
    p(u"certo21_" + _k, elogio(_n) + u" " + lp(_R[u"certa"]))
    p(u"dica21_" + _k, u"Leia as duas em voz alta. Uma fala de uma coisa enorme e a outra "
                       u"de uma coisa miudinha. Qual combina com a frase de cima?")

# --- 23, 24 e 25: dentro do texto --------------------------------------------
TXT = bloco(u"TXT")
for _pi, _tk in ((23, u"tx1"), (24, u"tx2"), (25, u"tx3")):
    _T = TXT[_tk]
    _nw = 0
    for _lin in _T[u"linhas"]:
        for _w in _lin:
            p(u"tx%d_%d" % (_pi, _nw), _w)
            _nw += 1
    p(u"certo%d_t" % _pi, u"Muito bem! As palavras eram " + u", ".join(_T[u"ok"]) + u".")
    if _pi == 25:
        p(u"dica%d_t" % _pi,
          u"Olhe de novo: rainha, galinha, vizinha e farinha terminam parecido, "
          u"mas não falam de coisa pequena. Tire essas.")
    else:
        p(u"dica%d_t" % _pi,
          u"Leia o texto de novo, devagar. Procure o fim da palavra: é ele que conta o tamanho.")

# --- 26 e 27: os caça-palavras -----------------------------------------------
for _pi, _nome in ((26, u"CACA"), (27, u"CACA2")):
    _C = bloco(_nome)
    for _n, _k in enumerate(pote(_pi)):
        _P = _C[u"pal"][_k]
        p(u"cp_" + _k, _P[u"pista"] + u".")
        p(u"certo%d_%s" % (_pi, _k), elogio(_n) + u" Achou.")

# --- 28: a cruzadinha --------------------------------------------------------
CRZD = bloco(u"CRZD")
for _n, _k in enumerate(pote(28)):
    _P = CRZD[_k]
    p(u"crz_" + _k, lp(_P[u"d"]))
    p(u"certo28_" + _k, elogio(_n) + u" " + lp(_P[u"d"]) + u" " + _P[u"p"].capitalize() + u".")
    p(u"dica28_" + _k, u"Conte as casinhas e diga a palavra em voz alta. "
                       u"O fim dela você já usou muitas vezes neste caderno.")

# --- 32: o caminho de volta --------------------------------------------------
VOLTA = bloco(u"VOLTA")
for _n, _k in enumerate(pote(32)):
    _X = VOLTA[_k]
    palavras(_X[u"g"], *_X[u"ops"])
    p(u"certo32_" + _k, elogio(_n) + u" %s vem de %s." % (_X[u"g"].capitalize(), _X[u"r"]))
    p(u"dica32_" + _k, u"Tape o fim da palavra com o dedo e leia só o começo. "
                       u"Que palavra sobra?")

# --- 34: a produção ----------------------------------------------------------
PROD = bloco(u"PROD")
for _n, _k in enumerate(pote(34)):
    _X = PROD[_k]
    p(u"prd_" + _k, u"Escreva " + _X[u"q"] + u".")
    p(u"certo34_" + _k, elogio(_n) + u" A palavra é sua e está no tamanho certo.")
    p(u"dica34_" + _k, u"Pense primeiro na coisa, depois no fim que ela precisa ganhar. "
                       u"Vale qualquer palavra de verdade.")

# --- 35: o cartaz ⭐ os nomes vêm por último -----------------------------------
CART = bloco(u"CART")
for _L in CART[u"linhas"]:
    p(u"cart_" + _L[u"k"], u"%s: %s. Por exemplo, %s." % (_L[u"t"].capitalize(), _L[u"d"], _L[u"e"]))
_CARTCERTO = {u"d": u" é a palavra do pequenininho: chama-se diminutivo.",
              u"n": u" é a palavra do tamanho de sempre: o grau normal.",
              u"a": u" é a palavra do grandão: chama-se aumentativo."}
for _n, _k in enumerate(pote(35)):
    _X = CART[u"exem"][_k]
    palavras(_X[u"p"])
    p(u"certo35_" + _k, elogio(_n) + u" " + _X[u"p"].capitalize() + _CARTCERTO[_X[u"c"]])
    p(u"dica35_" + _k, u"Olhe o fim da palavra e compare com o exemplo de cada linha do cartaz.")


# ==============================================================================
#  AS SÍLABAS FALADAS — e este bloco é obrigatório em caderno que fale sílaba
#
#  ⚠️⚠️ POR QUE NÃO DÁ PARA SINTETIZAR A SÍLABA SOLTA (e a casa já pagou por
#     isto DUAS vezes — set/2026 e 16/set/2026, as duas o Marcos ouvindo):
#     a voz não lê SOM, lê PALAVRA. Entregue "SA" a ela e ela soletra "esse-á";
#     "VA" vira "vê-á"; "ÇÃ" ela nem tenta, porque ç não começa palavra em
#     português. Escrever a sílaba "como se fala" conserta UM caso e nunca
#     fecha a família.
#
#  O QUE FUNCIONA é o contrário: gravar a PALAVRA INTEIRA — que a voz pronuncia
#  certo, porque é palavra de verdade — alinhar letra a letra com o
#  `ctc-forced-aligner` e CORTAR a sílaba de dentro dela. Quem faz isso é o
#  `_padrao/silabas_voz.py`, dentro do `entregar.yml`, lendo o `silabas.json`
#  que sai daqui. O portão é o `_qa/silabas.py`.
#
#  COMO SE USA: para cada palavra do caderno, uma linha
#      _reg(u"CAVALO", [u"CA", u"VA", u"LO"])
#  e, no app, a sílaba fala por `falarSilaba(null, 0, "VA")` — nunca por
#  `falar("sil_va")`. Caderno que não fala sílaba não escreve nada: o
#  `silabas.json` sai com `"palavras": {}` e o `entregar.yml` nem baixa o
#  alinhador por ele.
#
#  ⚠️ NÃO HÁ FALA DE RESERVA POR SÍLABA. Faltando o recorte, o app diz a
#     PALAVRA INTEIRA. Uma reserva sintetizada seria o defeito voltando pela
#     porta dos fundos — e calado, que é pior.
# ==============================================================================
_SIL_DE = {}          # palavra -> [sílabas, NA ORDEM da palavra]
_MAPA_SIL = {}        # sílaba  -> [palavra, posição]
_RECUSADAS = []


def _reg(palavra, silabas):
    u"""⚠️ A LISTA TEM DE ESTAR NA ORDEM DA PALAVRA. O alinhador corta pelos
    limites das letras: ["RO","CAR"] para CARRO faz sair "ro" onde devia sair
    "car" — e a criança ouve o pedaço errado, sem erro nenhum na tela. Folha de
    ORDENAR guarda as sílabas EMBARALHADAS: passe-as por `_ordena` antes.
    ⚠️ E ganha sempre a partição MAIS FINA: "PIPO"+"CA" fecha PIPOCA sem ser
    separação silábica, e sobrescrevendo PI-PO-CA deixaria a sílaba PI muda."""
    silabas = list(silabas)
    if u"".join(silabas).upper() != palavra.upper():
        _RECUSADAS.append((palavra, silabas))
        return
    velha = _SIL_DE.get(palavra.lower())
    if velha and len(velha) >= len(silabas):
        return
    _SIL_DE[palavra.lower()] = silabas


def _ordena(palavra, embaralhadas):
    u"""as mesmas sílabas na ORDEM em que formam a palavra — sem inventar
    nenhuma: encaixa da esquerda para a direita e desiste se não fechar."""
    resto, saida, alvo = list(embaralhadas), [], palavra.upper()
    while alvo:
        for _i, _sb in enumerate(resto):
            if alvo.startswith(_sb.upper()):
                saida.append(_sb)
                alvo = alvo[len(_sb):]
                resto.pop(_i)
                break
        else:
            return None
    return saida if not resto else None


def _achaSilaba(s):
    u"""a palavra de onde a sílaba será recortada. Ganha a MAIS CURTA: menos
    letras na gravação, menos lugar para o alinhador errar."""
    cand = [_w for _w in sorted(_SIL_DE) if s in _SIL_DE[_w]]
    if not cand:
        return None
    _w = min(cand, key=lambda w: (len(_SIL_DE[w]), len(w), w))
    return [_w, _SIL_DE[_w].index(s)]


def _mapeia(soltas):
    u"""monta o SILMAP das sílabas que o app fala sozinhas, e DEVOLVE as órfãs.
    ⚠️ Sílaba órfã não é erro — o app diz a palavra inteira — mas tem de sair
    IMPRESSA, senão aquele botão emudece sem ninguém saber. Distratora que não
    mora em palavra nenhuma do caderno pede uma PALAVRA-CARREGADORA: uma
    palavra de verdade, curta, registrada só para ser gravada e cortada."""
    orfas = []
    for _s in sorted(set(soltas)):
        _achou = _achaSilaba(_s)
        if _achou:
            _MAPA_SIL[_s] = _achou
        else:
            orfas.append(_s)
    # e a PALAVRA INTEIRA de cada uma precisa existir como fala: é dela que o
    # recorte sai, e é ela que o app diz quando o recorte falta.
    for _w in sorted(_SIL_DE):
        p(u"pal_" + ch(_w), _w.upper() + u".")
    return orfas


_ORFAS = _mapeia([])          # <- passe aqui TODA sílaba que o app fala sozinha


# ---------------------------------------------------------------------------
# A SAÍDA
# ---------------------------------------------------------------------------
def chave(s):
    u"""O nome do mp3 sai do TEXTO, não da chave da fala — assim duas chaves que
    dizem a mesma frase gravam um arquivo só."""
    s = re.sub(r"\s+", u" ", s or u"").strip().lower()
    hh = 5381
    for c in s:
        hh = ((hh * 33) ^ ord(c)) & 0xFFFFFFFF
    d, out = hh, u""
    if d == 0:
        return u"0"
    while d:
        out = u"0123456789abcdefghijklmnopqrstuvwxyz"[d % 36] + out
        d //= 36
    return out


falas, vistos = [], {}
for k in sorted(F.keys()):
    txt = F[k]
    if not txt:
        continue
    c = chave(txt)
    if c in vistos:
        continue
    vistos[c] = 1
    falas.append({u"id": PREFIXO + c, u"texto": txt, u"voz": VOZ})

html = io.open(CAM, encoding=u"utf-8").read()
blocoF = (u"/*FALAS-INI*/\nvar FALAS = "
          + json.dumps(F, ensure_ascii=False, indent=1, sort_keys=True) + u";\n/*FALAS-FIM*/")
blocoV = (u"/*VOZOK-INI*/var VOZOK = "
          + json.dumps(dict((c, 1) for c in vistos), ensure_ascii=False) + u";/*VOZOK-FIM*/")
novo = re.sub(r"/\*FALAS-INI\*/.*?/\*FALAS-FIM\*/", lambda m: blocoF, html, flags=re.S)
novo = re.sub(r"/\*VOZOK-INI\*/.*?/\*VOZOK-FIM\*/", lambda m: blocoV, novo, flags=re.S)

# ⭐ o `silabas.json` é o que o `entregar.yml` lê para cortar cada sílaba de
#    dentro do mp3 da palavra inteira, e o `SILMAP` é o que o app usa para saber
#    de qual palavra veio cada pedaço. Uma fonte só para os dois.
io.open(os.path.join(AQUI, u"silabas.json"), u"w", encoding=u"utf-8").write(
    json.dumps({u"prefixo": PREFIXO, u"voz": VOZ,
                u"palavras": dict((w, _SIL_DE[w]) for w in sorted(_SIL_DE))},
               ensure_ascii=False, indent=1))
blocoS = (u"/*SILMAP-INI*/var SILMAP = "
          + json.dumps(_MAPA_SIL, ensure_ascii=False, sort_keys=True) + u";/*SILMAP-FIM*/")
novo = re.sub(r"/\*SILMAP-INI\*/.*?/\*SILMAP-FIM\*/", lambda m: blocoS, novo, flags=re.S)
io.open(CAM, u"w", encoding=u"utf-8").write(novo)
io.open(os.path.join(AQUI, u"falas.json"), u"w", encoding=u"utf-8").write(
    json.dumps(falas, ensure_ascii=False, indent=1))
io.open(os.path.join(AQUI, u"voz.txt"), u"w", encoding=u"utf-8").write(VOZ + u"\n")
print(u"FALAS: %d chaves; falas.json: %d fala(s) para gravar; "
      u"silabas: %d palavra(s) para recortar, %d silaba(s) no mapa"
      % (len(F), len(falas), len(_SIL_DE), len(_MAPA_SIL)))
if _ORFAS:
    print(u"   \u26a0\ufe0f %d silaba(s) SEM palavra de origem (o app dira a palavra "
          u"inteira): %s" % (len(_ORFAS), u", ".join(_ORFAS)))
if _RECUSADAS:
    print(u"   \u26a0\ufe0f %d lista(s) recusada(s) por nao formarem a palavra: %s"
          % (len(_RECUSADAS), u", ".join(
              u"%s=%s" % (w, u"-".join(sl)) for w, sl in _RECUSADAS[:8])))
