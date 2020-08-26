import hashlib
import sys
import whirlpool

def usage():
    print("""

        First parameter <wordlist> second parameter <hash algorithm>
        Example: python3 checksums.py passwords.txt md5

        Checksum is calculated for each line in file and saved into an output file.

        Hash algorithms to use: md5, sha256, sha512, blake2b512 and whirlpool
        """)
    sys.exit()

def whirlpoolsum(wordlist, filepath):
    results = open(filepath, "w+")
    try:
        with open(wordlist) as words:
            for line in words:
                line = line.strip()
                results.write(f'{whirlpool.new(line.encode()).hexdigest()} {line}\n')
                #print(f'{whirlpool.new(line.encode()).hexdigest()} {line}')
    finally:
        results.close()
        sys.exit()

def blake2b512sum(wordlist, filepath):
    results = open(filepath, "w+")
    try:
        with open(wordlist) as words:
            for line in words:
                line = line.strip()
                results.write(f'{hashlib.blake2b(line.encode(), digest_size=64).hexdigest()} {line}\n')
                #print(f'{hashlib.blake2b(line.encode(), digest_size=64).hexdigest()} {line}\n')
    finally:
        results.close()
        sys.exit()

def calculateChecksum(wordlist, algorithm):
    if algorithm == "md5":
        filepath = "hashes/md5/md5-results.txt"
        function = hashlib.md5
    elif algorithm == "sha256":
        filepath = "hashes/sha256/sha256-results.txt"
        function = hashlib.sha256
    elif algorithm == "sha512":
        filepath = "hashes/sha512/sha512-results.txt"
        function = hashlib.sha512
    elif algorithm == "blake2b512":
        filepath = "hashes/blake2b512/blake2b512-results.txt"
        blake2b512sum(wordlist, filepath)
    elif algorithm == "whirlpool":
        filepath = "hashes/whirlpool/whirlpool-results.txt"
        whirlpoolsum(wordlist, filepath)
    else:
        usage()   
         
    results = open(filepath, "w+")
    try:
        with open(wordlist) as words:        
            for line in words:
                line = line.strip()
                results.write(f'{function(line.encode()).hexdigest()} {line}\n')
                #print(f'{function(line.encode()).hexdigest()} {line}')
    finally:
        results.close()

if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        usage()

    wordlist = sys.argv[1]
    algorithm = sys.argv[2]

    calculateChecksum(wordlist, algorithm)
