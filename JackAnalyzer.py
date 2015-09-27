################################
####### JRD JACK ANALYZER ######
################################

## JACK TOKENIZER MODULE ##

# Global variable declarations
currentPos = 0
currentToken = ""
currentTokenType = ""
outFile = ""
outFile2 = ""
tokenizedSource = []
tabLevel = 0

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
    userInput = "squaregame.jack" # Test without user input
    
    print "\nThis is the Initial Source Input: " + userInput
    
    if userInput.find(".jack") == -1: # Directory input
        inputType = "directory"
        print "(Source is a Directory Input)\n"
        import os
        scriptPath = os.path.dirname(os.path.abspath(__file__))
        sourcePath = scriptPath + "/" + userInput + "/"
        print "Source Path = " + sourcePath + "\n"
        
        sourceDirectoryList = os.listdir(sourcePath)
        print sourceDirectoryList
    
        for sourceFile in sourceDirectoryList:
            if sourceFile.find(".jack") != -1: # Found a .jack file
                
                print sourceFile

                outFilename = sourcePath + sourceFile[0:sourceFile.find(".")] + ".xml" # Creates **.xml for main parser file
                print outFilename
                outFilename2 = sourcePath + sourceFile[0:sourceFile.find(".")] + "T.xml" # Creates **T.xml for tokenizer ref file
                print outFilename2
                
                sourceFile = sourcePath + sourceFile
            
                jackTokenizerConstructor(sourceFile, outFilename, outFilename2)


    elif userInput.find(".jack") != -1: # File input
        inputType = "file"
        print "(Source Input is a FILE)\n"

        sourceFile = userInput

        print "This is the Current Source File: " + sourceFile

        outFilename = sourceFile[0:sourceFile.find(".")] + ".xml" # Creates **.xml for main parser file
        outFilename2 = sourceFile[0:sourceFile.find(".")] + "T.xml" # Creates **T.xml for tokenizer ref file
        
        jackTokenizerConstructor(sourceFile, outFilename, outFilename2)
    
    else:
        print "E60"
        error()

    print "\n----------------------------\n** JACK ANALYZER Complete **"

    return


def jackTokenizerConstructor(sourceFile, outFilename, outFilename2):
    
    global outFile, outFile2

    # Open the outFile(s)
    outFile = open(outFilename, 'w') # Opens the main parser file
    outFile2 = open(outFilename2, 'w') # Opens the tokenizer ref file
    print "Writing the Destination File (*.xml) and Tokenizer Ref File (*T.xml): " + outFilename + " and " + outFilename2 + "\n"
    

    # Get date/time stamp
    from time import localtime, strftime
    temp = strftime("%a, %d, %b, %Y, %X", localtime())

    # Write headers into outFile(s)
    outFile.write("<!-- \nJACK ANALYZED\nSOURCE CODE FROM: " + sourceFile + "\nON: " + temp + "\n-->\n\n")
    outFile2.write("<!-- \nJACK ANALYZED\nSOURCE CODE FROM: " + sourceFile + "\nON: " + temp + "\n-->\n\n") # tokenizer ref file

    # Process file
    processFile(sourceFile)

    # Close main outFile
    outFile.write("\n<!-- \nEND OF FILE\n-->")
    outFile.close()

    # Close tokenizer ref file
    outFile2.write("</tokens>\n") # Write footer
    outFile2.write("\n<!-- \nEND OF FILE\n-->")
    outFile2.close()

    return


def processFile(sourceFile):
    
    global tokenizedSource, currentPos, currentToken, currentTokenType
 
    # Write tokenizer ref file header
    outFile2.write("<tokens>\n")
 
    tokenizedSource = tokenizeFile(sourceFile) # Tokenize the source file
    print "Tokenized Source Code: \n"
    print tokenizedSource
    print "\n--------------------------------------------\n"
    
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
            outFile2.write("\t<stringConstant> " + currentToken + " </stringConstant>\n") # tokenizer ref file
        
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
    
    global currentToken, currentTokenType
    
    print "compileClass()\n"
    
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
                        print "E1"
                        error()
                        
                    performBasicCheck()
                
                # Write }
                if ((currentTokenType == "SYMBOL") & (currentToken == "}")):
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)

                else:
                    print "E2"
                    error()
            else:
                print "E3"
                error()
        else:
            print "E4"
            error()

        decrementTab()

        # Write class footer
        stringToExport = tabInsert() + "</class>\n"
        outFile.write(stringToExport)

    else:
        print "E5"
        error()

    return


