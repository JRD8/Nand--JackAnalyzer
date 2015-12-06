################################
####### JRD JACK ANALYZER ######
################################


## JACK TOKENIZER MODULE ##

# Global variable declarations
currentPos = 0
currentToken = ""
currentTokenType = ""

currentClass = ""
classToCall = ""
currentSubroutineName = ""
currentLabelIndex = 0
nArgsToCall = 0
nParsForFunction = 0

outFile = "" # Main Parser File **.xml
outFile2 = "" # Tokenizer Ref File **T.xml
outFile3 = "" # VM Code Writer File **.vm

tokenizedSource = []
tabLevel = 0

classScopeSymbolTable = {}
subroutineScopeSymbolTable = {}

currentFieldIndex = 0
currentStaticIndex = 0
currentVarIndex = 0
currentArgIndex = 0

symbols = ['}', '{', ')', '(', ']', '[', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
stringConstant = "\""


def main():
    
    # Import Jack file(s) form command line script
    from sys import argv
    print "JRD Nand-2-Tetris Jack Analyzer, 2015\n"
    print "Enter the Source Jack File (.jack) or Source Jack Directory (within this path) to be analyzed:"
    
    # Input options?
    #userInput = raw_input(">") # Prompt for user input...
    userInput = "average" # Test without user input
    
    print "\nThis is the Initial Source Input: " + userInput
    
    if userInput.find(".jack") == -1: # Directory input
        inputType = "directory"
        print "(Source is a Directory Input)\n"
        import os
        scriptPath = os.path.dirname(os.path.abspath(__file__))
        sourcePath = scriptPath + "/" + userInput + "/"
        print "Source Path = " + sourcePath + "\n"
        
        sourceDirectoryList = os.listdir(sourcePath)
    
        for sourceFile in sourceDirectoryList:
            if sourceFile.find(".jack") != -1: # Found a .jack file
                
                outFilename = sourcePath + sourceFile[0:sourceFile.find(".")] + ".xml" # Creates **.xml for main parser file
                outFilename2 = sourcePath + sourceFile[0:sourceFile.find(".")] + "T.xml" # Creates **T.xml for tokenizer ref file
                outFilename3 = sourcePath + sourceFile[0:sourceFile.find(".")] + ".vm" # Creates **.vm for code writer file
                
                sourceFile = sourcePath + sourceFile
                
                print "Processing Source File: " + sourceFile + "\n"
            
                jackTokenizerConstructor(sourceFile, outFilename, outFilename2, outFilename3)


    elif userInput.find(".jack") != -1: # File input
        inputType = "file"
        print "(Source Input is a FILE)\n"

        sourceFile = userInput

        print "This is the Current Source File: " + sourceFile

        outFilename = sourceFile[0:sourceFile.find(".")] + ".xml" # Creates **.xml for main parser file
        outFilename2 = sourceFile[0:sourceFile.find(".")] + "T.xml" # Creates **T.xml for tokenizer ref file
        outFilename3 = sourceFile[0:sourceFile.find(".")] + ".vm" # Creates **.vm for code writer file
        
        jackTokenizerConstructor(sourceFile, outFilename, outFilename2, outFilename3)

    else:
        print "E1"
        error()

    print "\n----------------------------\n** JACK ANALYZER Complete **"

    return


def jackTokenizerConstructor(sourceFile, outFilename, outFilename2, outFilename3):
    
    global outFile, outFile2, outFile3

    # Open the outFile(s)
    outFile = open(outFilename, 'w') # Opens the main parser file
    outFile2 = open(outFilename2, 'w') # Opens the tokenizer ref file
    print "Writing the Destination Parser File (*.xml): " + outFilename + "\nWriting Tokenizer Ref File (*T.xml): " + outFilename2
    
    # Contruct the VM Code Writer
    vmwriterConstructor(outFilename3)

    # Get date/time stamp
    from time import localtime, strftime
    temp = strftime("%a, %d, %b, %Y, %X", localtime())

    # Write headers into outFile(s)
    outFile.write("<!-- \nJACK ANALYZED\nSOURCE CODE FROM: " + sourceFile + "\nON: " + temp + "\n-->\n\n")
    outFile2.write("<!-- \nJACK ANALYZED\nSOURCE CODE FROM: " + sourceFile + "\nON: " + temp + "\n-->\n\n") # tokenizer ref file
    outFile3.write("// JACK ANALYZED\n// SOURCE CODE FROM: " + sourceFile + "\n// ON: " + temp + "\n\n") # VM code writer file
    
    # Process main Parser file
    processFile(sourceFile)
    
    # Close tokenizer ref file
    outFile2.write("</tokens>\n") # Write footer
    outFile2.write("\n<!-- \nEND OF FILE\n-->\n\n")
    outFile2.close()
    
    # Close VM code writer file
    vmwriterClose()

    # Close main parser File
    outFile.write("\n<!-- \nEND OF FILE\n-->\n\n")
    outFile.write("<!-- \nCLASS SCOPE SYMBOL TABLE: \n")
    outFile.write(str(classScopeSymbolTable))
    outFile.write("\n-->\n\n")
    outFile.close()
    
    print "-----------------------\nGenerating Class Scope Symbol Table:"
    print classScopeSymbolTable
    print "\n"
    print "Closing files:\n" + outFilename + "\n"+ outFilename2 + "\n" + outFilename3 + "\n-----------------------\n"
    
    return


def processFile(sourceFile):
    
    global tokenizedSource, currentPos, currentToken, currentTokenType
    
    # Reset key variables variables
    currentPos = 0
    currentToken = ""
    currentTokenType = ""
    tabLevel = 0
 
    tokenizedSource = tokenizeFile(sourceFile) # Tokenize the source file
    print "Tokenized Source Code: \n"
    print tokenizedSource
    print "\n--------------------------------------------\n"
    
    # Write tokenizer ref file header
    outFile2.write("<tokens>\n")
    
    # Log and write the tokenizer ref file
    while (hasMoreTokens()):
        currentToken = advance()
        currentTokenType = tokenType()
        print "\n\nCurrent Pos = " + str(currentPos - 1) + ", Current Token Type: " + currentTokenType + "\n"
        print "Current Token is: " + currentToken + "\n"

        if currentTokenType == "KEYWORD":
            temp = keyWord()
            print "Keyword: ",
            outFile2.write("\t<keyword> " + currentToken + " </keyword>\n") # tokenizer ref file
        
        if currentTokenType == "SYMBOL":
            temp = symbol()
            print "Symbol: ",
            
            # Handle the 3 exceptions for <,<,&
            if currentToken == "<":
                outFile2.write("\t<symbol> &lt; </symbol>\n")
            elif currentToken == ">":
                outFile2.write("\t<symbol> &gt; </symbol>\n")
            elif currentToken == "&":
                outFile2.write("\t<symbol> &amp; </symbol>\n")
            else:
                outFile2.write("\t<symbol> " + currentToken + " </symbol>\n")
                
                
        if currentTokenType == "IDENTIFIER":
            temp = identifier()
            print "Identifier: ",
            outFile2.write("\t<identifier> " + currentToken + " </identifier>\n") # tokenizer ref file
        
        if currentTokenType == "INT_CONST":
            temp = str(intVal())
            print "Integer Constant: ",
            outFile2.write("\t<integerConstant> " + currentToken + " </integerConstant>\n") # tokenizer ref file
        
        if currentTokenType == "STRING_CONST":
            temp = stringVal()
            print "String Constant: ",
            outFile2.write("\t<stringConstant> " + currentToken.strip("\"") + " </stringConstant>\n") # tokenizer ref file
        
        print temp + "\n"

    if not hasMoreTokens():
        currentPos = 0
        compilationEngineConstructor()

    return

def tokenizeFile(source_file):
    
    import re # Import the Regular Expresssion module for re.split method
    
    # First Pass: Read in source file
    firstStep = open(source_file, "r")
    firstPass = firstStep.read()
    print "----------------------------------------\n\nSource Code: \n"
    print firstPass

    # Second Pass: Replace all white spaces within a String with \x00 (control null) characters
    i = 0
    temp = list(firstPass)
    quoteOpen = 0
    while (i < len(temp)):
        if temp[i] == "\"":
            quoteOpen = ~quoteOpen
        if ((temp[i] == " ") & (quoteOpen)):
            temp[i] = "\x00"
        i = i + 1
    secondPass = "".join(temp)

    # Third Pass: Remove \n carriage returns
    thirdPass = secondPass.split("\n")
    
    # Fourth Pass: Remove // Comment lines
    fourthPass = []
    for e in thirdPass:
        if e.find("//") != -1:
            temp = e.lstrip(" \t")
            if temp.startswith("//", 0, 2) == False:
                fourthPass.append(e)
        else:
            fourthPass.append(e)
    print fourthPass
    # Routine to remove // comments inline after statement TODO PROBLEM HERE!!!!
    temp = []
    for e in fourthPass:
        if ((e.find("\r") != -1) & (e.find("//") == -1)):
            temp.append(e)
        else:
            i = e.find("//")
            if i != 1:
                temp.append(e[0:i])
            else:
                temp.append(e)
    fourthPass = temp
    print fourthPass


    # Fifth Pass: Remove \r and \t\r elements
    fifthPass = []
    for e in fourthPass:
        if ((e != "\r") & (e != "\t\r") & (e != "")):
            fifthPass.append(e)

    # Sixth Pass: Recombine into single string
    sixthPass = "".join(fifthPass)
    
    # Seventh Pass: Remove white spaces, tabs
    seventhPass = sixthPass.split()
    
    # Eighth Pass: Remove /** and /* ... */ comments
    eightPass = []
    include = True
    i = 0
    while (i < len(seventhPass)):
        if ((seventhPass[i] == "/**") | (seventhPass[i] == "/*")):
            include = False
        if include:
            eightPass.insert(i, seventhPass[i])
        if seventhPass[i] == "*/":
            include = True
        i = i + 1
    
    # Nineth Pass: Split out the string constants
    ninethPass = []
    for e in eightPass:
        temp2 = []
        if e.find("\"") == -1: # has no quotation marks...
            ninethPass.append(e)

        else: # has at least one quotation mark...
            temp = re.split('(\")', e)
            temp3 = ""
            quoteOpen = 0
            for f in temp:
                if f.find("\"") == -1: # No quotes...
                    if (quoteOpen):
                        temp3 = temp3 + f
                    if (~quoteOpen):
                        temp2.append(f)
                if f.find("\"") != -1:
                    if (quoteOpen): # Found closing quote
                        temp3 = temp3 + f
                        temp2.append(temp3)
                    if (~quoteOpen): # Found opening quote
                        temp3 = temp3 + f
                    quoteOpen = ~quoteOpen

        for g in temp2:
            ninethPass.append(g)

    # Tenth Pass: Split out the symbol elements
    tenthPass = []
    insertPass = []
    allSymbols = '([}{)(\][.,;+-/&|<>=~*])'
    for e in ninethPass:
        if e.find("\"") == -1: # Not a string constant
            temp = re.split(allSymbols, e)
            for f in temp:
                insertPass.append(f)
        else: # Is a string constant...
            insertPass.append(e)
    for e in insertPass: # cleanup the blank list elements
        if len(e) != 0:
            tenthPass.append(e)

    # Eleventh Pass: Replace \x00 (control null) characters with white spaces
    eleventhPass = []
    for e in tenthPass:
        eleventhPass.append(e.replace("\x00", " "))

    return eleventhPass


def hasMoreTokens():
    if (currentPos < len(tokenizedSource)):
        result = True
    else:
        result = False
    return result


def advance():
    global currentPos

    result = tokenizedSource[currentPos]
    currentPos = currentPos + 1

    return result


def tokenType():
    for keyword in keywords:
        if (currentToken == keyword):
            return "KEYWORD"
    for symbol in symbols:
        if (currentToken == symbol):
            return "SYMBOL"
    if currentToken.isdigit():
        return "INT_CONST"
        #if (currentToken.find("\"") != -1):
    if currentToken.startswith("\"") & currentToken.endswith("\""):
        return "STRING_CONST"
    return "IDENTIFIER"


def keyWord():
    return currentToken.upper()


def symbol():
    return currentToken


def identifier():
    return currentToken


def intVal():
    return int(currentToken)


def stringVal():
    return currentToken.strip("\"") # stringVal returns without quotation marks


## COMPILATION ENGINE MODULE ##


def compilationEngineConstructor():
    
    global currentPos, currentToken, currentTokenType
    
    currentPos = 0
    currentToken = ""
    currentTokenType = ""
    
    print "-----------------------\nWriting XML Code...\n"

    compileClass()
    
    return


def compileClass():
    
    global currentToken, currentTokenType, currentClass
    
    print "compileClass()\n"
    
    # Initialize class scope symbol table
    symbolTableConstructor()
    
    performBasicCheck()
    
    # Write class header
    if ((currentTokenType == "KEYWORD") & (currentToken == "class")):
        stringToExport = tabInsert() + "<class>\n"
        outFile.write(stringToExport)
    
        incrementTab()
        
        stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
        outFile.write(stringToExport)
        
        performBasicCheck()
            
        # Write className
        if currentTokenType == "IDENTIFIER":
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            outFile.write(tabInsert() + "<!-- Identifier: class, def, no index -->\n") # Chap 11, Stage 1 Comment
            
            currentClass = currentToken

            performBasicCheck()
            
            # Write {
            if ((currentTokenType == "SYMBOL") & (currentToken == "{")):
                stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                outFile.write(stringToExport)
                        
                # Begin Recursion...
                performBasicCheck()
                            
                # Loop to find either a classVarDec or a subroutineDec initial keyword
                while ((currentTokenType == "KEYWORD") & ((currentToken == "function") | (currentToken == "method") | (currentToken == "constructor") | (currentToken == "static") | (currentToken == "field"))):
                    
                    # Found a subroutineDec
                    if ((currentTokenType == "KEYWORD") & ((currentToken == "function") | (currentToken == "method") | (currentToken == "constructor"))):
                        compileSubroutine()
                    
                    # Found a ClassVarDec
                    elif ((currentTokenType == "KEYWORD") & ((currentToken == "static") | (currentToken == "field"))):
                        compileClassVarDec()

                    else:
                        print "E2"
                        error()
                        
                    performBasicCheck()
                
                # Write }
                if ((currentTokenType == "SYMBOL") & (currentToken == "}")):
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)

                else:
                    print "E3"
                    error()
            else:
                print "E4"
                error()
        else:
            print "E5"
            error()

        decrementTab()

        # Write class footer
        stringToExport = tabInsert() + "</class>\n"
        outFile.write(stringToExport)

    else:
        print "E6"
        error()

    return


