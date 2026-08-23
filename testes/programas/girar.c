/* so calcula: nao dorme, nao le disco */
#include <stdio.h>
int main(void){ volatile double x=0; for (long i=0;i<60000000L;i++) x+=i*0.5; printf("%.0f\n",x); return 0; }