def compileClassVarDec():

    print "compileClassVarDec()\n"
    
    # Write classVarDec header
    stringToExport = tabInsert() + "<classVarDec>\n"
    outFile.write(stringToExport)
    
    incrementTab()
    
    if ((currentTokenType == "KEYWORD") & ((currentToken == "static") | (currentToken == "field"))):
        stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
        outFile.write(stringToExport)
        
        performBasicCheck()
        
        # Write type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
            stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
            outFile.write(stringToExport)
        
        elif ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
        
        else:
            print "E6"
            error()
    
        performBasicCheck()
        
        # Write varName
        if ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)

        else:
            print "E7"
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
            
            else:
                print "E8"
                error()
                    
            performBasicCheck()
        
        # Writing a ; statement close
        if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)

        else:
            print "E9"
            error()

        decrementTab()

        # Write classVarDec footer
        stringToExport = tabInsert() + "</classVarDec>\n"
        outFile.write(stringToExport)
    
    else:
        print "E10"
        error()

    return


def compileSubroutine():
    
    print "compileSubroutine()\n"
    
    # Write subroutineDec header
    stringToExport = tabInsert() + "<subroutineDec>\n"
    outFile.write(stringToExport)
    
    incrementTab()
    
    if ((currentTokenType == "KEYWORD") & ((currentToken == "function") | (currentToken == "method") | (currentToken == "constructor"))):
        stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
        outFile.write(stringToExport)
    
        performBasicCheck()
    
        # Write return type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean") | (currentToken == "void"))):
            stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
            outFile.write(stringToExport)
 
        elif ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)

        else:
            print "E11"
            error()
                
        performBasicCheck()
            
        # Write subroutineName
        if ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
  
        else:
            print "E12"
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
                        
                        if ((currentTokenType == "KEYWORD") & (currentToken == "var")):
                            compileVarDec()
                        elif ((currentTokenType == "KEYWORD") & ((currentToken == "let") | (currentToken == "if") | (currentToken == "while") | (currentToken == "do") | (currentToken == "return"))):
                            compileStatements()
                        else:
                            print "E13"
                            error()
                                
                        performBasicCheck ()
                    
                    # Write }
                    if ((currentTokenType == "SYMBOL") & (currentToken == "}")):
                        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                        outFile.write(stringToExport)
                    
                        # Write subroutineBody footer
                        decrementTab()
                        stringToExport = tabInsert() + "</subroutineBody>\n"
                        outFile.write(stringToExport)

                    else:
                        print "E14"
                        error()
                else:
                    print "E15"
                    error()
            else:
                print "E16"
                error()
        else:
            print "E17"
            error()
    else:
        print "E18"
        error()
    
    decrementTab()
    
    # Write subroutineDec footer
    stringToExport = tabInsert() + "</subroutineDec>\n"
    outFile.write(stringToExport)
    
    return


