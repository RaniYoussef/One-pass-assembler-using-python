# Open the "program.txt" file and read its content, splitting lines into lists of words
with open("program.txt") as program:
    program = [line.split() for line in program]


# Open the "instruction.txt" file and read its content, splitting lines into lists of words
with open("instruction.txt") as instructions:

    instructionArray = [line.split() for line in instructions]
# Open/create "FullProgram.txt" file for writing
fileFullProgram = open("FullProgram.txt", "w")
fileFullProgram.close()

# Open/create "Symbol.txt" file for writing
fileSymbolTable = open("Symbol.txt", "w")
fileSymbolTable.close()

# Open/create "HTErec.txt" file for writing
HTE = open("HTErec.txt", "w")
HTE.close()

# Initialize global variables
SymbolTableArray = []
UsedArray = []
EndRecordAddress = ""
EndRecordAddressFlag = 0

# Define a function to get the object code for a given program line and location (LOC)
def GetObjectCode(ProgramLine, LOC):
    global SymbolTableArray
    global EndRecordAddress
    global EndRecordAddressFlag
    ObjectCode = "******"
    OppCode = "**"
    Format = "0"
    Address = "0000"

    # Iterate through instructionArray to find opcode and format for the given program line
    for instruction in instructionArray:
        if ProgramLine[0] == instruction[0]:
            OppCode = instruction[-1]
            Format = instruction[1]
        elif len(ProgramLine) > 1:
            if ProgramLine[1] == instruction[0]:
                OppCode = instruction[-1]
                Format = instruction[1]

    # Set end record address if the format is not "0" and the end record flag is not set
    if Format != "0" and EndRecordAddressFlag == 0:
        EndRecordAddress = hex(LOC).replace("0x", "").upper()
        EndRecordAddressFlag = 1

    # Generate object code based on instruction format
    if Format == "1":
        ObjectCode = OppCode
    if Format == "34":


        # Handle various cases for format "34"
        if len(ProgramLine) > 1:
            if ProgramLine[-1][0] == '#':
                ObjectCode = str("%02x" % (int(OppCode, 16) + 1)).replace("0x", "").upper()
            else:
                ObjectCode = str("%02x" % (int(OppCode, 16))).replace("0x", "").upper()
            Flagx = 0
            FlagUsed = 0


            for j in range(len(SymbolTableArray)):
                if ProgramLine[-1][-1].upper() == 'X' and ProgramLine[-1][-2].upper() == ',':
                    if ProgramLine[-1].split(',')[0].split('#')[-1].upper() == SymbolTableArray[j][1]:
                        Address = SymbolTableArray[j][0]
                        Flagx = 1
                        FlagUsed = 1
                else:
                    if ProgramLine[-1].split('#')[-1].upper() == SymbolTableArray[j][1]:
                        Address = SymbolTableArray[j][0]
                        FlagUsed = 1



            if Address == '0000' and ProgramLine[-1][0] == '#':
                FlagUsed = 1
                ObjectCode = ObjectCode + str("%04x" % int(ProgramLine[-1].split('#')[-1])).upper()
            elif Flagx == 1:
                ObjectCode = ObjectCode + str("%04x" % (int(str(Address), 16) + int('8000', 16))).replace("0x", "").upper()
            else:
                ObjectCode = ObjectCode + str("%04x" % int(str(Address), 16)).replace("0x", "").upper()

            if FlagUsed == 0:
                UsedArray.append([hex(LOC).replace("0x", "").upper(), ProgramLine[-1]])

        else:
            ObjectCode = OppCode + str("%04x" % int(str(Address), 16)).replace("0x", "").upper()


    if Format == "0":
        if len(ProgramLine) > 1:
            if ProgramLine[-2].upper() == 'BYTE' or ProgramLine[-2].upper() == 'WORD':
                if ProgramLine[-1][0].upper() == 'C':
                    tem = ProgramLine[-1].split('\'')
                    ObjectCode = ("".join(["{:02x}".format(ord(c)) for c in tem[1]])).upper()
                elif ProgramLine[-1][0].upper() == 'X':
                    tem = ProgramLine[-1].split('\'')
                    ObjectCode = tem[1].upper()
                else:
                    tem = ProgramLine[-1]
                    ObjectCode = hex(int(tem)).replace("0x", "").upper()
                    if ProgramLine[-2].upper() == 'WORD':
                        ObjectCode = str("%06x" % (int(tem, 16))).replace("0x", "").upper()

    return ObjectCode