def compileClassVarDec():

    print "compileClassVarDec()\n"
    
    # Write classVarDec header
    stringToExport = tabInsert() + "<classVarDec>\n"
    outFile.write(stringToExport)
    
    incrementTab()
    
    # Found a Static class variable
    if ((currentTokenType == "KEYWORD") & ((currentToken == "static"))):
        stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
        outFile.write(stringToExport)
        
        performBasicCheck()
        
        # Write primitive type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
            stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
            outFile.write(stringToExport)
        
            currentType = currentToken
        
        # Write object type
        elif ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            currentType = currentToken

            outFile.write(tabInsert() + "<!-- Identifier: class, def, no index -->\n") # Chap 11, Stage 1 Comment

        else:
            print "E7"
            error()
    
        performBasicCheck()
        
        # Write varName
        if ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            # Add STATIC variable to class scope symbol table
            define(currentToken, currentType, "STATIC")
            
            outFile.write(tabInsert() + "<!-- Identifier: static, def, " + str(indexOf(currentToken)) + " -->\n") # Chap 11, Stage 1 Comment

        else:
            print "E8"
            error()
        
        performBasicCheck()
    
        # Loop to write multiple varNames
        while ((currentTokenType == "SYMBOL") & (currentToken == ",")):
            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)
        
            performBasicCheck()
        
            # Write varName
            if ((currentTokenType == "IDENTIFIER")):
                stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
                outFile.write(stringToExport)
                
                # Add STATIC variable to class scope symbol table
                define(currentToken, currentType, "STATIC")
            
                outFile.write(tabInsert() + "<!-- Identifier: static, def, " + str(indexOf(currentToken)) + " -->\n") # Chap 11, Stage 1 Comment
            
            else:
                print "E9"
                error()
                    
            performBasicCheck()
        
        
    # Found a Field class variable
    elif ((currentTokenType == "KEYWORD") & ((currentToken == "field"))):
        stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
        outFile.write(stringToExport)
        
        performBasicCheck()
        
        # Write primitive type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
            stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
            outFile.write(stringToExport)
        
            currentType = currentToken

        # Write object type
        elif ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            currentType = currentToken
            
            outFile.write(tabInsert() + "<!-- Identifier: class, def, no index -->\n") # Chap 11, Stage 1 Comment
        
        else:
            print "E10"
            error()

        performBasicCheck()
        
        # Write varName
        if ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            # Add FIELD variable to class scope symbol table
            define(currentToken, currentType, "FIELD")
            
            outFile.write(tabInsert() + "<!-- Identifier: field, def, " + str(indexOf(currentToken)) + " -->\n") # Chap 11, Stage 1 Comment

        else:
            print "E11"
            error()
        
        performBasicCheck()
        
        # Loop to write multiple varNames
        while ((currentTokenType == "SYMBOL") & (currentToken == ",")):
            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)
            
            performBasicCheck()
            
            # Write varName
            if ((currentTokenType == "IDENTIFIER")):
                stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
                outFile.write(stringToExport)
                
                # Add FIELD variable to class scope symbol table
                define(currentToken, currentType, "FIELD")

                outFile.write(tabInsert() + "<!-- Identifier: field, def, " + str(indexOf(currentToken)) + " -->\n") # Chap 11, Stage 1 Comment

            else:
                print "E12"
                error()
            
            performBasicCheck()

        
    # Writing a ; statement close
    if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
        outFile.write(stringToExport)

    else:
        print "E13"
        error()

    decrementTab()

    # Write classVarDec footer
    stringToExport = tabInsert() + "</classVarDec>\n"
    outFile.write(stringToExport)

    return


