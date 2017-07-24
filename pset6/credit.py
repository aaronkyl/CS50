import cs50

print("Number: ", end = "")
entered_card_number = cs50.get_float()
card_number = entered_card_number

checksum = 0
card_number_length = 0

while card_number > 0:
    checksum += card_number % 10
    card_number //= 10
    card_number_length += 1
    
    if ((card_number % 10) * 2) >= 10:
        checksum += 1 + (((card_number % 10) * 2) % 10)
    else:
        checksum += ((card_number % 10) * 2)
    
    if card_number != 0:
        card_number_length += 1
    
    card_number //= 10
    
first_digits = entered_card_number

for counter in range(card_number_length, 2, -1):
    first_digits //= 10
    
if checksum % 10 == 0:
    if card_number_length == 15:
        if first_digits == 34 or first_digits == 37:
            print("AMEX")
    elif card_number_length == 13 or card_number_length == 16:
        if first_digits // 10 == 4:
            print("VISA")
        elif 51 <= first_digits <= 55:
            print("MASTERCARD")
    else:
        print("INVALID")
else:
    print("INVALID")
