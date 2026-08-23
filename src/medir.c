/*
 * Entrega 4 — o shell mede o sistema.
 *
 * Tres embutidos que rodam um comando e, DEPOIS que ele termina, contam o que
 * o sistema registrou. Tudo sai na saida de ERRO, para nao sujar a saida do
 * comando medido:
 *
 *   tempo   <cmd>   parede=<s> usuario=<s> sistema=<s>
 *   trocas  <cmd>   voluntarias=<n> involuntarias=<n>
 *   paginas <cmd>   menores=<n> maiores=<n> rss_pico_kb=<n>
 *
 * A chave e o wait4(): igual ao waitpid, mas com um quarto argumento
 * `struct rusage *`, que o nucleo preenche com a contabilidade do filho —
 * ru_utime, ru_stime, ru_nvcsw, ru_nivcsw, ru_minflt, ru_majflt, ru_maxrss.
 * O tempo de parede nao esta la: e voce quem mede, com clock_gettime, antes e
 * depois.
 *
 * O que se aprende aqui, e o que a apresentacao vai cobrar: um programa que so
 * calcula e um que so espera produzem numeros OPOSTOS. Se os seus derem
 * parecido, a medicao esta morta.
 *
 * Leiam antes: CONTRATOS.md secao 6, e entregas/E4.md.
 */
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include "comum.h"

int medir(const char *qual, char *v[], int n, struct redir *r)
{
    (void)qual; (void)v; (void)n; (void)r;
    FALTA_ESCREVER("as medicoes do sistema (Entrega 4)");
    return 3;
}