def compileSubroutine():
    
    global currentSubroutineName, currentLabelIndex
    
    # CodeGen
    currentSubroutineName = ""
    currentLabelIndex = 1
    
    print "compileSubroutine()\n"
    
    # Write subroutineDec header
    stringToExport = tabInsert() + "<subroutineDec>\n"
    outFile.write(stringToExport)
    
    # Initialize a new subroutine scope symbol table
    startSubroutine()
    
    incrementTab()
    
    if ((currentTokenType == "KEYWORD") & ((currentToken == "function") | (currentToken == "method") | (currentToken == "constructor"))):
        stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
        outFile.write(stringToExport)
        
        subroutineType = currentToken
        
        # Additional routine to add "this" as ARG 0 for a method subroutine call
        if (subroutineType == "method"):
            
            i = 0
            while (i < len(tokenizedSource)):
                if (tokenizedSource[i] == "class"):
                    temp = tokenizedSource[i + 1]
                i = i + 1
            
            # Add ARG variable to class scope symbol table
            define ("this", temp, "ARG")
    
        performBasicCheck()
    
        # Write primitive return type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean") | (currentToken == "void"))):
            stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
            outFile.write(stringToExport)
        
            currentType = currentToken
                
        
        # Write object return type
        elif ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            currentType = currentToken
        
            outFile.write(tabInsert() + "<!-- Identifier: class, def, no index -->\n") # Chap 11, Stage 1 Comment

        else:
            print "E14"
            error()
                
        performBasicCheck()
            
        # Write subroutineName
        if ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
        
            outFile.write(tabInsert() + "<!-- Identifier: subroutine, def, no index -->\n") # Chap 11, Stage 1 Comment
        
            currentSubroutineName = currentToken
  
        else:
            print "E15"
            error()
                
        performBasicCheck()
            
        # Write (
        if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)

            performBasicCheck()

            compileParameterList()
            
            # Write )
            if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
                stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                outFile.write(stringToExport)
                
                # Write subroutineBody header
                stringToExport = tabInsert() + "<subroutineBody>\n"
                outFile.write(stringToExport)

                performBasicCheck()
            
                # Write {
                if ((currentTokenType == "SYMBOL") & (currentToken == "{")):
                    incrementTab()
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)
            
                    performBasicCheck()
                    
                    # Loop to find either a varDec or a Statement initial keyword
                    while (currentToken != "}"):
                        
                        while ((currentTokenType == "KEYWORD") & (currentToken == "var")):
                            compileVarDec()
                        
                        # CodeGen
                        writeFunction(currentClass + "." + currentSubroutineName, varCount("VAR"))
                        if (currentSubroutineName == "new"): # Additional code for a Constructor
                            writePush("CONST", varCount("FIELD"))
                            writeCall("Memory.alloc", 1)
                            writePop("POINTER", 0)
                        if (subroutineType == "method"): # Additional code for a method subroutine to push THIS value and restore it to POINTER 0
                            writePush("ARG", 0)
                            writePop("POINTER", 0)
                        
                        if ((currentTokenType == "KEYWORD") & ((currentToken == "let") | (currentToken == "if") | (currentToken == "while") | (currentToken == "do") | (currentToken == "return"))):
                            compileStatements()
                        else:
                            print "E16"
                            error()
                
                    # Write }
                    if ((currentTokenType == "SYMBOL") & (currentToken == "}")):
                        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                        outFile.write(stringToExport)
                    
                        # Write subroutineBody footer
                        decrementTab()
                        stringToExport = tabInsert() + "</subroutineBody>\n"
                        outFile.write(stringToExport)

                    else:
                        print "E17"
                        error()
                else:
                    print "E18"
                    error()
            else:
                print "E19"
                error()
        else:
            print "E20"
            error()
    else:
        print "E21"
        error()
    
    decrementTab()

    # Write subroutine scope symbol table
    outFile.write(tabInsert() + "<!-- SUBROUTINE SCOPE SYMBOL TABLE: ")
    outFile.write(str(subroutineScopeSymbolTable))
    outFile.write(" -->\n")


    # Write subroutineDec footer
    stringToExport = tabInsert() + "</subroutineDec>\n"
    outFile.write(stringToExport)

    return


