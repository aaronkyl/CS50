import cs50
import sys

def main():
    if len(sys.argv) != 2:
        print("Must provide one keyword!")
        exit(1)

    if not sys.argv[1].isalpha():
        print("Key must only contain alphabetic characters!")
        exit(2)
    
    print("plaintext: ", end="")
    plaintext = cs50.get_string()
    
    vigenere_cipher(plaintext, sys.argv[1])
    print()
    exit(0)

def vigenere_cipher(pt, key):
    counter = 0
    print("ciphertext: ", end="")
    for char in range(len(pt)):
        ptchar = pt[char]
        if ptchar.isalpha():
            if ptchar.isupper():
                a = ord('A')
            else:
                a = ord('a')
                
            if key[counter % len(key)].isupper():
                key_char = ord(key[counter % len(key)]) - ord('A')
            else:
                key_char = ord(key[counter % len(key)]) - ord('a')
            
            print(chr((((ord(ptchar) - a) + key_char) % 26) + a), end="")
            counter += 1
            continue
        print(ptchar, end="")

if __name__ == "__main__":
    main()