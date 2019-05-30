import re
import random
import string
import pickle
from audiolazy import str2midi
from midiutil import MIDIFile

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
        with open('corpusMusic.txt', 'r+') as file:
            output = file.read()
            output = output.replace(" ", "")
            output = output.replace("'", "")
            output = output.replace("[", "")
            output = output.replace("]", "")
            output = output.replace(",", " ")
            output = output.replace("#", "s")
            output = re.sub(' +', ' ', output)
            output = ' '.join(output.split())
            print("Finished pre-processing")
        return output


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

            for x in range (0, length):
                holder = self.chooseWord(outList, probList, pairList, order)
                outList.append(holder)

            for x in range(0 , len(outList)):
                sequence += outList[x]

        else:
            raise Exception('order should not be below exceed 0. The value of order was: {}'.format(order))


        sequence = re.sub(r'\s([?.;,!"](?:\s|$))', r'\1', sequence)
        return(sequence)

machine = Generator(" ")


#Loading all the note pairs and probabilities
oneWordPair = machine.load_obj("oneWordPairMusic")
twoWordPair = machine.load_obj("twoWordPairMusic")
threeWordPair = machine.load_obj("threeWordPairMusic")
fourWordPair = machine.load_obj("fourWordPairMusic")
fiveWordPair = machine.load_obj("fiveWordPairMusic")
sixWordPair = machine.load_obj("sixWordPairMusic")

twoWordProb = machine.load_obj("twoWordProbMusic")
threeWordProb = machine.load_obj("threeWordProbMusic")
fourWordProb = machine.load_obj("fourWordProbMusic")
fiveWordProb = machine.load_obj("fiveWordProbMusic")
sixWordProb = machine.load_obj("sixWordProbMusic")

pairList = [oneWordPair, twoWordPair, threeWordPair, fourWordPair, fiveWordPair, sixWordPair]
probList = [twoWordProb, threeWordProb, fourWordProb, fiveWordProb, sixWordProb]

def Generate():

    print("What order would you like to generate at? (0-6)")
    order = input()
    order = int(order)

    print("How many notes would you like to generate?")
    length = input()
    length = int(length)


    choice = "N"
    if(order >= 2):
        print("Would you like to choose the start? Y/N")
        choice = input()

    if(choice == "Y" and order > 1):
        print("Choose a note sequence " + str(order-1) + " notes long:")
        start = input()
    else:
        start = random.choice(list(pairList[order-2]))

    output = machine.buildSequence(order, pairList, probList, start, length)

    print("")
        #Bring back in the sharp notes (They were removed during pre-processing due to errors with RE)
    output = output.replace("s", "#")
    output = output.split(" ")
    output.pop()

        #Convert notes into MIDI degrees
    print(output)
    for x in range(0, len(output)):
        output[x] = str2midi(output[x])

    res = 0


    return output

while True:
    start = ""
    output = Generate()
    print("Would you like to generate again? ('N' to write to file) Y/N")
    start = input()

    if(start == 'N'):
        break

print("What tempo would you like to play at?")
tempo = input()
tempo = int(tempo)

degrees  = output# MIDI note number

#This forms the MIDI object which we will pass to the file
track    = 0
channel  = 0
time     = 0    # In beats
duration = 1    # In beats
volume   = 100  # 0-127, as per the MIDI standard

MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                      # automatically)
MyMIDI.addTempo(track, time, tempo)

for i, pitch in enumerate(degrees):
    MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

#Writing to a midi file (or creating a new one)
print("WRITE TO FILE!")
with open("output.mid", "wb") as output_file:
    MyMIDI.writeFile(output_file)