def compileParameterList():
    
    global nParsForFunction
    
    print "compileParameterList()\n"
    
    nParsForFunction = 0

    # Write parameterList header
    stringToExport = tabInsert() + "<parameterList>\n"
    outFile.write(stringToExport)
    
    # Found an empty parameterList
    if ((currentTokenType == "SYMBOL") & (currentToken == ")")):

        # Write parameterList footer
        stringToExport = tabInsert() + "</parameterList>\n"
        outFile.write(stringToExport)

        return

    else:
        
        # Write primitive type parameter
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
            incrementTab()
            stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
            outFile.write(stringToExport)
        
            currentType = currentToken
    
        # Write object type parameter
        elif ((currentTokenType == "IDENTIFIER")):
            incrementTab()
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            currentType = currentToken

            outFile.write(tabInsert() + "<!-- Identifier: class, def, no index -->\n") # Chap 11, Stage 1 Comment

        else:
            print "E22"
            error()

        performBasicCheck()
            
        # Write parameter varName
        if ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            # Add ARG variable to class scope symbol table
            define(currentToken, currentType, "ARG")

            outFile.write(tabInsert() + "<!-- Identifier: arg, def, " + str(indexOf(currentToken))+ " -->\n") # Chap 11, Stage 1 Comment

            nParsForFunction = nParsForFunction + 1

        else:
            print "E23"
            error()

        performBasicCheck()

        # Loop to write multiple parameter varNames
        while ((currentTokenType == "SYMBOL") & (currentToken == ",")):

            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)
            
            performBasicCheck()

            # Write primitive type parameter
            if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
                stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
                outFile.write(stringToExport)
            
                currentType = currentToken

            # Write object type parameter
            elif ((currentTokenType == "IDENTIFIER")):
                stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
                outFile.write(stringToExport)
                
                currentType = currentToken
                
                outFile.write(tabInsert() + "<!-- Identifier: class, def, no index -->\n") # Chap 11, Stage 1 Comment

            else:
                print "E24"
                error()
                    
            performBasicCheck()
                
            # Write parameter varName
            if ((currentTokenType == "IDENTIFIER")):
                stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
                outFile.write(stringToExport)
                
                # Add ARG variable to class scope symbol table
                define(currentToken, currentType, "ARG")
                
                outFile.write(tabInsert() + "<!-- Identifier: arg, def, " + str(indexOf(currentToken)) + " -->\n") # Chap 11, Stage 1 Comment

            else:
                print "E25"
                error()
            
            performBasicCheck()
    
        # Write parameterList footer
        decrementTab()
        stringToExport = tabInsert() + "</parameterList>\n"
        outFile.write(stringToExport)

        return


def compileVarDec():
    
    print "compileVarDec()\n"
    
    # Write varDec header
    stringToExport = tabInsert() + "<varDec>\n"
    outFile.write(stringToExport)
    
    if ((currentTokenType == "KEYWORD") & (currentToken == "var")):
        incrementTab()
        stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
        outFile.write(stringToExport)
        
        performBasicCheck()
    
        # Write primitive type varDec
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
            stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
            outFile.write(stringToExport)
        
            currentType = currentToken
        
        # Write object type varDec
        elif ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            currentType = currentToken

            outFile.write(tabInsert() + "<!-- Identifier: class, def, no index -->\n") # Chap 11, Stage 1 Comment

        else:
            print "E26"
            error()
        
        performBasicCheck()
        
        # Write varDec varName
        if ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            # Add VAR variable to class scope symbol table
            define(currentToken, currentType, "VAR")

            outFile.write(tabInsert() + "<!-- Identifier: var, def, " + str(indexOf(currentToken)) + " -->\n") # Chap 11, Stage 1 Comment

        else:
            print "E27"
            error()
    
        performBasicCheck()
        
        # Loop to write multiple varNames
        while ((currentTokenType == "SYMBOL") & (currentToken == ",")):
            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)
            
            performBasicCheck()
            
            # Write varName
            if ((currentTokenType == "IDENTIFIER")):
                stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
                outFile.write(stringToExport)
                
                # Add VAR variable to class scope symbol table
                define(currentToken, currentType, "VAR")
            
                outFile.write(tabInsert() + "<!-- Identifier: var, def, " + str(indexOf(currentToken)) + " -->\n") # Chap 11, Stage 1 Comment

            else:
                print "E28"
                error()
            
            performBasicCheck()
        
        # Writing a ; statement close
        if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)
        
            performBasicCheck()
        
        else:
            print "E29"
            error()
    else:
        print "E30"
        error()
    
    # Write varDec footer
    decrementTab()
    stringToExport = tabInsert() + "</varDec>\n"
    outFile.write(stringToExport)
    
    return


def compileStatements():
    
    print "compileStatements()\n"
    
    # Write compileStatements header
    stringToExport = tabInsert() + "<statements>\n"
    outFile.write(stringToExport)
    
    incrementTab()
    
    while ((currentTokenType != "SYMBOL") & (currentToken != "}")):
        
        if ((currentTokenType == "KEYWORD") & (currentToken == "let")):
            compileLet()
        elif ((currentTokenType == "KEYWORD") & (currentToken == "if")):
            compileIf()
        elif ((currentTokenType == "KEYWORD") & (currentToken == "while")):
            compileWhile()
        elif ((currentTokenType == "KEYWORD") & (currentToken == "do")):
            compileDo()
        elif ((currentTokenType == "KEYWORD") & (currentToken == "return")):
            compileReturn()
        else:
            print "E31"
            error()

    decrementTab()

    # Write compileStatements footer
    stringToExport = tabInsert() + "</statements>\n"
    outFile.write(stringToExport)

    return


