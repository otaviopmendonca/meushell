/* O que as partes do shell combinam entre si. */
#ifndef COMUM_H
#define COMUM_H
#include "linha.h"

/* Codigo do ultimo comando — o embutido `codigo` imprime isto. */
extern int ultimo_codigo;

/* Marca uma parte que ainda nao foi escrita. Enquanto estiver aqui, o
   verificador sabe dizer "espera: <o que>" em vez de despejar um muro. */
#define FALTA_ESCREVER(o_que)                                        \
    do {                                                             \
        fprintf(stderr, "meushell: ainda falta escrever: %s\n", o_que); \
        ultimo_codigo = 3;                                           \
    } while (0)

/* ---- Entrega 1 e 2: executar.c ---- */
/* Roda um comando externo. `fundo` = 1 quando a linha terminava em &.
   Devolve o codigo do comando (ou 0 se foi para o segundo plano). */
int executar_comando(char *v[], int n, struct redir *r, int fundo);

/* Roda `esquerda | direita`. Devolve o codigo do comando da DIREITA. */
int executar_com_cano(char *ve[], int ne, struct redir *re,
                      char *vd[], int nd, struct redir *rd);

/* ---- Entrega 3: trabalhos.c ---- */
void anotar_trabalho(pid_t pid, const char *comando);  /* guarda um job */
void colher_trabalhos(void);                           /* colhe quem terminou */
void listar_trabalhos(void);                           /* o embutido `jobs` */
void preparar_sinais(void);                            /* chamado uma vez, no inicio */

/* ---- Entrega 4: medir.c ---- */
/* `qual` e "tempo", "trocas" ou "paginas". Devolve o codigo do comando. */
int medir(const char *qual, char *v[], int n, struct redir *r);
#endif
