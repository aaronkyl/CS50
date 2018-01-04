#include <stdio.h>
#include <cs50.h>

int main(void){
    // get card_number from user
    printf("Number: ");
    long long entered_card_number = get_long_long();
    long long card_number = entered_card_number;
    // initialize checksum variable and card number length variable
    int checksum = 0;
    int card_number_length = 0;
    
    // calculate the checksum for the card number using Luhn's algorithm and
    // count card number length
    while(card_number > 0){
        // add last digit in card_number to checksum
        checksum += card_number % 10;
        // remove last digit from card_number and increment card_number_length
        card_number /= 10;
        card_number_length += 1;
        // if last digit in card_number times 2 >= 10, add the two digits of that number
        // to checksum, otherwise add that single digit to the checksum
        if(((card_number % 10) * 2) >= 10){
            checksum += 1 + (((card_number % 10) * 2) % 10);
        } else {
            checksum += ((card_number % 10) * 2);
        }
        // remove last digit from card_number and increment card_number_length as long as
        // card_number is not now zero
        if(card_number != 0){card_number_length += 1;}
        card_number = card_number / 10;
    }

    //shorten entered card number to only the first two digits
    long long first_digits = entered_card_number;
    for(int i = card_number_length; i > 2; i--){
        first_digits /= 10;
    }
    
    // determine card number validity
    if(checksum % 10 == 0){
        switch(card_number_length){
            case 15:
                if(first_digits == 34 || first_digits == 37){
                    printf("AMEX\n");
                }
                break;
            case 16:
                if(first_digits == 51 || first_digits == 52 || first_digits == 53 || first_digits == 54 || first_digits == 55){
                    printf("MASTERCARD\n");
                }
            case 13:
                if(first_digits / 10 == 4){
                    printf("VISA\n");
                }
                break;
            default:
                printf("INVALID\n");
                break;
        }
    } else {
        printf("INVALID\n");
    }
}