def compileDo():
    
    isVoid = True # This needs to be checked!!!!
    
    print "compileDo()\n"
    
    # Write compileDo header
    stringToExport = tabInsert() + "<doStatement>\n"
    outFile.write(stringToExport)
    
    incrementTab()
    
    # Write do keyword
    if ((currentTokenType == "KEYWORD") & (currentToken == "do")):
        stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
        outFile.write(stringToExport)
    
        performBasicCheck()
    
        # Found a method subroutine call
        if (currentTokenType == "IDENTIFIER"):
            lookAhead = tokenizedSource[currentPos] # Not currentPos + 1 due to advance() counting...
    
            # Found a method subroutine (i.e., do whatever(x) ) // in class MyClass, method:  push this; push x; call MyClass.whatever 2)
            if (lookAhead == "("):
                
                # Writing a subroutineName
                stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
                outFile.write(stringToExport)
                
                outFile.write(tabInsert() + "<!-- Identifier: subroutine, used, no index -->\n") # Chap 11, Stage 1 Comment
                
                # CodeGen
                currentSubroutineName = currentToken
                classToCall = currentClass
            
                performBasicCheck()
               
                # Writing ( symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)
                
                    performBasicCheck()
                    
                    # CodeGen
                    writePush("POINTER", 0)
                
                    # Write expressionList
                    compileExpressionList()
                    
                    # CodeGen
                    writeCall(classToCall + "." + currentSubroutineName, nArgsToCall + 1)
                    if (isVoid): # Need to pop and ignore stack for a void method subroutine
                        writePop("TEMP", 0)
        
                    # Write ) symbol
                    if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
                        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                        outFile.write(stringToExport)
                    
                        performBasicCheck()
                        
                        # Write ; end of statement
                        if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
                            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                            outFile.write(stringToExport)
                        
                            performBasicCheck()
                
                        else:
                            print "E32"
                            error()
                    else:
                        print "E33"
                        error()
                else:
                    print "E34"
                    error()

            # Found a function/constructor (class) or method (var)subroutine call
            elif (lookAhead == "."):
                
                # Writing a class/var name
                stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
                outFile.write(stringToExport)
                
                # Found a method call
                if (kindOf(currentToken) == "VAR"):
                    outFile.write(tabInsert() + "<!-- Identifier: var, used, " + str(indexOf(currentToken)) + " -->\n") # Chap 11, Stage 1 Comment
                    #subroutine method call (do foo.bar(x); // method:  push foo; push x; call Foo.bar 2)
                    
                    # CodeGen
                    writePush("LOCAL", indexOf(currentToken))
                    classToCall = typeOf(currentToken)
                    isMethod = True
                                          
                elif (kindOf(currentToken) == "FIELD"):
                    outFile.write(tabInsert() + "<!-- Identifier: field, used, " + str(indexOf(currentToken)) + " -->\n") # Chap 11, Stage 1 Comment
                    #subroutine method call (do foo.bar(x); // method:  push foo; push x; call Foo.bar 2)
                    
                    # CodeGen
                    classToCall = typeOf(currentToken)
                    isMethod = True
               
                # Found a function/constuctor call
                elif (kindOf(currentToken) == "NONE"):
                    outFile.write(tabInsert() + "<!-- Identifier: class, used, no index -->\n") # Chap 11, Stage 1 Comment
                    #subroutine function call (do Sys.error(x); // function:  push x; call Sys.error 1)
                    
                    # CodeGen
                    classToCall = currentToken
                    isMethod = False

                performBasicCheck()
                
                # Write a . symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == ".")):
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)
                    
                    performBasicCheck()
                    
                    # Write a subroutineName
                    stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
                    outFile.write(stringToExport)
                    
                    outFile.write(tabInsert() + "<!-- Identifier: subroutine, used, no index -->\n") # Chap 11, Stage 1 Comment
                    
                    # CodeGen
                    subroutineToCall = currentToken
                    
                    performBasicCheck()
            
                    # Writing ( symbol
                    if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
                        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                        outFile.write(stringToExport)
                    
                        performBasicCheck()
                    
                        # Write expressionList
                        compileExpressionList()
                        
                        # CodeGen
                        if (isMethod):
                            writePush("THIS", 0)
                            writeCall(classToCall + "." + subroutineToCall, nArgsToCall + 1) # Methods operate on K + 1 arguments
                        elif (~isMethod):
                            writeCall(classToCall + "." + subroutineToCall, nArgsToCall) # Functions/Constructors operate on K arguments

                        if (isVoid): # Need to pop and ignore stack for a void function/method subroutine
                            writePop("TEMP", 0)
                    
                        # Write ) symbol
                        if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
                            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                            outFile.write(stringToExport)
                        
                            performBasicCheck()
                        
                            # Write ; end of statement
                            if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
                                stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                                outFile.write(stringToExport)
                            
                                performBasicCheck()

                            else:
                                print "E35"
                                error()
                        else:
                            print "E36"
                            error()
                    else:
                        print "E37"
                        error()
                else:
                    print "E38"
                    error()
            else:
                print "E39"
                error()
        else:
            print "E40"
            error()

    decrementTab()
    
    # Write compileDo footer
    stringToExport = tabInsert() + "</doStatement>\n"
    outFile.write(stringToExport)
    
    return


def compileLet():
    
    print "compileLet()\n"
    
    # Write compileLet header
    stringToExport = tabInsert() + "<letStatement>\n"
    outFile.write(stringToExport)
    
    incrementTab()
    
    # Write let keyword
    if ((currentTokenType == "KEYWORD") & (currentToken == "let")):
        stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
        outFile.write(stringToExport)
        
        performBasicCheck()
    
        # Write varName
        if (currentTokenType == "IDENTIFIER"):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            outFile.write(tabInsert() + "<!-- Identifier: " + str(kindOf(currentToken)).lower() + ", used, " + str(indexOf(currentToken))+ " -->\n") # Chap 11, Stage 1 Comment
            
            # CodeGen
            variableToAssign = currentToken
            isArray = False
        
            performBasicCheck()
            
            # Found an expression/array & write [ symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == "[")):
                stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                outFile.write(stringToExport)
                
                #CodeGen
                isArray = True
            
                performBasicCheck()
            
                # Write expression
                compileExpression()
                
                # CodeGen
                writePush("LOCAL", indexOf(variableToAssign))
                writeArithmetic("ADD")
                
                # Write ] symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == "]")):
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)
                
                    performBasicCheck()
        
        
            # Write = symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == "=")):
                stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                outFile.write(stringToExport)
            
                performBasicCheck()
            
                # Compile expression
                compileExpression()
                
                # CodeGen
                if (kindOf(variableToAssign) == "VAR"):
                    if isArray:
                        writePop("TEMP", 0)
                        writePop("POINTER", 1)
                        writePush("TEMP", 0)
                        writePop("THAT", 0)
                    elif ~isArray:
                        writePop("LOCAL", indexOf(variableToAssign))
                
                elif (kindOf(variableToAssign) == "ARG"):
                    writePop("ARG", indexOf(variableToAssign))
                        
                elif (kindOf(variableToAssign) == "FIELD"):
                    writePop("THIS", indexOf(variableToAssign))
    
                # Write ; end of statement
                if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)
                
                    performBasicCheck()

                else:
                    print "E41"
                    error()
            else:
                print "E42"
                error()
        else:
            print "E43"
            error()
    else:
        print "E44"
        error()
    
    
    decrementTab()
    
    # Write compileLet footer
    stringToExport = tabInsert() + "</letStatement>\n"
    outFile.write(stringToExport)
    
    return


def compileWhile():
    
    global currentLabelIndex

    print "compileWhile()\n"
    
    # Process function label indexes
    L1 = currentLabelIndex
    L2 = currentLabelIndex + 1
    currentLabelIndex = currentLabelIndex + 2

    # Write compileWhile header
    stringToExport = tabInsert() + "<whileStatement>\n"
    outFile.write(stringToExport)

    incrementTab()
    
    # Write while keyword
    if ((currentTokenType == "KEYWORD") & (currentToken == "while")):
        stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
        outFile.write(stringToExport)
        
        performBasicCheck()
        
        # CodeGen
        writeLabel(currentSubroutineName + "$L" + str(L1))
    
        # Write ( symbol
        if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)
        
            performBasicCheck()
        
            # Write expression
            compileExpression()
            
            # CodeGen
            writeArithmetic("NOT")
            writeIf(currentSubroutineName + "$L" + str(L2))
        
            # Write ) symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
                stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                outFile.write(stringToExport)
            
                performBasicCheck()
            
                # Write { symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == "{")):
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)
                
                    performBasicCheck()
                
                    # Write statement(s)
                    compileStatements()
                    
                    # CodeGen
                    writeGoto(currentSubroutineName + "$L" + str(L1))
                
                    # Write } symbol
                    if ((currentTokenType == "SYMBOL") & (currentToken == "}")):
                        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                        outFile.write(stringToExport)
                        
                        # CodeGen
                        writeLabel(currentSubroutineName + "$L" + str(L2))
                    
                        performBasicCheck()

                    else:
                        print "E45"
                        error()
                else:
                    print "E46"
                    error()
            else:
                print "E47"
                error()
        else:
            print "E48"
            error()
    else:
        print "E49"
        error()


    decrementTab()
    
    # Write compileWhile footer
    stringToExport = tabInsert() + "</whileStatement>\n"
    outFile.write(stringToExport)
    
    return


