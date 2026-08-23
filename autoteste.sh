#!/bin/sh
# Autoteste do verificador.
#
# Nao confere o shell de voces. Confere o VERIFICADOR: constroi shells
# sabotados de proposito e exige que cada um fique VERMELHO. Um verificador
# que so sabe ficar verde nao esta verificando nada.
#
# A sabotagem mais importante e a do cano falso: ela produz a saida CERTA com
# o mecanismo ERRADO. Se o verificador nao pegar essa, ele esta conferindo
# texto, nao sistema operacional.

set -u
RAIZ=$(cd "$(dirname "$0")" && pwd)
REF="${SO_REFERENCIA:-$HOME/projetos/so-lab-gabarito/referencia.c}"
VERDE='\033[32m'; VERMELHO='\033[31m'; ZERO='\033[0m'
falhas=0

if [ ! -f "$REF" ]; then
  echo "Este autoteste precisa da implementacao de referencia, que fica com o"
  echo "professor. Voces nao precisam dele: rodem 'make verificar E=n'."
  exit 3
fi

banca=$(mktemp -d)
trap 'rm -rf "$banca"' EXIT
cp "$RAIZ/verificar.py" "$banca/"
cp -r "$RAIZ/testes" "$banca/"

montar() {
  cp "$REF" "$banca/motor.c"
  if [ -n "${2:-}" ]; then
    python3 - "$banca/motor.c" "$2" "$3" <<'PY'
import sys
caminho, antes, depois = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(caminho, encoding='utf-8').read()
if antes not in s:
    print(f'SABOTAGEM FALHOU: nao achei {antes!r}', file=sys.stderr); sys.exit(9)
open(caminho, 'w', encoding='utf-8').write(s.replace(antes, depois, 1))
PY
    [ $? -eq 9 ] && return 9
  fi
  gcc -w -O1 -o "$banca/meushell" "$banca/motor.c" 2>/dev/null || return 8
  return 0
}

exigir_vermelho() {
  nome="$1"; entrega="$2"
  if (cd "$banca" && python3 verificar.py "$entrega" >/dev/null 2>&1); then
    printf "  ${VERMELHO}CEGO${ZERO}  %s — o verificador passou mesmo assim\n" "$nome"
    falhas=$((falhas + 1))
  else
    printf "  ${VERDE}pega${ZERO}  %s\n" "$nome"
  fi
}

echo "── controle positivo: a referencia intacta"
montar intacta
if (cd "$banca" && python3 verificar.py todas >/dev/null 2>&1); then
  printf "  ${VERDE}ok${ZERO}    a referencia passa nas quatro entregas\n"
else
  printf "  ${VERMELHO}FALHA${ZERO} a referencia NAO passa — o verificador exige o impossivel\n"
  falhas=$((falhas + 1))
fi

echo "── sabotagens: cada uma tem que ser pega"

montar s1 "    _exit(127);" "    _exit(1);" \
  && exigir_vermelho "comando inexistente devolvendo 1 em vez de 127" 1

montar s2 '    printf("%d\n", ultimo_codigo);   /* codigo */' '    printf("0\n");' \
  && exigir_vermelho "o embutido codigo mentindo sempre zero" 1

# A JOIA: saida identica, mecanismo errado. Escreve num arquivo temporario e
# depois le de volta — o `wc -l` recebe os mesmos bytes, e nao ha cano nenhum.
montar s3 "        int fd[2];
        if (pipe(fd) < 0) { perror(\"pipe\"); ultimo_codigo = 1; return 0; }

        pid_t p1 = fork();
        if (p1 == 0) { dup2(fd[1], 1); close(fd[0]); close(fd[1]); virar_comando(ve, &re); }
        pid_t p2 = fork();
        if (p2 == 0) { dup2(fd[0], 0); close(fd[0]); close(fd[1]); virar_comando(vd, &rd); }
        close(fd[0]); close(fd[1]);
        int s1, s2;
        waitpid(p1, &s1, 0);
        waitpid(p2, &s2, 0);" \
"        const char *tmp = \"/tmp/cano-falso.txt\";
        int s1, s2;
        pid_t p1 = fork();
        if (p1 == 0) { int w = open(tmp, O_WRONLY|O_CREAT|O_TRUNC, 0644); dup2(w, 1); close(w); virar_comando(ve, &re); }
        waitpid(p1, &s1, 0);
        pid_t p2 = fork();
        if (p2 == 0) { int r2 = open(tmp, O_RDONLY); dup2(r2, 0); close(r2); virar_comando(vd, &rd); }
        waitpid(p2, &s2, 0);" \
  && exigir_vermelho "cano falso: arquivo temporario com a saida CERTA" 2

montar s4 "    signal(SIGINT, SIG_DFL);            /* o filho MORRE com Ctrl-C; o shell nao */" \
          "    /* o filho herda o ignorar do pai */" \
  && exigir_vermelho "filho herdando o 'ignorar SIGINT' do shell" 3

montar s5 "    while ((p = waitpid(-1, &status, WNOHANG)) > 0)" "    while (0)" \
  && exigir_vermelho "segundo plano nunca colhido (zumbi permanente)" 3

montar s6 'fprintf(stderr, "voluntarias=%ld involuntarias=%ld\n", ru.ru_nvcsw, ru.ru_nivcsw);' \
          'fprintf(stderr, "voluntarias=%d involuntarias=%d\n", 7, 7);' \
  && exigir_vermelho "medicao constante: numero que nao distingue nada" 4

echo
if [ "$falhas" -eq 0 ]; then
  printf "${VERDE}O verificador sabe ficar vermelho. Um verde dele vale.${ZERO}\n"
  exit 0
fi
printf "${VERMELHO}%s sabotagem(ns) passaram batido. O verificador esta cego ali.${ZERO}\n" "$falhas"
exit 1
