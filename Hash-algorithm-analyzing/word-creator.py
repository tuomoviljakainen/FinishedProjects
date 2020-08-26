import random
import string
import sys

def usage():
    print("""
        python3 word-creator.py <Character space> <word length> <amount>

        Character space defines what characters the word may include. There are predefined options:
        - all: numbers, punctuation characters, whitespace, small and big letters.
        - nowhitespace: numbers, punctuation characters, small and big ascii letters.
        - digits: numbers
        - lowercase: Lowercase ascii characters
        - uppercase: Uppercase ascii characters

        Word length specifies the exact length of each word.

        Amount specifies the amount of words to be created.
        """)
    sys.exit()

def createWords(wordlen, amount, letters):

    if letters == "all":
        filename = "all-characters"
        characterSpace = string.printable
    elif letters == "nowhitespace":
        filename = "all-characters-no-whitescape"
        characterspace = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    elif letters == "digits":
        filename = "digit-characters"
        characterspace = string.digits
    elif letters == "lowercase":
        filename = "lowercase-characters"
        characterspace = string.ascii_lowercase
    elif letters == "uppercase":
        filename = "uppercase-characters"
        characterspace = string.ascii_uppercase
    else:
        usage()   
    
    uniqueWords = set()
    wordlist = open("words/" + filename + "-" + str(wordlen) + ".txt", "w+")
    try: 
        for x in range(0, amount):
            value = ''.join(random.choice(characterspace) for i in range(wordlen))
            if value not in uniqueWords:
                uniqueWords.add(value)
                wordlist.write(value + "\n")
            else:
                x -= 1
    except:
        print("error")
    finally:
        wordlist.close()
    
if __name__ == "__main__":

    if len(sys.argv) != 4:
        usage()
    
    letterSpace = sys.argv[1]
    wordlength = int(sys.argv[2])
    amount = int(sys.argv[3])

    createWords(wordlength, amount, letterSpace)
