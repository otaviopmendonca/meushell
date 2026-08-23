#!/usr/bin/env python3
"""
Verificador das entregas do trabalho semestral de Sistemas Operacionais.

  python3 verificar.py 1      confere a Entrega 1
  python3 verificar.py 4      confere a Entrega 4 (e todas as anteriores)
  python3 verificar.py todas

Ele nao le o codigo de voces. Ele alimenta o ./meushell com roteiros, compara
a saida, e depois olha o ESTADO DO SISTEMA: zumbi deixado para tras, para onde
apontam os descritores, se o shell sobreviveu ao sinal. Saida igual com
mecanismo errado nao passa.
"""
import os, re, signal, subprocess, sys, time

RAIZ = os.path.dirname(os.path.abspath(__file__))
T = os.path.abspath(os.environ.get('SO_TESTES') or os.path.join(RAIZ, 'testes'))
SHELL = os.path.join(RAIZ, 'meushell')
ROTEIRO_SINAL = 'sleep 5\ncodigo\necho SOBREVIVI\nsair\n'

VERDE, VERMELHO, AMARELO, CINZA, ZERO = '\033[32m', '\033[31m', '\033[33m', '\033[90m', '\033[0m'
if not sys.stdout.isatty():
    VERDE = VERMELHO = AMARELO = CINZA = ZERO = ''

FALTA = re.compile(r'ainda falta escrever: (.+?)\s*$', re.M)


def normalizar(texto):
    """O pid do `jobs` muda a cada execucao — nao da para compara-lo."""
    return re.sub(r'^\[(\d+)\] \d+ ', r'[\1] <pid> ', texto, flags=re.M)


class Placar:
    def __init__(self):
        self.ok = self.falhas = 0
        self.pendentes = {}
    def certo(self, nome):
        self.ok += 1
        print(f'  {VERDE}ok{ZERO}   {nome}')
    def errado(self, nome, esperado, veio, erro=''):
        self.falhas += 1
        m = FALTA.search(erro or '') or FALTA.search(veio or '')
        if m:
            fase = m.group(1)
            self.pendentes[fase] = self.pendentes.get(fase, 0) + 1
            print(f'  {CINZA}--{ZERO}   {nome} {CINZA}(espera: {fase}){ZERO}')
            return
        print(f'  {VERMELHO}FALHA{ZERO} {nome}')
        print(f'         esperado: {CINZA}{esperado}{ZERO}')
        print(f'         veio:     {CINZA}{veio}{ZERO}')


def rodar_roteiro(caminho, limite=20):
    with open(caminho) as f:
        entrada = f.read()
    try:
        p = subprocess.run([SHELL], input=entrada, capture_output=True,
                           text=True, timeout=limite, cwd=RAIZ)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, '', f'passou de {limite} s sem terminar'


def abrir_com_roteiro(texto):
    """
    Entrega o roteiro ao shell por um ARQUIVO, nao por um cano que fica aberto.

    Com cano aberto, um shell que so produza saida depois do EOF nunca produz
    nada — e a prova fica esperando para sempre. Com arquivo, o EOF ja esta
    la desde o comeco e o shell anda no ritmo dele.
    """
    import tempfile
    fh = tempfile.NamedTemporaryFile('w', suffix='.sh', delete=False)
    fh.write(texto)
    fh.close()
    entrada = open(fh.name)
    proc = subprocess.Popen([SHELL], stdin=entrada, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, cwd=RAIZ,
                            start_new_session=True)
    return proc, fh.name


def encerrar(proc, caminho, limite=12):
    try:
        saida, err = proc.communicate(timeout=limite)
    except subprocess.TimeoutExpired:
        proc.kill()
        saida, err = proc.communicate()
    try:
        os.unlink(caminho)
    except OSError:
        pass
    return saida, err


def diferenca(esperado, veio):
    a, b = esperado.rstrip('\n').split('\n'), veio.rstrip('\n').split('\n')
    for i in range(max(len(a), len(b))):
        la = a[i] if i < len(a) else '<acabou>'
        lb = b[i] if i < len(b) else '<acabou>'
        if la != lb:
            return f'linha {i+1}: {la!r}', f'linha {i+1}: {lb!r}'
    return repr(esperado[:60]), repr(veio[:60])


def caminho_teste(*partes):
    """Caminho a passar para o shell: relativo quando o corpus e o do repo."""
    caminho = os.path.join(T, *partes)
    rel = os.path.relpath(caminho, RAIZ)
    return rel if not rel.startswith('..') else caminho


