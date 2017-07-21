/**
 * Implements a dictionary's functionality.
 */

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <cs50.h>
#include <ctype.h>

#include "dictionary.h"

typedef struct node 
{
    char word[LENGTH + 1];
    struct node* next;
} node;

// create hash table array full of NULL values
node* hash_table[HASH_SIZE] = { NULL };

// create word counter and initialize to 0
int word_count = 0;

/**
 * Returns true if word is in dictionary else false.
 */
bool check(const char* word)
{
    int word_length = strlen(word);

    char text_word[word_length + 1];
    
    for (int i = 0; i < word_length; i++) {
            text_word[i] = tolower(word[i]);
    }
    
    text_word[word_length] = '\0';
    
    // initialize cursor to hash table pointer at location of word's hash
    node* cursor = hash_table[hash(text_word)];
    if (cursor == NULL) {
        return false;
    }
    
    while (true) {
        // if the word variable and the word at cursor are different, set cursor to current node's next
        if (strcmp(text_word, cursor->word) == 0) {
            // if words matched, return true
            return true;  
        } else if (strcmp(text_word, cursor->word) !=0) {
            // if last word in list reached, return false
            if (cursor->next == NULL) {
                return false;
            } else {
                // if words did not match, move to next word in list
                cursor = cursor->next;
            }
        }
    }
}

/**
 * Loads dictionary into memory. Returns true if successful else false.
 */
bool load(const char* dictionary)
{
    // open dictionary
    FILE* fp = fopen(dictionary, "r");
    
    // check that file opened
    if (fp == NULL) {
        return false;
    }
    
    while (true) {
        // malloc a new node
        node* new_node = malloc(sizeof(node));
        // check that new node is not null
        if (new_node == NULL) {
            unload();
            return false;
        }
        // read word from file
        fscanf(fp, "%s", new_node->word);
        // if line scanned is EOF, free new_node and fp pointers and break out of loop
        if (feof(fp)) {
            free(new_node);
            fclose(fp);
            break;
        }
        // increment word count
        word_count++;
        // hash the new word
        unsigned long hash_value = hash(new_node->word);

        // check if hash_table at index of hash is null
        if (hash_table[hash_value] == NULL) {
            // if null, set pointer in array to new_node and set new_node's next pointer to null
            hash_table[hash_value] = new_node;
            new_node->next = NULL;
        // else point new_node->next to existing array entry and point array to new_node
        } else {
            new_node->next = hash_table[hash_value];
            hash_table[hash_value] = new_node;
        }
    }
    return true;
}

/**
 * Returns number of words in dictionary if loaded else 0 if not yet loaded.
 */
unsigned int size(void)
{
    return word_count;
}

/**
 * Unloads dictionary from memory. Returns true if successful else false.
 */
bool unload(void)
{
    // go through hash table
    for (int i = 0; i < HASH_SIZE; i++) {
        // if current hash table entry is not null
        if (hash_table[i] != NULL) {
            // set both pointers to table entry
            node* cursor = hash_table[i];
            // iterate through linked list until next pointer is null
            while(true) {
                // set temp pointer to node pointed to by cursor
                node* temp = cursor;
                // set cursor to next node in list
                cursor = cursor->next;
                // if this is last item in list, free temp and break out of loop
                if(temp->next == NULL) {
                    free(temp);
                    break;
                }
                // free node temp points to
                free(temp);
            }
            free(cursor);
        }
    }
    return true;
}

/**
 * Hashes words to determine has table location
 * CREDIT: http://www.cse.yorku.ca/~oz/hash.html
 */
unsigned long hash(char* word)
{
    unsigned long hash = 5381;
    int c;

    while ((c = *word++))
        hash = ((hash << 5) + hash) + c; /* hash * 33 + c */

    return hash % HASH_SIZE;
}