def compileReturn():
    
    print "compileReturn()\n"
    
    # Write compileReturn header
    stringToExport = tabInsert() + "<returnStatement>\n"
    outFile.write(stringToExport)
    
    # Write return keyword
    if ((currentTokenType == "KEYWORD") & (currentToken == "return")):

        incrementTab()
        stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
        outFile.write(stringToExport)
    
        performBasicCheck()

        voidReturn = True

        while not currentToken == ";":
            compileExpression()
            voidReturn = False

        if voidReturn:
            writePush("CONST", 0)
        
        writeReturn()

    # Write ; end of statement
    if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
        
        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
        outFile.write(stringToExport)

        performBasicCheck()
        
    else:
        print "E50"
        error()

    # Write compileReturn footer
    decrementTab()
    stringToExport = tabInsert() + "</returnStatement>\n"
    outFile.write(stringToExport)

    return


def compileIf():
    
    global currentLabelIndex

    print "compileIf()\n"
    
    # Process function label indexes
    L1 = currentLabelIndex
    L2 = currentLabelIndex + 1
    L3 = currentLabelIndex + 2
    currentLabelIndex = currentLabelIndex + 3
    
    # Write compileIf header
    stringToExport = tabInsert() + "<ifStatement>\n"
    outFile.write(stringToExport)
    
    incrementTab()
    
    # Write if keyword
    if ((currentTokenType == "KEYWORD") & (currentToken == "if")):
        stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
        outFile.write(stringToExport)
        
        performBasicCheck()
        
        # Write ( symbol
        if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)
            
            performBasicCheck()
            
            # Write expression
            compileExpression()
            
            # CodeGen
            writeIf(currentSubroutineName + "$L" + str(L1))
            writeGoto(currentSubroutineName + "$L" + str(L2))
            
            
            # Write ) symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
                stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                outFile.write(stringToExport)
                
                performBasicCheck()
                
                # Write { symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == "{")):
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)
                    
                    performBasicCheck()
                    
                    # CodeGen
                    writeLabel(currentSubroutineName + "$L" + str(L1))
                    
                    # Write statement(s)
                    compileStatements()
                    
                    # Write } symbol
                    if ((currentTokenType == "SYMBOL") & (currentToken == "}")):
                        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                        outFile.write(stringToExport)
                        
                        performBasicCheck()
                    
                        # Check if there's an additional else statement...
                        if ((currentTokenType == "KEYWORD") & (currentToken == "else")):
                            stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
                            outFile.write(stringToExport)
                            
                            # CodeGen
                            writeGoto(currentSubroutineName + "$L" + str(L3))
                            writeLabel(currentSubroutineName + "$L" + str(L2))
                            
                            performBasicCheck()

                            # Write { symbol
                            if ((currentTokenType == "SYMBOL") & (currentToken == "{")):
                                stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                                outFile.write(stringToExport)
        
                                performBasicCheck()
                
                                # Write statement(s)
                                compileStatements()
                    
                                # Write } symbol
                                if ((currentTokenType == "SYMBOL") & (currentToken == "}")):
                                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                                    outFile.write(stringToExport)
                        
                                    performBasicCheck()
                                
                                    # CodeGen
                                    writeLabel(currentSubroutineName + "$L" + str(L3))
                                
                                else:
                                    print "E51"
                                    error()
                            else:
                                print "E52"
                                error()
                        else:
                            # No else statement/if only
                            # CodeGen
                            writeLabel(currentSubroutineName + "$L" + str(L2))
                            
                    else:
                        print "E53"
                        error()
                else:
                    print "E54"
                    error()
            else:
                print "E55"
                error()
        else:
            print "E56"
            error()
    else:
        print "E57"
        error()


    # Write compileIf Footer
    decrementTab()
    stringToExport = tabInsert() + "</ifStatement>\n"
    outFile.write(stringToExport)

    return


def compileExpression():
    
    print "compileExpression()\n"
    
    opToCall = ""
    
    # Write compileExpression header
    stringToExport = tabInsert() + "<expression>\n"
    outFile.write(stringToExport)
    
    incrementTab()

    compileTerm()
    
    # Write an Op
    while ((currentTokenType == "SYMBOL") & ((currentToken == "+") | (currentToken == "-") | (currentToken == "*") | (currentToken == "/") | (currentToken == "&") | (currentToken == "|") | (currentToken == "<") | (currentToken == ">") | (currentToken == "="))):
        # Account for the 3 op XML exceptions, <,>,&
        if currentToken == "<":
            stringToExport = tabInsert() + "<symbol> &lt; </symbol>\n"
            outFile.write(stringToExport)
        elif currentToken == ">":
            stringToExport = tabInsert() + "<symbol> &gt; </symbol>\n"
            outFile.write(stringToExport)
        elif currentToken == "&":
            stringToExport = tabInsert() + "<symbol> &amp; </symbol>\n"
            outFile.write(stringToExport)
        else:
            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)
            
        # Flag the arithmatic Op to use for later RPN
        if (currentToken == "+"):
            opToCall = "+"
        elif (currentToken == "-"):
            opToCall = "-"
        elif (currentToken == "*"):
            opToCall = "*"
        elif (currentToken == "/"):
            opToCall = "/"
        elif (currentToken == "="):
            opToCall = "="
        elif (currentToken == ">"):
            opToCall = ">"
        elif (currentToken == "<"):
            opToCall = "<"
        elif (currentToken == "&"):
            opToCall = "&"
        elif (currentToken == "|"):
            opToCall = "|"

        performBasicCheck()

        compileTerm()

    # Output the Op for RPN notation
    if (opToCall == "+"):
        writeArithmetic("ADD")
    elif (opToCall == "-"):
        writeArithmetic("SUB")
    elif (opToCall == "*"):
        outFile3.write("call Math.multiply 2\n")
    elif (opToCall == "/"):
        outFile3.write("call Math.divide 2\n")
    elif (opToCall == "="):
        writeArithmetic("EQ")
    elif (opToCall == ">"):
        writeArithmetic("GT")
    elif (opToCall == "<"):
        writeArithmetic("LT")
    elif (opToCall == "&"):
        writeArithmetic("AND")
    elif (opToCall == "|"):
        writeArithmetic("OR")

    decrementTab()

    # Write compileExpression footer
    stringToExport = tabInsert() + "</expression>\n"
    outFile.write(stringToExport)

    return


