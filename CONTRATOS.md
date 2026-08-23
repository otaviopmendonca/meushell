# Contratos — o que o verificador exige do shell de vocês

O trabalho é um **shell**: um programa que lê linhas de comando e as executa.
Este arquivo diz como ele conversa com o mundo. Quando a intuição de vocês
discordar daqui, é este arquivo que vale.

---

## 1. Como o shell é chamado

O programa se chama `meushell` e nasce da compilação com `make`:

```
./meushell
```

Ele lê comandos da **entrada padrão**, um por linha, até o fim da entrada
(EOF) ou até o comando `sair`.

### 1.1 O prompt só existe para gente

```c
if (isatty(0)) { /* imprime o prompt */ }
```

Quando a entrada é um terminal, o shell imprime `meushell$ ` antes de cada
linha. Quando a entrada é um arquivo ou um cano — que é como o verificador
chama o shell — **ele não imprime prompt nenhum**.

Isso não é um truque para facilitar o teste: é como todo shell do mundo se
comporta, e é a primeira vez que vocês vão usar `isatty` para descobrir com
quem estão falando.

### 1.2 Código de saída do shell

| Código | Quando |
|---|---|
| 0 | terminou por `sair` ou por fim da entrada |
| o que vier de `sair N` | quando o `sair` recebe um número |

---

## 2. A linha de comando

Palavras separadas por espaços ou tabulações. Uma linha vazia não faz nada.
Uma linha que começa com `#` é comentário e não faz nada.

Aspas simples agrupam palavras: `echo 'um dois'` passa **um** argumento.

Não existe expansão de `*`, de `$VAR`, nem aspas duplas. Não é preguiça: é
escopo. O que se aprende aqui é processo, não análise de texto — isso vocês
já viram em outra disciplina.

---

## 3. Executar um comando

`ls -l` roda o programa `ls` com o argumento `-l`, **num processo novo**, e o
shell espera ele terminar antes de ler a próxima linha.

- O programa é procurado no `PATH` (use a família `execvp`).
- Comando que não existe: escreva na saída de erro
  `meushell: comando nao encontrado: <nome>` e guarde **127** como último código.
- O shell **nunca** morre porque o comando falhou.

### 3.1 Embutidos

Três comandos são do próprio shell — não geram processo:

| Comando | O que faz |
|---|---|
| `sair` / `sair N` | encerra o shell, com código 0 ou N |
| `cd <dir>` | troca o diretório do **próprio shell** |
| `codigo` | imprime, na saída padrão, o código do último comando, e mais nada |

`cd` precisa ser embutido, e vale a pena entender por quê: se fosse um
processo filho, quem mudaria de diretório seria o filho, que morre em
seguida. O pai continuaria onde estava. Essa é a lição.

---

## 4. Redirecionamento e cano

```
comando > arquivo      a saída padrão vai para o arquivo (cria ou trunca)
comando >> arquivo     a saída padrão vai para o fim do arquivo
comando < arquivo      a entrada padrão vem do arquivo
esquerda | direita     a saída da esquerda vira a entrada da direita
```

Um cano por linha, no máximo. O redirecionamento aparece depois do comando e
não vira argumento dele.

⚠️ **O cano tem que ser um cano.** Dá para produzir a saída certa gravando um
arquivo temporário no meio — e o verificador olha para
`/proc/<pid>/fd` do processo filho para conferir que o descritor 1 aponta
para `pipe:[...]`, não para um arquivo comum. Saída idêntica não salva.

---

## 5. Sinais e segundo plano

```
comando &        roda em segundo plano; o shell NÃO espera
jobs             lista o que está em segundo plano, um por linha:  [n] pid comando
```

- `Ctrl-C` (SIGINT) mata o comando em **primeiro plano** e **não** mata o shell.
- Processo que termina em segundo plano tem que ser **colhido**. Zumbi ao fim
  do roteiro é falha.

---

## 6. Medir o sistema

Três embutidos que rodam um comando e, depois, imprimem o que o sistema
registrou sobre ele. Cada um imprime **na saída de erro**, para não sujar a
saída do comando medido.

```
tempo <comando>      parede=<s> usuario=<s> sistema=<s>
trocas <comando>     voluntarias=<n> involuntarias=<n>
paginas <comando>    menores=<n> maiores=<n> rss_pico_kb=<n>
```

Os números saem de `wait4` com `struct rusage`, ou de `/proc/<pid>/status` —
a escolha é de vocês. Os segundos têm **três casas decimais**.

O verificador **não** compara esses números com valores fixos: eles mudam a
cada execução. Ele compara **relações** entre execuções — um programa que só
calcula e um que só espera precisam dar perfis diferentes. Se derem iguais, a
medição está morta, e um número que não distingue nada não mede nada.

---

## 7. O que o verificador faz

Ele alimenta o shell com um **roteiro** (um arquivo de comandos), compara a
saída padrão byte a byte com o esperado, e depois olha o **estado do sistema**:
zumbis deixados para trás, para onde apontam os descritores, se o shell
sobreviveu ao sinal.

Saída em UTF-8, sem BOM. Fim de linha `\n` (CRLF é tolerado: o verificador
normaliza).