def roteiros(prefixo):
    d = os.path.join(T, 'roteiros')
    return sorted(x for x in os.listdir(d) if x.startswith(prefixo) and x.endswith('.sh'))


def conferir_roteiros(p, prefixo):
    for nome in roteiros(prefixo):
        base = nome[:-3]
        cam = os.path.join(T, 'roteiros', nome)
        cod, saida, err = rodar_roteiro(cam)
        esperado = open(os.path.join(T, 'roteiros', base + '.saida')).read()
        cod_esperado = int(open(os.path.join(T, 'roteiros', base + '.codigo')).read().strip())
        if normalizar(saida) != normalizar(esperado):
            e, v = diferenca(normalizar(esperado), normalizar(saida))
            p.errado(f'roteiro {base}', e, v, err)
        elif cod != cod_esperado:
            p.errado(f'roteiro {base}', f'o shell sair com codigo {cod_esperado}',
                     f'saiu com {cod}', err)
        else:
            p.certo(f'roteiro {base}')


# ---------------------------------------------------- provas de comportamento

def filhos_de(pid):
    saida = []
    for d in os.listdir('/proc'):
        if not d.isdigit():
            continue
        try:
            with open(f'/proc/{d}/stat') as f:
                campos = f.read().rsplit(')', 1)[1].split()
            estado, ppid = campos[0], int(campos[1])
            if ppid == pid:
                saida.append((int(d), estado))
        except (OSError, IndexError, ValueError):
            pass
    return saida


def conferir_compilou(p):
    if os.path.exists(SHELL) and os.access(SHELL, os.X_OK):
        p.certo('./meushell existe e e executavel')
    else:
        p.errado('./meushell existe e e executavel', 'o binario compilado por make',
                 'nao existe — rode make')


def conferir_sem_zumbi(p):
    """
    Um comando em segundo plano que termina e nao e colhido vira zumbi. Este
    teste olha o estado do sistema ENQUANTO o shell ainda vive: depois que ele
    morre, os filhos sao adotados pelo init e o zumbi some — o defeito
    desapareceria junto com a prova.
    """
    nome = 'nao sobra zumbi do segundo plano'
    # O zumbi e transitorio: enquanto o shell espera um filho em PRIMEIRO plano,
    # o waitpid daquele pid nao colhe o outro. Por isso a prova olha DEPOIS que
    # o shell voltou a processar linhas — se ali ainda houver zumbi, e porque
    # ninguem colhe nunca.
    entrada = 'sleep 0.2 &\nsleep 1\necho pronto\nsleep 3\nsair\n'
    try:
        proc, arq = abrir_com_roteiro(entrada)
        time.sleep(1.8)          # ja passou do `echo pronto` e entrou na linha seguinte
        zumbis = [pid for pid, est in filhos_de(proc.pid) if est == 'Z']
        _, err = encerrar(proc, arq)
    except Exception as e:
        p.errado(nome, 'o shell rodando', str(e)); return
    if zumbis:
        p.errado(nome, 'nenhum filho em estado Z',
                 f'{len(zumbis)} zumbi(s): pid {zumbis[0]} — falta colher com waitpid/WNOHANG', err)
    else:
        p.certo(nome)


def conferir_cano_e_cano(p):
    """
    Da para produzir a saida certa do `|` gravando um arquivo temporario no
    meio. Aqui a prova nao e a saida: e para onde o descritor aponta.
    """
    nome = 'o cano e um cano de verdade'
    try:
        proc, arq = abrir_com_roteiro('sleep 1 | cat\nsair\n')
        alvo = destino = None
        for _ in range(30):
            time.sleep(0.1)
            for pid, _est in filhos_de(proc.pid):
                try:
                    cmd = open(f'/proc/{pid}/cmdline').read()
                    if 'sleep' in cmd:
                        destino = os.readlink(f'/proc/{pid}/fd/1')
                        alvo = pid
                        break
                except OSError:
                    pass
            if alvo:
                break
        _, err = encerrar(proc, arq)
    except Exception as e:
        p.errado(nome, 'o shell rodando', str(e)); return
    if alvo is None:
        p.errado(nome, 'os dois lados do cano rodando ao mesmo tempo',
                 'nao achei o processo da esquerda vivo', err)
    elif not destino.startswith('pipe:'):
        p.errado(nome, "a saida do primeiro apontando para pipe:[...]",
                 f'aponta para {destino} — isso nao e um cano', err)
    else:
        p.certo(nome)


