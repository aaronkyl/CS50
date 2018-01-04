#include <stdio.h>
#include <cs50.h>

int main(void){
    
    // initialize height variable
    int height;
    
    // prompt user for height and repeat until valid number given
    do{
        printf("Height: ");
        height = get_int();
    }
    while(height > 23 || height < 0);
    
    // construct pyramid
    for(int row = 0; row < height; row++){

        // add padding spaces to row
        for(int i = 0; i < (height - row - 1); i++){
            printf(" ");
        }
        
        // add first pyramid's hashes to row
        for(int i = 0; i <= row; i++){
            printf("#");
        }
        
        // add middle spaces to row
        printf("  ");
        
        // add second pyramid's hashes to row
        for(int i = 0; i <= row; i++){
            printf("#");
        }
        
        // terminate line with newline character
        printf("\n");
    }
}