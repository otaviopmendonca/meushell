/*
 * meushell — o laco principal. PRONTO: nao precisa mexer aqui.
 *
 * Ele le uma linha, decide o que ela e, e chama a parte certa. As partes que
 * voces escrevem estao em executar.c, trabalhos.c e medir.c.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "comum.h"

int ultimo_codigo = 0;

/* Devolve 1 quando o shell deve encerrar. */
static int uma_linha(char *linha, int *saida_do_shell)
{
    colher_trabalhos();               /* quem terminou no segundo plano */

    char *barra = strchr(linha, '|');
    if (barra) {                      /* ---------- com cano ---------- */
        *barra = '\0';
        char *ve[MAX_PALAVRAS], *vd[MAX_PALAVRAS];
        int ne = separar(linha, ve, MAX_PALAVRAS);
        int nd = separar(barra + 1, vd, MAX_PALAVRAS);
        if (ne == 0 || nd == 0) {
            fprintf(stderr, "meushell: cano sem comando\n");
            ultimo_codigo = 1;
            return 0;
        }
        struct redir re, rd;
        if (extrair_redir(ve, &ne, &re) < 0 || extrair_redir(vd, &nd, &rd) < 0) {
            ultimo_codigo = 1;
            return 0;
        }
        ultimo_codigo = executar_com_cano(ve, ne, &re, vd, nd, &rd);
        return 0;
    }

    char *v[MAX_PALAVRAS];
    int n = separar(linha, v, MAX_PALAVRAS);
    if (n == 0) return 0;

    int fundo = 0;                    /* a linha terminava em & ? */
    if (!strcmp(v[n-1], "&")) { fundo = 1; v[--n] = NULL; }
    if (n == 0) return 0;

    /* embutidos que ja vem prontos */
    if (!strcmp(v[0], "sair")) {
        *saida_do_shell = (n > 1) ? atoi(v[1]) : 0;
        return 1;
    }
    if (!strcmp(v[0], "codigo")) {
        printf("%d\n", ultimo_codigo);
        fflush(stdout);
        ultimo_codigo = 0;
        return 0;
    }
    if (!strcmp(v[0], "cd")) {
        const char *destino = (n > 1) ? v[1] : getenv("HOME");
        if (!destino || chdir(destino) != 0) {
            fprintf(stderr, "meushell: cd: %s\n", destino ? destino : "");
            ultimo_codigo = 1;
        } else ultimo_codigo = 0;
        return 0;
    }
    if (!strcmp(v[0], "jobs")) {
        colher_trabalhos();
        listar_trabalhos();
        ultimo_codigo = 0;
        return 0;
    }

    struct redir r;
    if (extrair_redir(v, &n, &r) < 0) { ultimo_codigo = 1; return 0; }
    if (n == 0) { ultimo_codigo = 1; return 0; }

    if (!strcmp(v[0], "tempo") || !strcmp(v[0], "trocas") || !strcmp(v[0], "paginas")) {
        char qual[16];
        snprintf(qual, sizeof qual, "%s", v[0]);
        ultimo_codigo = medir(qual, v + 1, n - 1, &r);
        return 0;
    }

    ultimo_codigo = executar_comando(v, n, &r, fundo);
    return 0;
}

int main(void)
{
    preparar_sinais();
    setvbuf(stdout, NULL, _IOLBF, 0);

    char linha[1024];
    int saida = 0;
    for (;;) {
        /* Prompt SO para gente: quando a entrada e um terminal. O verificador
           alimenta o shell por um cano, e ai nao sai prompt nenhum. */
        if (isatty(0)) { printf("meushell$ "); fflush(stdout); }
        if (!fgets(linha, sizeof linha, stdin)) break;
        linha[strcspn(linha, "\r\n")] = '\0';
        char *p = linha;
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '\0' || *p == '#') continue;      /* linha vazia ou comentario */
        if (uma_linha(p, &saida)) break;
    }
    colher_trabalhos();
    return saida;
}
