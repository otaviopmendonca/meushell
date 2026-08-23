/*
 * Entrega 3 — segundo plano, `jobs` e sinais.
 *
 * O que precisa acontecer:
 *   - `comando &` nao trava o shell: ele anota o pid e volta a ler linhas;
 *   - `jobs` lista o que ainda esta vivo, um por linha: [n] pid comando
 *   - quem termina no segundo plano tem que ser COLHIDO — senao vira zumbi, e
 *     o verificador conta zumbis cujo pai e o shell de voces;
 *   - Ctrl-C mata o comando em primeiro plano e NAO mata o shell.
 *
 * Sobre colher: waitpid(-1, &status, WNOHANG) devolve >0 quando havia alguem
 * para colher e 0 quando nao havia. Num laco, antes de cada linha, resolve —
 * e evita a corrida que um tratador de SIGCHLD traria junto.
 *
 * Leiam antes: CONTRATOS.md secao 5, e entregas/E3.md.
 */
#include <stdio.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <sys/wait.h>
#include "comum.h"

void preparar_sinais(void)
{
    /* Chamada UMA vez, no inicio. Enquanto a Entrega 3 nao existe ela fica
       calada de proposito: reclamar aqui carimbaria a mensagem na saida de
       erro de toda execucao, inclusive nos testes da Entrega 1. O verificador
       cobra o comportamento — o shell sobreviver ao Ctrl-C —, nao a chamada.

       Aqui vai o signal(SIGINT, SIG_IGN) do shell. Lembre que o filho HERDA
       esse "ignorar": e executar.c que precisa devolver o padrao antes do
       execvp, senao o Ctrl-C nao mata comando nenhum. */
}

void anotar_trabalho(pid_t pid, const char *comando)
{
    (void)pid; (void)comando;
    FALTA_ESCREVER("a anotacao de trabalhos em segundo plano (Entrega 3)");
}

void colher_trabalhos(void)
{
    /* Enquanto a Entrega 3 nao existe, esta funcao nao faz nada e nao
       reclama: ela e chamada antes de CADA linha, e reclamar aqui encheria a
       saida de erro de ruido. O verificador cobra o resultado — zumbi zero —,
       nao a chamada. */
}

void listar_trabalhos(void)
{
    FALTA_ESCREVER("o embutido jobs (Entrega 3)");
}
