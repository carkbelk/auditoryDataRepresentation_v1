// C program to implement one side of FIFO 
// This side reads input from named pipe "/tmp/myfifo", then prints it 
#include <stdio.h> 
#include <string.h> 
#include <fcntl.h> 
#include <sys/stat.h> 
#include <sys/types.h> 
#include <unistd.h> 
#include <stdlib.h>
  
int main() 
{ 
    int fd1; 
    int value = 1;
  
    // FIFO file path 
    char * myfifo = "/tmp/myfifo"; 
  
    // Creating the named file(FIFO) 
    // mkfifo(<pathname>,<permission>) 
    mkfifo(myfifo, 0666); 
  
    char str1[80], str2[80]; 
    while (value)
    { 
        // First open in read only and read 
        fd1 = open(myfifo,O_RDONLY); 
        read(fd1, str1, 80);
	 
	char * values = strtok(str1, " ");

	while(values != NULL)
	{
		value = atoi(values);
		if(value)
		{
        		// Print the read string and close 
        		//printf("string %s\n", str1); 
			printf("%d ",value);
		}
		values = strtok(NULL, " ");
	}

	printf("\n");
	fflush( stdout ); // Force this for immediate use in pipe

        close(fd1);
    } 
    return 0; 
}
