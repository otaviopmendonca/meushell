# Trabalho semestral de Sistemas Operacionais — meushell
#
#   make                   compila o shell
#   make verificar E=1     confere a Entrega 1
#   make verificar         confere as quatro
#   make prova             roda a verificacao num CLONE LIMPO (o que a correcao faz)
#   make evidencias E=1    grava evidencias/verificacao-1.txt para entregar
#   make limpar            apaga o que a compilacao gerou

CC      := gcc
CFLAGS  := -Wall -Wextra -g -std=c11 -D_GNU_SOURCE
PY      := python3
FONTES  := src/meushell.c src/linha.c src/executar.c src/trabalhos.c src/medir.c
E       :=

.PHONY: all verificar prova evidencias limpar autoteste ajuda

all: meushell testes/programas/girar testes/programas/esperar testes/programas/comer

meushell: $(FONTES) src/comum.h src/linha.h
	@$(CC) $(CFLAGS) -o $@ $(FONTES)
	@echo "meushell compilado"

testes/programas/%: testes/programas/%.c
	@$(CC) -O0 -o $@ $<

ajuda:
	@sed -n '/^# Trabalho/,/^$$/p' Makefile | sed 's/^# \{0,1\}//'

verificar: all
	@$(PY) verificar.py $(if $(E),$(E),todas)

# A correcao clona o repositorio de voces numa maquina limpa. Isto faz o mesmo,
# aqui, antes de entregar: pega arquivo nao commitado, caminho absoluto e
# binario que so existe na pasta de voces.
prova:
	@if [ ! -d .git ]; then echo "Isto precisa de um clone git (nao achei .git)."; exit 1; fi
	@sujos=`git status --porcelain | wc -l`; \
	 if [ "$$sujos" -gt 0 ]; then \
	   echo "ATENCAO: $$sujos arquivo(s) alterado(s) e ainda NAO commitado(s):"; \
	   git status --porcelain | sed 's/^/     /'; \
	   echo "  A correcao so enxerga o que esta commitado."; echo ""; \
	 fi
	@tmp=`mktemp -d`; \
	 git clone -q . $$tmp/prova; \
	 echo "Verificando um clone limpo do que esta commitado:"; \
	 ( cd $$tmp/prova && make --no-print-directory verificar $(if $(E),E=$(E),) ); \
	 estado=$$?; rm -rf $$tmp; echo ""; \
	 if [ $$estado -eq 0 ]; then echo "O clone limpo passou. Isto e o que a correcao vai ver."; \
	 else echo "O clone limpo NAO passou. Se aqui na sua pasta passa, falta commitar algo."; fi; \
	 exit $$estado

evidencias: all
	@if [ -z "$(E)" ]; then echo "diga qual: make evidencias E=1"; exit 1; fi
	@mkdir -p evidencias
	@$(PY) verificar.py $(E) > evidencias/verificacao-$(E).txt 2>&1; \
	  estado=$$?; echo "gravado em evidencias/verificacao-$(E).txt"; \
	  if [ $$estado -ne 0 ]; then \
	    echo "ATENCAO: a verificacao falhou. A evidencia registra a falha —"; \
	    echo "e isso e melhor do que entregar sem evidencia nenhuma."; fi

limpar:
	@rm -f meushell testes/programas/girar testes/programas/esperar testes/programas/comer
	@rm -f testes/roteiros/*.saida-obtida
	@echo "limpo"

autoteste:
	@./autoteste.sh