def compileTerm():
    
    print "compileTerm()\n"
    
    # Write compileTerm header
    stringToExport = tabInsert() + "<term>\n"
    outFile.write(stringToExport)
    
    incrementTab()
    
    # Analyze the term components...

    # Found an integerConstant...
    if currentTokenType == "INT_CONST":
        stringToExport = tabInsert() + "<integerConstant> " + currentToken + " </integerConstant>\n"
        outFile.write(stringToExport)
        
        writePush("CONST", currentToken)
    
        performBasicCheck()

    # Found a stringConstant...
    elif currentTokenType == "STRING_CONST":
        stringToExport = tabInsert() + "<stringConstant> " + currentToken.strip("\"") + " </stringConstant>\n"
        outFile.write(stringToExport)
        
        # Code Gen
        stringToProcess = currentToken.strip("\"")
        stringLength = len(stringToProcess)
        writePush("CONST", stringLength)
        writeCall("String.new", 1)
        
        i = 0
        while (i < stringLength):
            writePush("CONST", ord(stringToProcess[i]))
            writeCall("String.appendChar", 2)
            i = i + 1

        performBasicCheck()
    
    # Found a keywordConstant...
    elif ((currentTokenType == "KEYWORD") & ((currentToken == "true") | (currentToken == "false") | (currentToken == "null") | (currentToken == "this"))):
        stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
        outFile.write(stringToExport)
        
        # CodeGen
        if (currentToken == "true"):
            writePush("CONST", 0)
            writeArithmetic("NOT")
        if (currentToken == "false"):
            writePush("CONST", 0)
        if (currentToken == "this"):
            writePush("POINTER", 0)

        performBasicCheck()

    # Found a unaryOp term
    elif ((currentTokenType == "SYMBOL") & ((currentToken == "-") | (currentToken == "~"))):
        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
        outFile.write(stringToExport)
        
        # CodeGen
        opToCall = currentToken

        performBasicCheck()

        compileTerm()
    
        # CodeGen
        if (opToCall == "-"):
            writeArithmetic("NEG")
        if (opToCall == "~"):
            writeArithmetic("NOT")


    # Found an (expression)...
    elif ((currentTokenType == "SYMBOL") & (currentToken == "(")):
        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
        outFile.write(stringToExport)
        
        performBasicCheck()
        
        compileExpression()
        
        if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)
            
            performBasicCheck()
        
        else:
            print "E66"
            error()

    # Found an Identifier...
    elif (currentTokenType == "IDENTIFIER"):
        lookAhead = tokenizedSource[currentPos] # Not currentPos + 1 due to advance() counting...
        
        # Found a varName[array]
        if lookAhead == "[":
            # Writing the varName
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            outFile.write(tabInsert() + "<!-- Identifier: " + str(kindOf(currentToken)).lower() + ", used, " + str(indexOf(currentToken)) + " -->\n") # Chap 11, Stage 1 Comment
            
            # CodeGen
            variableToAssign = currentToken
        
            performBasicCheck()
        
            if ((currentTokenType == "SYMBOL") & (currentToken == "[")):
                
                # Writing [ symbol
                stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                outFile.write(stringToExport)
                
                performBasicCheck()
                
                # Writing the expression...
                incrementTab()
                
                compileExpression()
                
                # CodeGen
                writePush("LOCAL", indexOf(variableToAssign))
                
                decrementTab()
                
                if ((currentTokenType == "SYMBOL") & (currentToken == "]")):
                    # Writing ] symbol
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)
                    
                    # CodeGen
                    writeArithmetic("ADD")
                    writePop("POINTER", 1)
                    writePush("THAT", 0)
                
                    performBasicCheck()

                else:
                    print "E58"
                    error()
            else:
                print "E59"
                error()

        # Found a method subroutine call
        elif (lookAhead == "("):
            
            # Writing a subroutineName
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            outFile.write(tabInsert() + "<!-- Identifier: subroutine, used, no index -->\n") # Chap 11, Stage 1 Comment

            performBasicCheck()
            
            # Writing ( symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
                stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                outFile.write(stringToExport)
                
                performBasicCheck()
                
                # Write expressionList
                compileExpressionList()
                
                # Writing ) symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)
        
                    performBasicCheck()
                
                else:
                    print "E60"
                    error()
            else:
                print "E61"
                error()

        # Found a function/constructor (class) or method (var)subroutine call
        elif (lookAhead == "."):
        
            # Writing a class/var name
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            # CodeGen
            classToCall = currentToken
            
            # Found a method call
            if (kindOf(currentToken) == "VAR"):
                outFile.write(tabInsert() + "<!-- Identifier: var, used, " + str(indexOf(currentToken)) + " -->\n") # Chap 11, Stage 1 Comment
                #subroutine method call (do foo.bar(x); // method:  push foo; push x; call Foo.bar 2)
                
            elif (kindOf(currentToken) == "FIELD"):
                outFile.write(tabInsert() + "<!-- Identifier: field, used, " + str(indexOf(currentToken)) + " -->\n") # Chap 11, Stage 1 Comment
                #subroutine method call (do foo.bar(x); // method:  push foo; push x; call Foo.bar 2)


            # Found a function/constuctor call
            elif (kindOf(currentToken) == "NONE"):
                outFile.write(tabInsert() + "<!-- Identifier: class, used, no index -->\n") # Chap 11, Stage 1 Comment
                #subroutine function call (do Sys.error(x); // function:  push x; call Sys.error 1)

            performBasicCheck()
            
            # Write a . symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == ".")):
                stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                outFile.write(stringToExport)
                
                performBasicCheck()
                
                # Write a subroutineName
                stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
                outFile.write(stringToExport)
                
                outFile.write(tabInsert() + "<!-- Identifier: subroutine, used, no index -->\n") # Chap 11, Stage 1 Comment
                
                # CodeGen
                subroutineToCall = currentToken
                
                performBasicCheck()
            
                # Writing ( symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)
                
                    performBasicCheck()
                
                    # Write expressionList
                    compileExpressionList()
                    
                    # CodeGen
                    writeCall(classToCall + "." + subroutineToCall, nArgsToCall)

                    # Writing ) symbol
                    if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
                        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                        outFile.write(stringToExport)
                    
                        performBasicCheck()
                
                    else:
                        print "E62"
                        error()
                else:
                    print "E63"
                    error()
            else:
                print "E64"
                error()


        # Found a varName
        elif ((lookAhead != "(") & (lookAhead != ".")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
            
            outFile.write(tabInsert() + "<!-- Identifier: " + str(kindOf(currentToken)).lower() + ", used, " + str(indexOf(currentToken)) + " -->\n") # Chap 11, Stage 1 Comment
            
            # CodeGen
            if (kindOf(currentToken) == "VAR"):
                writePush("LOCAL", indexOf(currentToken))
            elif (kindOf(currentToken) == "ARG"):
                writePush("ARG", indexOf(currentToken))
            elif (kindOf(currentToken) == "FIELD"):
                writePush("THIS", indexOf(currentToken))
        
            performBasicCheck()

        else:
            print "E65"
            error()
    else:
        print "E67"
        error()
    
    decrementTab()

    # Write compileTerm footer
    stringToExport = tabInsert() + "</term>\n"
    outFile.write(stringToExport)

    return


def compileExpressionList():
    
    global nArgsToCall
    
    print "compileExpressionList()\n"
    
    nArgsToCall = 0
    
    # Write expressionList header
    stringToExport = tabInsert() + "<expressionList>\n"
    outFile.write(stringToExport)
    
    incrementTab()
    
    if not ((currentTokenType == "SYMBOL") & (currentToken == ")")):
        
        compileExpression()
        
        nArgsToCall = nArgsToCall + 1
    
        # Loop to write multiple expressions
        while ((currentTokenType == "SYMBOL") & (currentToken == ",")):
        
            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)
            
            performBasicCheck()
            
            compileExpression()

            nArgsToCall = nArgsToCall + 1

    decrementTab()

    # Write expressionList footer
    stringToExport = tabInsert() + "</expressionList>\n"
    outFile.write(stringToExport)
    
    return


