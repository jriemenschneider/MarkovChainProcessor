import re
import random
import string
import pickle

class Generator:
    #The only initialization field is at what character to make splits, default that is " " (a space)
    def __init__(self, SKIPCHAR):
        self.SKIPCHAR = SKIPCHAR
    #Saves an object (dictionary) to an obj file in the root folder
    def save_obj(self, obj, name):
        with open('obj/'+ name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    #Loads pickle dictionary from root/obj
    def load_obj(self, name):
        with open('obj/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)

    #Not needed when using pickle files. Used to load a corpus in plain-text and format it
    def processWords(self):
        with open('corpusTwitter.txt',encoding="latin-1") as file:
            WORDS = file.read().replace('\n', '')
            WORDS = ''.join([i for i in WORDS if not i.isdigit()])
            WORDS = WORDS.lower()
            WORDS = re.sub(' +', ' ', WORDS)
            WORDS = ' '.join(WORDS.split())
            WORDS = re.sub('@[^\s]+','',WORDS)
            print("Finished pre-processing")
        return WORDS


    #This function takes a string input, makes it into a list, then outputs an dictionary where the key is the word (or word
    #pairs) and the value is how many times it appears. numSkips is essentially the order of the operation and skipPlace is
    #character (defaulty " ")
    def listToDict(self, inWords, numSkips):
        tempDict = dict()
        corpus = self.splitter(inWords, numSkips)

        for x in range (len(corpus)):
            if(corpus[x] in tempDict):
                tempDict[corpus[x]] += 1
            else:
                tempDict[corpus[x]] = 1

        return tempDict

    #This function gets the total number of occurances in a dictionary using listToDict format
    def getTotal(self, dictionary):
        tempTotal = 0
        for x in dictionary:
            tempTotal += dictionary[x]

        return tempTotal

    #Builds a probability dictionary of the same type as topWordPair using probabilistic value
    def buildProb(self, topWordPair, bottomWordPair, bottomWordNum):
        tempProbDict = dict()

        for q in topWordPair:
                tempList = q.split()
                if(len(tempList) != 1):
                    tempString = ""
                    for z in range(0, bottomWordNum):
                        tempString += tempList[z] + " "


                    tempProbDict[q] = topWordPair[q] / bottomWordPair[tempString]
        return tempProbDict

    #Uses the seq as it' starting pair, this chooses the next most likely words to come after this based off of the orderProb
    def chooseWord(self, seq, probList, pairList, order):
        r = random.random()
        found = 0
        tempString = ""

        orderProb = probList[order-2]

        for x in range(0, order-1):
            tempString += seq[len(seq)-(order-1)+x]

        for a in pairList[0]:

            if(tempString + a) in orderProb:
                if(r > found and r < (found + orderProb[tempString + a])):
                    #print("CHOOSING: " + str(a) + "AT ORDER " + str(order))
                    return(a)
                found += orderProb[tempString + a]

        if(order >= 2):
            return(self.chooseWord(seq, probList, pairList, order-1))
        else:
            randReturn = random.choice(list(pairList[0]))
            #print("RANDOM: " + randReturn)
            return(randReturn)

    #A unique splitter than takes a string input, the seperation character, and how many positions to skip
    def splitter(self, strng, pos):
        strng = re.findall(r"[\w']+|[.,!?;]", strng)
        output = []

        for x in range(0, len(strng)):
            tempString = ""
            lenTotal = 0

            for z in range(0, pos):
                if(x+z < len(strng)):
                    tempString += strng[x+z] + " "
                    lenTotal +=1

            if (lenTotal == pos):
                output.append(tempString)

        return output

    #The full buildsequence that inputs the word and outputs a list of values
    def fullBuild(self, order, WORDS, length):
        oneWordPair = self.listToDict(WORDS, self.SKIPCHAR, 1)
        lowerOrderPair = self.listToDict(WORDS, self.SKIPCHAR, order-1)
        upperOrderPair = self.listToDict(WORDS, self.SKIPCHAR, order)

        orderProb = self.buildProb(upperOrderPair, lowerOrderPair, order-1)

        tempStart =  random.choice(list(lowerOrderPair))

        seq = self.splitter(tempStart,  1)
        seq.pop()



        for x in range(0, length):
            holder = self.chooseWord(seq, orderProb, oneWordPair, order)
            seq.append(holder)

        return(seq)

    #This function builds the sequence necessary. Needs to be past a list of pairs and probabilities
    def buildSequence(self, order, pairList, probList, tempStart, length):
        sequence = ""

        if(order == 0):
            for z in range(0, length):
                sequence += random.choice(list(pairList[0]))

        elif(order == 1):
            oneWordPair = pairList[0]

            for z in range(0, length):
                r = random.randint(0, self.getTotal(oneWordPair)-1)
                found = 0
                for q in oneWordPair:
                    if(r >= found and r < found + oneWordPair[q]):
                        sequence += q
                        break
                    found += oneWordPair[q]

        elif(order >= 2):
            outList = self.splitter(tempStart, 1)

            index = 0
            unfinished = True

            while(unfinished):
                holder = self.chooseWord(outList, probList, pairList, order)
                outList.append(holder)
                index += 1

                if((index >= length and holder == ". ") or index >= (2*index)):
                    unfinished = False
                    print("Index: " + str(index))
                elif(index >+ (2*length)):
                    unfinished = False
                    print("Index: " + str(index))

            for x in range(0 , len(outList)):
                sequence += outList[x]

        else:
            raise Exception('order should not be below exceed 0. The value of order was: {}'.format(order))


        sequence = re.sub(r'\s([?.;,!"](?:\s|$))', r'\1', sequence)
        return(sequence)

machine = Generator(" ")

oneWordPair = machine.load_obj("oneWordPairTwitter")
twoWordPair = machine.load_obj("twoWordPairTwitter")
threeWordPair = machine.load_obj("threeWordPairTwitter")
fourWordPair = machine.load_obj("fourWordPairTwitter")

twoWordProb = machine.load_obj("twoWordProbTwitter")
threeWordProb = machine.load_obj("threeWordProbTwitter")
fourWordProb = machine.load_obj("fourWordProbTwitter")


pairList = [oneWordPair, twoWordPair, threeWordPair, fourWordPair]
probList = [twoWordProb, threeWordProb, fourWordProb]



def Generate():

    print("What order would you like to generate at? (0-4)")
    order = input()
    order = int(order)

    print("What should the minimum length of the sentence be?")
    length = input()
    length = int(length)

    choice = "N"
    if(order >= 2):
        print("Would you like to choose the start? Y/N")
        choice = input()

    if(choice == "Y" and order > 1):
        print("Choose a sentence " + str(order-1) + " words long:")
        start = input()
    else:
        start = random.choice(list(pairList[order-2]))
        print("Your start word is: " + start)

    while True:
        output = machine.buildSequence(order, pairList, probList, start, length)

        print(str(order) + " ORDER SENTENCE OF length " + str(length))
        print("")
        print(output)
        print("")

        res = 0

        print("Would you like to generate another using these setting? Y/N")
        res = input()

        if(res == 'N'):
            break

while True:
    start = ""
    Generate()
    print("Would you like to generate again? Y/N")
    start = input()

    if(start == 'N'):
        break
