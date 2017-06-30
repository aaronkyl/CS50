// header files
#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>

// function declarations
bool at_lst_one_ltr(string s);
void print_initials(string name);

// main
int main(void){
    // get name from user
    string name = get_string();
    
    // check to see if the name entered has at least one character;
    // do not run if it does not
    if(at_lst_one_ltr(name)){
        
        // call function to print initials from name
        print_initials(name);
    }
}

// function to determine if entered name has at least one letter
bool at_lst_one_ltr(string s){
    // iterate through string and if current character is not a space
    // return true (1)
    for(int i = 0, n = strlen(s); i < n; i++){
        if(s[i] != ' '){
            return true;
        }
    }
    
    // if all characters in the string were spaces, return false (0)
    return false;
}

// function to print first character from each word
void print_initials(string name){
    // create flag to record if last character examined in the following 
    // for loop was a space; starting as true so first character in name 
    // is added to the initials array if no leading spaces
    bool last_was_space = true;
    
    // iterate through array and print each words's first character
    for(int i = 0, n = strlen(name); i < n; i++){
        // if last character was a space and this one is too, skip rest of loop
        if(last_was_space && name[i] == ' '){
            continue;
        }
        
        // if last character was a space print uppercare version of current
        // character then reset 'last character was space' flag to false since
        // this character is not a space
        if(last_was_space){
            printf("%c", toupper(name[i]));
            last_was_space = false;
            continue;
        }
        
        // if current character is a space set 'last character was space' flag 
        // to true
        if(name[i] == ' '){
            last_was_space = true;
        }
    }
    
    // print newline character after all initials printed
    printf("\n");
}
