/* Separar a linha em palavras. PRONTO — e trabalho de outra disciplina. */
#include <stdio.h>
#include <string.h>
#include "linha.h"

int separar(char *linha, char *v[], int max)
{
    int n = 0;
    char *p = linha;
    while (*p && n < max - 1) {
        while (*p == ' ' || *p == '\t') p++;
        if (!*p) break;
        if (*p == '\'') {                 /* aspas simples agrupam */
            p++;
            v[n++] = p;
            while (*p && *p != '\'') p++;
            if (*p) *p++ = '\0';
        } else {
            v[n++] = p;
            while (*p && *p != ' ' && *p != '\t') p++;
            if (*p) *p++ = '\0';
        }
    }
    v[n] = NULL;
    return n;
}

int extrair_redir(char *v[], int *n, struct redir *r)
{
    r->entrada = r->saida = NULL;
    r->anexar = 0;
    for (int i = 0; i < *n; ) {
        int achou = 0;
        if (!strcmp(v[i], "<"))       { r->entrada = v[i+1]; achou = 1; }
        else if (!strcmp(v[i], ">"))  { r->saida = v[i+1]; r->anexar = 0; achou = 1; }
        else if (!strcmp(v[i], ">>")) { r->saida = v[i+1]; r->anexar = 1; achou = 1; }
        if (achou) {
            if (!v[i+1]) {
                fprintf(stderr, "meushell: falta o arquivo depois de %s\n", v[i]);
                return -1;
            }
            for (int k = i; k + 2 <= *n; k++) v[k] = v[k+2];
            *n -= 2;
        } else i++;
    }
    v[*n] = NULL;
    return 0;
}
