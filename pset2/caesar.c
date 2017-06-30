// header files
#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

// function declarations
void caesar_cipher(string plaintext, int key);

// main
int main(int argc, string argv[]){
    
    // confirm only one command-line argument has been provided and end program if not
    if(argc != 2){
        printf("Must provide one non-negative integer! Terminating program...\n");
        return 1;
    }
    
    // get plaintext string from user
    printf("plaintext: ");
    string plaintext = get_string();
    
    // run plaintext through Caesar's cipher using the key provided on the command-line
    // atoi converts a string to an integer (argv is an array of strings)
    caesar_cipher(plaintext, atoi(argv[1]));
    
    // end program
    return 0;
}


void caesar_cipher(string plaintext, int key){
    // prepare printout line with "ciphertext:"
    printf("ciphertext: ");
    
    // iterate over each character in the plaintext string
    for(int i = 0, n = strlen(plaintext); i < n; i++){
        // assign current character to temporary variable
        char ptchar = plaintext[i];
        // check if current character is alpha character; if not skip this code
        if(isalpha(ptchar)){
            // declare variable to record if current character is uppercase or not
            char a;
            // set variable a to 'A' if current character is uppercase, else set
            // it to 'a'
            if(isupper(ptchar)){
                a = 'A';
            } else {
                a = 'a';
            }
            // change numeric ASCII value of current character to that of a
            // zero-indexed alphabet number by subtracting variable a, add 
            // the key, then divide by 26 (the length of the alphabet) to see 
            // if the key caused a loop from Z to A, then change the result 
            // back to an ASCII value by adding variable a and print it
            printf("%c", (((ptchar - a) + key) % 26) + a);
            // break out of current loop
            continue;
        }
        // print current character if it was not alphabetic
        printf("%c", ptchar);
    }
    //print newline character after plaintext has been iterated through entirely
    printf("\n");
}