def compileParameterList():
    
    print "compileParameterList()\n"

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
        
        # Write parameter type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
            incrementTab()
            stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
            outFile.write(stringToExport)

        elif ((currentTokenType == "IDENTIFIER")):
            incrementTab()
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)

        else:
            print "E19"
            error()

        performBasicCheck()
            
        # Write parameter varName
        if ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)

        else:
            print "E20"
            error()

        performBasicCheck()

        # Loop to write multiple parameter varNames
        while ((currentTokenType == "SYMBOL") & (currentToken == ",")):

            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)
            
            performBasicCheck()

            # Write parameter type
            if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
                stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
                outFile.write(stringToExport)
        
            elif ((currentTokenType == "IDENTIFIER")):
                stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
                outFile.write(stringToExport)
        
            else:
                print "E21"
                error()
                    
            performBasicCheck()
                
            # Write parameter varName
            if ((currentTokenType == "IDENTIFIER")):
                stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
                outFile.write(stringToExport)

            else:
                print "E22"
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
    
        # Write varDec type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
            stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
            outFile.write(stringToExport)

        elif ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)

        else:
            print "E23"
            error()
        
        performBasicCheck()
        
        # Write varDec varName
        if ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
        
        else:
            print "E24"
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
            else:
                print "E25"
                error()
            
            performBasicCheck()
        
        # Writing a ; statement close
        if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)
        else:
            print "E26"
            error()
    else:
        print "E27"
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
            print "E28"
            error()

    decrementTab()

    # Write compileStatements footer
    stringToExport = tabInsert() + "</statements>\n"
    outFile.write(stringToExport)

    return


def compileDo():
    
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
    
        # Found a subroutineCall
        if (currentTokenType == "IDENTIFIER"):
            lookAhead = tokenizedSource[currentPos] # Not currentPos + 1 due to advance() counting...
    
            if ((lookAhead == "(") | (lookAhead == ".")):
            # Writing a subroutineName/className/varName
                stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
                outFile.write(stringToExport)
            
                performBasicCheck()

                # Write a . symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == ".")):
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)
                
                    performBasicCheck()
                
                    # Write a subroutineName
                    stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
                    outFile.write(stringToExport)
                
                    performBasicCheck()
        
        
                # Writing ( symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)
                
                    performBasicCheck()
                
                    # Write expressionList
                    compileExpressionList()
                
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
                            print "E29"
                            error()
                    else:
                        print "E30"
                        error()
                else:
                    print "E31"
                    error()
            else:
                print "E32"
                error()
        else:
            print "E33"
            error()
    else:
        print "E34"
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
        
            performBasicCheck()
            
            # Found an expression/array & write [ symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == "[")):
                stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                outFile.write(stringToExport)
            
                performBasicCheck()
            
                # Write expression
                compileExpression()
                
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
    
    
    decrementTab()
    
    # Write compileLet footer
    stringToExport = tabInsert() + "</letStatement>\n"
    outFile.write(stringToExport)
    
    return


def compileWhile():

    print "compileWhile()\n"

    # Write compileWhile header
    stringToExport = tabInsert() + "<whileStatement>\n"
    outFile.write(stringToExport)

    incrementTab()
    
    # Write while keyword
    if ((currentTokenType == "KEYWORD") & (currentToken == "while")):
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
                
                    # Write } symbol
                    if ((currentTokenType == "SYMBOL") & (currentToken == "}")):
                        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                        outFile.write(stringToExport)
                    
                        performBasicCheck()

                    else:
                        print "E39"
                        error()
                else:
                    print "E40"
                    error()
            else:
                print "E41"
                error()
        else:
            print "E42"
            error()
    else:
        print "E43"
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

    while not currentToken == ";":
        compileExpression()

    # Write ; end of statement
    if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
        outFile.write(stringToExport)
        
    else:
        print "E44"
        error()

    # Write compileReturn footer
    decrementTab()
    stringToExport = tabInsert() + "</returnStatement>\n"
    outFile.write(stringToExport)
    
    return


def compileIf():

    print "compileIf()\n"
    
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
                    
                    # Write } symbol
                    if ((currentTokenType == "SYMBOL") & (currentToken == "}")):
                        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                        outFile.write(stringToExport)
                        
                        performBasicCheck()
                    
                        # Check if there's an additional else statement...
                        if ((currentTokenType == "KEYWORD") & (currentToken == "else")):
                            stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
                            outFile.write(stringToExport)
                        
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
        else:
            print "E50"
            error()
    else:
        print "E51"
        error()


    # Write compileIf Footer
    decrementTab()
    stringToExport = tabInsert() + "</ifStatement>\n"
    outFile.write(stringToExport)

    return


