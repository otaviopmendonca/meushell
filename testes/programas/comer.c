/* toca 60 MB de memoria: faz falta de pagina menor a valer */
#include <stdlib.h>
#include <string.h>
int main(void){ size_t n=60u*1024*1024; char*p=malloc(n); for(size_t i=0;i<n;i+=4096) p[i]=1; return 0; }