## SYMBOL TABLE MODULE ##

def symbolTableConstructor():
    
    global classScopeSymbolTable, currentFieldIndex, currentStaticIndex
    
    # Reset class scope variables
    classScopeSymbolTable = {}
    currentFieldIndex = 0
    currentStaticIndex = 0
    
    return


def startSubroutine():
    
    global subroutineScopeSymbolTable, currentVarIndex, currentArgIndex
    
    # Reset subroutine scope variables
    subroutineScopeSymbolTable = {}
    currentVarIndex = 0
    currentArgIndex = 0
    
    return


def define(name, type, kind):
    
    global classScopeSymbolTable, subroutineScopeSymbolTable, currentFieldIndex, currentStaticIndex, currentVarIndex, currentArgIndex

    if kind == "FIELD":
        classScopeSymbolTable[name] = [type, kind, currentFieldIndex]
        currentFieldIndex = currentFieldIndex + 1
    
    elif kind == "STATIC":
        classScopeSymbolTable[name] = [type, kind, currentStaticIndex]
        currentStaticIndex = currentStaticIndex + 1

    elif kind == "VAR":
        subroutineScopeSymbolTable[name] = [type, kind, currentVarIndex]
        currentVarIndex = currentVarIndex + 1

    elif kind == "ARG":
        subroutineScopeSymbolTable[name] = [type, kind, currentArgIndex]
        currentArgIndex = currentArgIndex + 1

    return


def varCount(kind):
    
    if ((kind == "FIELD") | (kind == "STATIC")):
        currentScope = classScopeSymbolTable
    elif ((kind == "ARG") | (kind == "VAR")):
        currentScope = subroutineScopeSymbolTable

    varCount = 0
    for e in currentScope:
        temp = currentScope[e]
        if temp[1] == kind: # Match the kind element of the value pair, which is indexed to 1
            varCount = varCount + 1
           
    return varCount



def kindOf(name):
    
    # First, check subroutine scope symbol table
    for e in subroutineScopeSymbolTable:
        if (name == e):
            temp = subroutineScopeSymbolTable[e]
            return temp[1] # Match the kind element of the value pair, which is indexed to 1

    # Then, if no match, check class scope symbol table
    for e in classScopeSymbolTable:
        if (name == e):
            temp = classScopeSymbolTable[e]
            return temp[1] # Match the kind element of the value pair, which is indexed to 1

    return "NONE" # Return NONE if no matches found


def typeOf(name):
    
    # First, check subroutine scope symbol table
    for e in subroutineScopeSymbolTable:
        if (name == e):
            temp = subroutineScopeSymbolTable[e]
            return temp[0] # Match the type element of the value pair, which is indexed to 0

    # Then, if no match, check class scope symbol table
    for e in classScopeSymbolTable:
        if (name == e):
            temp = classScopeSymbolTable[e]
            return temp[0] # Match the type element of the value pair, which is indexed to 0

    return "ERROR - NO TYPE/NO IDENTIFIER FOUND"

def indexOf(name):
    
    # First, check subroutine scope symbol table
    for e in subroutineScopeSymbolTable:
        if (name == e):
            temp = subroutineScopeSymbolTable[e]
            return temp[2] # Match the running index element of the value pair, which is indexed to 2

    # Then, if no match, check class scope symbol table
    for e in classScopeSymbolTable:
        if (name == e):
            temp = classScopeSymbolTable[e]
            return temp[2] # Match the running index element of the value pair, which is indexed to 2

    return "ERROR - NO RUNNING INDEX/NO IDENTIFIER FOUND"


## VMWRITER MODULE ##

def vmwriterConstructor(outFilename3):
    
    global outFile3
    
    outFile3 = open(outFilename3, 'w') # Opens the VM code writer file
    print "Writing the Destination VM Code Writer file (*.vm): " + outFilename3

    return


def writePush(segment, index):
    
    global outFile3
    
    if (segment == "CONST"):
        insertString = "constant"
    elif (segment == "ARG"):
        insertString = "argument"
    else:
        insertString = str(segment.lower())

    outFile3.write("push " + insertString + " " + str(index) + "\n")

    return


def writePop(segment, index):
    
    global outFile3
    
    if (segment == "CONST"):
        insertString = "constant"
    elif (segment == "ARG"):
        insertString = "argument"
    else:
        insertString = str(segment.lower())
    
    outFile3.write("pop " + insertString + " " + str(index) + "\n")
    
    return


def writeArithmetic(command):
    
    global outFile3
    
    outFile3.write(str(command.lower()) + "\n")
    
    return


def writeLabel(label):
    
    global outFile3
    
    outFile3.write("label " + label + "\n")

    return


def writeGoto(label):
    
    global outFile3
    
    outFile3.write("goto " + label + "\n")
    
    return


def writeIf(label):
    
    global outFile3
    
    outFile3.write("if-goto " + label + "\n")
    
    return


def writeCall(name, nArgs):
    
    global outFile3
    
    outFile3.write("call " + name + " " + str(nArgs) + "\n")

    return


def writeFunction(name, nLocals):
    
    global outFile3
    
    outFile3.write("function " + name + " " + str(nLocals) + "\n")
    
    return


def writeReturn():
    
    outFile3.write("return\n")
    
    return


def vmwriterClose():
    
    global outFile3

    outFile3.write("\n// END OF FILE\n")
    outFile3.close()

    return


## HELPER ROUTINES ##

def performBasicCheck():

    global currentToken, currentTokenType

    if hasMoreTokens():
        currentToken = advance()
        currentTokenType = tokenType()
    elif not hasMoreTokens() & ((currentPos + 1) == len(tokenizedSource)): # At end of tokenizedSource elements
        return
    else:
        print "E68"
        error()
    
    return


def error():
    
    print "ERROR at Token #" + str(currentPos - 1) + "\n"
    print "Prior Token = " + str(tokenizedSource[currentPos - 2])
    print "Current Token = " + currentToken;
    print "Next Token = " + str(tokenizedSource[currentPos]) + "\n"
    
    # Print indexed tokenizedSource for reference
    i = 0
    temp = ""
    
    while (i < len(tokenizedSource)):
        temp = temp + "(" + str(i) + ") " + str(tokenizedSource[i]) + "  "
        i = i + 1
    print temp

    print "\n-----\n"

    return


def incrementTab():

    global tabLevel

    tabLevel = tabLevel + 1
    
    return


def decrementTab():
    
    global tabLevel
    
    tabLevel = tabLevel - 1
    if tabLevel < 0:
        tabLevel = 0

    return

def tabInsert():
    
    global tabLevel
    
    tabs = ""
    i = 0

    while (i < tabLevel):
        tabs = tabs + "\t"
        i = i + 1
    
    return tabs


# Process main routine
main()