# Define a function to add a symbol to the symbol table
def AddToSymbolTable(ProgramLine, LOC):
    global SymbolTableArray
    FlagSymbol = 0
    for instruction in instructionArray:
        if ProgramLine[0] == instruction[0]:
            FlagSymbol = 1
    if FlagSymbol == 0:
        SymbolTableArray.append([hex(LOC).replace("0x", "").upper(), ProgramLine[0]])


# Define a function to handle LOC calculation for RESW and RESB
def ReswResbHandel(ProgramLine, LOC):
    if ProgramLine[1].upper() == 'RESB':
        if ProgramLine[2][0].upper() == 'X':
            LOC = LOC + int(str(ProgramLine[2]).split('\'')[1], 16)
        else:
            LOC = LOC + int(ProgramLine[2])
    elif ProgramLine[1].upper() == 'RESW':
        if ProgramLine[2][0].upper() == 'X':
            LOC = LOC + int(str(ProgramLine[2]).split('\'')[1], 16) * 3
        else:
            LOC = LOC + int(ProgramLine[2]) * 3
    return LOC

# Define a function to handle LOC calculation for RESW and RESB
def UseAVariable(ProgramLine):
    Mask = False
    Format = "0"
    for instruction in instructionArray:
        if ProgramLine[0] == instruction[0]:
            Format = instruction[1]
        elif len(ProgramLine) > 1:
            if ProgramLine[1] == instruction[0]:
                Format = instruction[1]
    if Format == "34":
        if len(ProgramLine) > 1:
            Mask = True

    return Mask

# Define the main function
def main():
    global SymbolTableArray
    global UsedArray

    # Get the first address from the program
    FirstAddress = program[0][2]
    LOC = int(FirstAddress, 16)
    FullProgram = []

    # Initialize FullProgram with the first program line
    line = [FirstAddress] + program[0]
    print(line)
    FullProgram.append(line)
    Trecords = []


     # Iterate through the program lines
    for i in range(1, len(program)-1):
        line = []

        # Generate LOC, add the program line to FullProgram, and add the symbol to the symbol table
        line.append(hex(LOC).replace("0x", "").upper())
        line = line + program[i]
        AddToSymbolTable(program[i], LOC)

        # Get the object code, update LOC, and add object code, mask, and line to FullProgram
        ObjectCode = GetObjectCode(program[i], LOC)


        if UseAVariable(program[i]):
            Mask = "1"
        else:
            Mask = "0"
        if ObjectCode != "******":
            LOC += int(len(ObjectCode)/2)
        else:
            LOC = ReswResbHandel(program[i], LOC)
        line.append(ObjectCode)
        line.append(Mask)

        FullProgram.append(line)


    # Add the END record to FullProgram
    line = ["END", FirstAddress]
    FullProgram.append(line)

    # Write symbol table and FullProgram to corresponding files
    for data in SymbolTableArray:
        fileSymbolTable = open("Symbol.txt", "a")
        fileSymbolTable.write(data[0] + "\t" + data[1] + "\n")
        fileSymbolTable.close()

    for data in FullProgram:
        fileFullProgram = open("FullProgram.txt", "a")
        fileFullProgram.write(str(data) + "\n")
        fileFullProgram.close()


    # Process T records and write to HTErec.txt
    ObjectCodes = ""
    MaskingBits = ""
    
    g = 0
    TrecordsUse = []
    for i in range(1, len(FullProgram)):

        if FullProgram[i][0].find('END') != -1:
            break
        FlagINUsedArray = 0

        # if FullProgram[-2] != "******":
        for use in UsedArray:
            if FullProgram[i][1] == use[1]:
                Change = hex(int(use[0], 16)+1).replace("0x", "").upper()
                TrecUse = "T " + "0"*(6-len(Change))+Change + " 02 000 " + FullProgram[i][0]
                TrecordsUse.append(TrecUse)


        flagddd = 0

        for rec in TrecordsUse:
            if int(FullProgram[i][0], 16) == int(rec.split(' ')[-1], 16):
                flagddd = 1


