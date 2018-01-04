#include <stdio.h>
#include <cs50.h>
#include <math.h>

int main(void){
    
    // delcare variables and cents array
    float change;
    int coins = 0;
    int centsArray[4] = {25,10,5,1};
    
    // prompt for change until non-negative float given
    do{
        printf("O hai! How much change is owed?\n");
        change = get_float();
    }
    while(change < 0);

    // convert user input to cents then round
    int cents_owed = round(change * 100);

    // cycle through array and increase coins count when cents_owed can be
    // divided by the current array value
    for(int i = 0; i < 4; i++) {
        if(cents_owed / centsArray[i] > 0){
            coins += (cents_owed / centsArray[i]);
            cents_owed -= (cents_owed / centsArray[i]) * centsArray[i];
        }
    }
    
    // print minimum number of coins required to provide change
    printf("%i\n", coins);
}