def compileExpression():
    
    print "compileExpression()\n"
    
    # Write compileExpression header
    stringToExport = tabInsert() + "<expression>\n"
    outFile.write(stringToExport)
    
    incrementTab()

    compileTerm()
    
    # Write an Op
    if ((currentTokenType == "SYMBOL") & ((currentToken == "+") | (currentToken == "-") | (currentToken == "*") | (currentToken == "/") | (currentToken == "&") | (currentToken == "|") | (currentToken == "<") | (currentToken == ">") | (currentToken == "="))):
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
                
        performBasicCheck()
        
        # Write a second term
        compileTerm()
    
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
    
        performBasicCheck()

    # Found a stringConstant...
    elif currentTokenType == "STRING_CONST":
        stringToExport = tabInsert() + "<stringConstant> " + currentToken.strip("\"") + " </stringConstant>\n"
        outFile.write(stringToExport)

        performBasicCheck()
    
    # Found a keywordConstant...
    elif ((currentTokenType == "KEYWORD") & ((currentToken == "true") | (currentToken == "false") | (currentToken == "null") | (currentToken == "this"))):
        stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
        outFile.write(stringToExport)

        performBasicCheck()

    # Found a unaryOp term
    elif ((currentTokenType == "SYMBOL") & ((currentToken == "-") | (currentToken == "~"))):
        stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
        outFile.write(stringToExport)

        performBasicCheck()

        compileTerm()

    # Found an Identifier...
    elif (currentTokenType == "IDENTIFIER"):
        lookAhead = tokenizedSource[currentPos] # Not currentPos + 1 due to advance() counting...
        
        # Found a varName[array]
        if lookAhead == "[":
            # Writing the varName
            stringToExport = tabInsert() + "<keyword> " + currentToken + " </keyword>\n"
            outFile.write(stringToExport)
        
            performBasicCheck()
        
            if ((currentTokenType == "SYMBOL") & (currentToken == "[")):
                
                # Writing [ symbol
                stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                outFile.write(stringToExport)
                
                performBasicCheck()
                
                # Writing the expression...
                incrementTab()
                compileExpression()
                decrementTab()
                
                if ((currentTokenType == "SYMBOL") & (currentToken == "]")):
                    # Writing ] symbol
                    stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                    outFile.write(stringToExport)
                
                    performBasicCheck()

                else:
                    print "E52"
                    error()
            else:
                print "E53"
                error()

        # Found a subroutineCall
        elif ((lookAhead == "(") | (lookAhead == ".")):
            # Writing a subroutineName/className/varName
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)

            performBasicCheck()
            
            # Write a . symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == ".")):
                stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
                outFile.write(stringToExport)
            
                performBasicCheck()
            
                # Write a subroutineName
                stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
                outFile.write(stringToExport)
            
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
                    print "E54"
                    error()
            else:
                print "E55"
                error()


        # Found a varName
        elif ((lookAhead != "(") & (lookAhead != ".")):
            stringToExport = tabInsert() + "<identifier> " + currentToken + " </identifier>\n"
            outFile.write(stringToExport)
        
            performBasicCheck()

        else:
            print "E56"
            error()


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
            print "E57"
            error()
    else:
        print "E58"
        error()
    
    decrementTab()

    # Write compileTerm footer
    stringToExport = tabInsert() + "</term>\n"
    outFile.write(stringToExport)

    return


def compileExpressionList():
    
    print "compileExpressionList()\n"
    
    # Write expressionList header
    stringToExport = tabInsert() + "<expressionList>\n"
    outFile.write(stringToExport)
    
    incrementTab()
    
    if not ((currentTokenType == "SYMBOL") & (currentToken == ")")):
        
        compileExpression()
    
        # Loop to write multiple expressions
        while ((currentTokenType == "SYMBOL") & (currentToken == ",")):
        
            stringToExport = tabInsert() + "<symbol> " + currentToken + " </symbol>\n"
            outFile.write(stringToExport)
            
            performBasicCheck()
            
            compileExpression()

    decrementTab()

    # Write expressionList footer
    stringToExport = tabInsert() + "</expressionList>\n"
    outFile.write(stringToExport)
    
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
        print "E59"
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