# lenght is ok and not RSW or RSB

        if len(ObjectCodes + FullProgram[i][-2].replace("*", "")) <= 60 and FullProgram[i][-2] != "******" and flagddd == 0 and FullProgram[i+1][0].find('END') == -1:
                if FullProgram[i][-2].replace("*", "") != "":
                    ObjectCodes = ObjectCodes + " " + FullProgram[i][-2].replace("*", "")
                    MaskingBits = FullProgram[i][-1] + MaskingBits


        else:

            # RSW or RSB or next
            if FullProgram[i+1][-2] == "******":
                for rec in TrecordsUse:
                    if int(FullProgram[i][0], 16) == int(rec.split(' ')[-1], 16):
                        Trecords.append(rec)

                #object code is not empty
                if FullProgram[i][-2].replace("*", "") != "":
                    ObjectCodes = ObjectCodes + " " + FullProgram[i][-2].replace("*", "")


            # full object code is not empty
            if ObjectCodes != "":
                if FullProgram[i + 1][0].find('END') != -1:
                    if FullProgram[-2][-2].replace("*", "") != "":
                        ObjectCodes = ObjectCodes + " " + FullProgram[-2][-2].replace("*", "")
                        MaskingBits = FullProgram[i-1][-1] + MaskingBits
                        MaskingBits = MaskingBits + FullProgram[-2][-1]


                MaskingBits = MaskingBits + '0' * (12 - len(MaskingBits))
                RelocateBitsHex = ("%03x" % (int(MaskingBits, 2))).replace("0x", "").upper()
                addersss = str("%06x" % (int(FullProgram[g][0], 16))).replace("0x", "").upper()
                Trec = "T " + addersss + " " + str("%02x" % int(len(ObjectCodes.replace(" ", "")) / 2)).replace("0x", "").upper() + " " + RelocateBitsHex + " " + ObjectCodes
                Trecords.append(Trec)
                MaskingBits = ""
                for rec in TrecordsUse:
                    if int(FullProgram[i][0], 16) == int(rec.split(' ')[-1], 16):
                        Trecords.append(rec)


            # full object code or object code are not empty
            if len(ObjectCodes + '{0: <6}'.format(FullProgram[i][-2]).replace("*", "")):
                g = i
                ObjectCodes = '{0: <6}'.format(FullProgram[i][-2]).replace("*", "").replace(" ", "")


            # full object code and the object code exeed the 60 or  rsw or rsb or next End
            if len(ObjectCodes + '{0: <6}'.format(FullProgram[i][-2]).replace("*", "")) > 60 or FullProgram[i+1][-2] == "******":
                ObjectCodes = ''
                g = i + 2

    # Write H, T, and E records to the HTErec.txt file
    length = hex(int(FullProgram[-2][0], 16)+ int(len(FullProgram[-2][-2])/2) - int(FirstAddress, 16)).replace("0x", "").upper()
    Hrec ="H " + FullProgram[0][1] + " " * (6 - len(FullProgram[0][1])) + " " + "0" * (6 - len(FullProgram[0][0])) + FullProgram[0][0] + " " + "0" * (6 - len(length)) + length

    HTErecord = open("HTErec.txt", "a")
    HTErecord.write(Hrec+ "\n")
    HTErecord.close()
    for Trec in Trecords:
        HTErecord = open("HTErec.txt", "a")
        HTErecord.write(Trec + "\n")
        HTErecord.close()

    Erec = "E " + "0" * (6 - len(FullProgram[0][0])) + EndRecordAddress
    HTErecord = open("HTErec.txt", "a")
    HTErecord.write(Erec + "\n")
    HTErecord.close()



# Call the main function
main()