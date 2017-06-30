// header files
#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

// function declarations
void vigenere_cipher(string plaintext, string key);

// main
int main(int argc, string argv[]) {
    
    // confirm only one command-line argument has been provided and end program if not
    if(argc != 2){
        printf("Must provide one non-negative integer! Terminating program...\n");
        return 1;
    }
    
    // confirm key is composed of only alphabetic characters and end program if not
    for(int i = 0, n = strlen(argv[1]); i < n; i++) {
        if(!isalpha(argv[1][i])) {
            printf("Key must only contain alphabetic characters! Terminating program...\n");
            return 1;
        }
    }
    
    // get plaintext string from user
    printf("plaintext: ");
    string plaintext = get_string();
    
    // execute Vigenere's cipher on plaintext
    vigenere_cipher(plaintext, argv[1]);
    
    return 0;
}


void vigenere_cipher(string plaintext, string key) {
    // create counter for current character in key
    int k = 0;

    // prepare printout line with "ciphertext:"
    printf("ciphertext: ");

    // iterate through plaintext, character by character
    for(int i = 0, n = strlen(plaintext), k_length = strlen(key); i < n; i++) {
        // assign current character in plaintext to variable ptchar
        char ptchar = plaintext[i];
        // check if current character is letter; if not skip code
        if(isalpha(ptchar)) {
            // create variable to record if current character is uppercase or lowercase
            char a;
            // check if current character is uppercase or lowercase
            if(isupper(ptchar)) {
                a = 'A';
            } else {
                a = 'a';
            }
            // create variable to contain integer value of current key character
            int key_char;
            // check if current key character is uppercase or lowercase
            // assign integer value of current key character after zeroing out
            if(isupper(key[k % k_length])) {
                key_char = (int)(key[k % k_length] - 'A');
            } else {
                key_char = (int)(key[k % k_length] - 'a');
            }
            // print ciphered version of current plaintext character
            printf("%c", (((ptchar - a) + key_char) % 26) + a);
            // increment key counter
            k++;
            // escape loop
            continue;
        }
        // print current character if it was not a letter
        printf("%c", ptchar);
    }
    // print newline at end of cipher program
    printf("\n");
}
