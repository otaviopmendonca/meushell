/* Separar a linha em palavras. PRONTO — nao precisa mexer. */
#ifndef LINHA_H
#define LINHA_H
#define MAX_PALAVRAS 64

/* Separa `linha` em palavras, respeitando aspas simples. Modifica `linha` no
   lugar e preenche v[] com ponteiros para dentro dela. Devolve quantas. */
int separar(char *linha, char *v[], int max);

/* Redirecionamentos encontrados numa linha de comando. */
struct redir { char *entrada; char *saida; int anexar; };

/* Tira de v[] os operadores < > >> e o arquivo que vem depois, preenchendo r.
   Devolve 0, ou -1 se faltar o nome do arquivo. PRONTO. */
int extrair_redir(char *v[], int *n, struct redir *r);
#endif
