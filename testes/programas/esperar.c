/* so espera: cede a CPU o tempo todo */
#include <time.h>
int main(void){ struct timespec t={0,2000000}; for(int i=0;i<150;i++) nanosleep(&t,0); return 0; }