def conferir_sobrevive_ao_sinal(p):
    """
    Ctrl-C manda SIGINT para o grupo inteiro: o shell E o filho recebem. O
    shell tem que ignorar; o filho tem que morrer. Se o shell nao devolver o
    padrao ao filho antes do execvp, o filho herda o "ignorar" e nao morre.
    """
    nome = 'Ctrl-C mata o filho e nao o shell'
    # `codigo` responde a OUTRA metade: 130 e 128+2, ou seja, o filho morreu
    # pelo sinal 2. Se tivesse herdado o "ignorar", terminaria sozinho com
    # codigo 0 — e o SOBREVIVI sairia igual. Conferir so o SOBREVIVI seria um
    # teste que nao sabe dizer o lado.
    try:
        proc, arq = abrir_com_roteiro(ROTEIRO_SINAL)
        # `codigo` depois do sleep responde a OUTRA metade da pergunta: 130 e
        # 128+2, ou seja, o filho morreu pelo sinal 2. Se ele tivesse ignorado
        # o SIGINT, terminaria sozinho e o codigo seria 0 — com o SOBREVIVI
        # saindo igual. Conferir so o SOBREVIVI e um teste que nao diz o lado.
        time.sleep(0.8)
        os.killpg(os.getpgid(proc.pid), signal.SIGINT)
        saida, err = encerrar(proc, arq)
    except subprocess.TimeoutExpired:
        proc.kill()
        p.errado(nome, 'o shell continuar depois do sinal',
                 'o shell travou — o filho provavelmente herdou o "ignorar" do SIGINT')
        return
    except Exception as e:
        p.errado(nome, 'o shell rodando', str(e)); return
    if 'SOBREVIVI' not in saida:
        p.errado(nome, 'o shell continuar lendo comandos depois do Ctrl-C',
                 'o shell morreu junto com o filho', err)
    elif '130' not in saida.split('SOBREVIVI')[0]:
        p.errado(nome, 'o filho morrendo pelo sinal (codigo 130 = 128 + SIGINT)',
                 f'codigo {saida.splitlines()[0] if saida.splitlines() else "?"} — '
                 'o filho herdou o "ignorar" do shell e sobreviveu ao Ctrl-C', err)
    else:
        p.certo(nome)


# ------------------------------------------------------------ Entrega 4

def medir(comando, qual, limite=25):
    cod, _saida, err = rodar_roteiro_texto(f'{qual} {comando}\nsair\n', limite)
    numeros = dict(re.findall(r'(\w+)=([\d.]+)', err))
    return {k: float(v) for k, v in numeros.items()}, err


def rodar_roteiro_texto(entrada, limite=25):
    try:
        p = subprocess.run([SHELL], input=entrada, capture_output=True,
                           text=True, timeout=limite, cwd=RAIZ)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, '', 'passou do tempo'


def conferir_medicoes(p):
    girar = caminho_teste('programas', 'girar') + ' > /dev/null'
    esperar = caminho_teste('programas', 'esperar')
    comer = caminho_teste('programas', 'comer')
    if not girar.startswith('/'):
        girar, esperar, comer = './' + girar, './' + esperar, './' + comer

    t_girar, e1 = medir(girar, 'tempo')
    t_esperar, e2 = medir(esperar, 'tempo')
    nome = 'tempo separa quem calcula de quem espera'
    if not {'parede', 'usuario'} <= t_girar.keys():
        p.errado(nome, 'parede=<s> usuario=<s> sistema=<s>', (e1.strip() or '(nada)')[:90], e1)
    elif not (t_girar['usuario'] >= 0.5 * t_girar['parede']):
        p.errado(nome, 'no ./girar, usuario perto da parede (ele so calcula)',
                 f"usuario={t_girar['usuario']} parede={t_girar['parede']}", e1)
    elif not (t_esperar.get('usuario', 9) <= 0.3 * max(t_esperar.get('parede', 0), 1e-9)):
        p.errado(nome, 'no ./esperar, usuario MUITO menor que a parede (ele so dorme)',
                 f"usuario={t_esperar.get('usuario')} parede={t_esperar.get('parede')}", e2)
    else:
        p.certo(nome)

    c_girar, e3 = medir(girar, 'trocas')
    c_esperar, e4 = medir(esperar, 'trocas')
    nome = 'trocas de contexto invertem entre os dois perfis'
    if 'voluntarias' not in c_girar or 'voluntarias' not in c_esperar:
        p.errado(nome, 'voluntarias=<n> involuntarias=<n>', (e3.strip() or '(nada)')[:90], e3)
    elif not (c_esperar['voluntarias'] >= 10 * max(c_girar['voluntarias'], 1)):
        p.errado(nome, 'o ./esperar cedendo a CPU MUITO mais vezes que o ./girar',
                 f"esperar={c_esperar['voluntarias']} girar={c_girar['voluntarias']} — "
                 'se der parecido, a medicao nao esta medindo', e4)
    else:
        p.certo(nome)

    g_comer, e5 = medir(comer, 'paginas')
    g_esperar, e6 = medir(esperar, 'paginas')
    nome = 'faltas de pagina acompanham a memoria tocada'
    if 'menores' not in g_comer or 'rss_pico_kb' not in g_comer:
        p.errado(nome, 'menores=<n> maiores=<n> rss_pico_kb=<n>', (e5.strip() or '(nada)')[:90], e5)
    elif not (g_comer['menores'] >= 10 * max(g_esperar.get('menores', 1), 1)):
        p.errado(nome, 'o ./comer com MUITO mais faltas menores que o ./esperar',
                 f"comer={g_comer['menores']} esperar={g_esperar.get('menores')}", e6)
    elif not (g_comer['rss_pico_kb'] >= 40000):
        p.errado(nome, 'o ./comer com pico de RSS acima de 40 MB (ele toca 60)',
                 f"rss_pico_kb={g_comer['rss_pico_kb']}", e5)
    else:
        p.certo(nome)


