import sys

def usage():
    sys.exit()

def getHashLength(wordlist):

    try:
        filetoread = open(wordlist, "r")
        length = len(filetoread.readline().split()[0])
    except:
        print("Error occurred when counting hash length!")
        sys.exit()
    finally:
        filetoread.close()
    return length

def analyzeHashes(wordlist):

    hashlength = getHashLength(wordlist)
    #lists = [[[] for i in range(256)] for x in range(int(hashlength/2) + 1)]
    lists = [[0 for i in range(256)] for x in range(int(hashlength/2) + 1)]

    with open(wordlist) as hashes:
        for count, line in enumerate(hashes):
            bytenumber = 1
            #print(line)
            for value in range(0, hashlength, 2):
                lists[bytenumber][int(line[value:value+2], 16)] += 1
                #lists[bytenumber][int(line[value:value+2], 16)].append(line.split()[1])
                #print(str(int(line[value:value+2], 16)) + " " + str(line[value:value+2]).upper())
                bytenumber += 1
    print(lists)
    print("List is ready")
    return lists

def countresults(results):
    hashlength = len(results)
    csvfile = open("calculations.txt", "w+")
    csvfile.write('""')
    
    for x in range(1, hashlength):
        csvfile.write("," + str(x))

    for bit in range(0, 256):
        csvfile.write("\n")
        csvfile.write(str(bit))
        for byte in range(1, hashlength):
            #csvfile.write("," + str(len(results[byte][bit])))
            csvfile.write("," + str(results[byte][bit]))
    csvfile.close()
            
if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        usage()
    wordlist = sys.argv[1]
    results = analyzeHashes(wordlist)
    countresults(results)
