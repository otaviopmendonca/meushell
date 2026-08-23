# Apresentação — demonstração e defesa

**Vale 1,0** · **04/12/2026** · em aula

Oito minutos por grupo: cinco de demonstração e três de alteração ao vivo.

---

## Os cinco minutos

1. **O shell rodando (30 s).** Ao vivo, no terminal, a partir do repositório.
   Um comando, um redirecionamento, um cano.
2. **Um processo nascendo (1,5 min).** Rodem `sleep 60 &` e, noutro terminal,
   mostrem o processo na árvore: quem é o pai, qual o estado. Depois matem o
   pai e mostrem o órfão sendo adotado. Isso vocês vão explicar, não só exibir.
3. **O cano por dentro (1 min).** `ls | wc -l` e, ao lado, o
   `/proc/<pid>/fd` mostrando o descritor apontando para `pipe:[...]`. É a
   diferença entre a saída certa e o mecanismo certo.
4. **Os números da Entrega 4 (2 min).** A tabela dos três programas, e a
   explicação da inversão entre trocas voluntárias e involuntárias. Se souberem
   dizer por que o `esperar` cede a CPU cento e cinquenta vezes e o `girar`
   quase nunca, vocês entenderam escalonamento.

## Os três minutos de alteração ao vivo

Cada grupo recebe **uma alteração pequena, sorteada na hora**, e tem dez
minutos para fazê-la funcionar:

- aceitar `2>` para redirecionar a saída de erro;
- fazer o `jobs` marcar com `[concluido]` quem já terminou;
- aceitar dois canos na mesma linha (`a | b | c`);
- um embutido `ultimo` que imprime o pid do último processo criado;
- colher pelo `SIGCHLD` em vez de antes de cada linha.

Podem consultar o código de vocês, o manual e a internet. O que não dá para
consultar é saber onde mexer.

## Como entregar

1. Slides em PDF (se usarem) até as 23h59 de 03/12.
2. O repositório com a Entrega 4 completa. Só apresenta quem entregou.
3. O ambiente **pronto para rodar**, testado no computador que vão usar.

## Como é avaliado

| | |
|---|---|
| A demonstração funciona e o processo é explicado, não só exibido | 0,4 |
| A alteração ao vivo | 0,3 |
| Os números da Entrega 4 interpretados corretamente | 0,2 |
| Todos falam, e o tempo é respeitado | 0,1 |