# ------------------------------------------------------------- as entregas

def entrega1(p):
    conferir_compilou(p)
    conferir_roteiros(p, 'e1')

def entrega2(p):
    entrega1(p)
    conferir_roteiros(p, 'e2')
    conferir_cano_e_cano(p)

def entrega3(p):
    entrega2(p)
    conferir_roteiros(p, 'e3')
    conferir_sem_zumbi(p)
    conferir_sobrevive_ao_sinal(p)

def entrega4(p):
    entrega3(p)
    conferir_medicoes(p)

ENTREGAS = {1: entrega1, 2: entrega2, 3: entrega3, 4: entrega4}

ONDE = [
    ('criacao de processos', 'src/executar.c', 'CONTRATOS.md secao 3'),
    ('redirecionamento',     'src/executar.c', 'CONTRATOS.md secao 4'),
    ('cano',                 'src/executar.c', 'CONTRATOS.md secao 4'),
    ('sinais',               'src/trabalhos.c', 'CONTRATOS.md secao 5'),
    ('trabalhos',            'src/trabalhos.c', 'CONTRATOS.md secao 5'),
    ('jobs',                 'src/trabalhos.c', 'CONTRATOS.md secao 5'),
    ('medicoes',             'src/medir.c',     'CONTRATOS.md secao 6'),
]

def onde_escrever(fase):
    for chave, arquivo, leitura in ONDE:
        if chave in fase:
            return arquivo, leitura
    return None, None


def main(argv):
    if not argv or argv[0] not in ('1', '2', '3', '4', 'todas'):
        print(__doc__.strip()); return 1
    quais = [1, 2, 3, 4] if argv[0] == 'todas' else [int(argv[0])]
    geral = 0
    for n in quais:
        print(f'\n{AMARELO}══ Entrega {n} ══{ZERO}')
        p = Placar()
        ENTREGAS[n](p)
        total = p.ok + p.falhas
        esperando = sum(p.pendentes.values())
        if not p.falhas:
            print(f'{VERDE}Entrega {n}: {p.ok} de {total} passaram.{ZERO}')
            continue
        geral = 1
        if esperando == p.falhas:
            print(f'{AMARELO}Entrega {n}: {p.ok} de {total} provas passaram; '
                  f'{esperando} esperam codigo que ainda nao existe.{ZERO}')
        else:
            print(f'{VERMELHO}Entrega {n}: {p.falhas} de {total} falharam'
                  + (f' ({esperando} por falta de codigo).' if esperando else '.') + ZERO)
        if p.pendentes:
            print(f'\n{AMARELO}▸ Por onde comecar{ZERO}')
            for fase, quantas in p.pendentes.items():
                arquivo, leitura = onde_escrever(fase)
                print(f'  Falta escrever: {fase} — {quantas} prova(s) dependem dela.')
                if arquivo:
                    print(f'  Escreva em {VERDE}{arquivo}{ZERO}. Leia antes: {CINZA}{leitura}{ZERO}')
            print(f'  O enunciado completo esta em {CINZA}entregas/E{n}.md{ZERO}')
    return geral


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
