################################
####### JRD JACK ANALYZER ######
################################

## JACK TOKENIZER MODULE ##

# Global variable declarations
currentPos = 0
currentToken = ""
currentTokenType = ""
out_file = ""
out_fileT = ""
tokenizedSource = []
tabLevel = 0

symbols = ['}', '{', ')', '(', ']', '[', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
stringConstant = "\""


def main():
    
    # Import Jack file form command line script
    from sys import argv
    print "JRD Nand-2-Tetris Jack Analyzer, 2015\n"
    print "Enter the Source Jack File (.jack) or Source Jack Directory (within this path) to be analyzed:"
    #source_input = raw_input(">") # User inputs source...
    source_input = "Square.jack" # Uncomment to test without user input
    
    ## These are the test Jack files.  Uncomment to substitute for source_input ##
    #...
    
    print "\nThis is the Source: " + source_input
    
    jackTokenizerConstructor(source_input)

    return


def jackTokenizerConstructor(input_file_or_stream):
    
    global out_file, out_file2
    
    if input_file_or_stream.find(".jack") == -1: # Directory input
        input_type = "directory"
        print "(Source is a Directory Input)\n"
        import os
        script_path = os.path.dirname(os.path.abspath(__file__))
        source_path = script_path + "/" + input_file_or_stream + "/*.jack"
        print "Source Path = " + source_path + "\n"
    
    if input_file_or_stream.find(".jack") != -1:
        input_type = "file"
        print "(Source is a File Input)\n"
        source_path = ""

    print "This is the Source Name: " + input_file_or_stream

    if input_type == "file":
        out_filename = input_file_or_stream[0:input_file_or_stream.find(".")] + ".xml" # for file input
        out_filename2 = input_file_or_stream[0:input_file_or_stream.find(".")] + "T.xml" # Creates **T.xml for tokenizer ref file
    else:
        out_filename = input_file_or_stream + ".xml" # for directory input...
        out_filename2 = input_file_or_stream + "T.xml" # for Creates **T.xml for tokenizer ref file

    # Open the out_file(s)
    out_file = open(out_filename, 'w') # Main file
    print "Writing the Destination File (.xml): " + out_filename + "\n"
    out_file2 = open(out_filename2, 'w') # Opens the tokenizer ref file
    

    # Get date/time stamp
    from time import localtime, strftime
    temp = strftime("%a, %d, %b, %Y, %X", localtime())

    # Write headers into out_file(s)
    out_file.write("<!-- \nJACK ANALYZED\nSOURCE CODE FROM: " + input_file_or_stream + "\nINPUT TYPE: " + input_type + "\nON: " + temp + "\n-->\n\n")
    out_file2.write("<!-- \nJACK ANALYZED\nSOURCE CODE FROM: " + input_file_or_stream + "\nINPUT TYPE: " + input_type + "\nON: " + temp + "\n-->\n\n") # tokenizer ref file

    # Process file(s)...
    if input_type == "file":
        processFile(input_file_or_stream, out_file)
    if input_type == "directory":
        import glob
        files = glob.glob(source_path)
        for file in files:
            processFile(file,out_file)

    # Close main out_file
    out_file.write("\n<!-- \nEND OF FILE\n-->")
    out_file.close()
    print "\n----------------------------\n** JACK ANALYZER Complete **"

    # Close tokenizer ref file
    out_file2.write("</tokens>\n") # Write footer
    out_file2.write("\n<!-- \nEND OF FILE\n-->")
    out_file2.close()

    return


def processFile(source_file, out_file):
    
    # Import global variables since they are being modified within this routing and not 'read-only'
    global tokenizedSource, currentPos, currentToken, currentTokenType
    
    print "Processing: " + source_file + "\n"
 
    # Write tokenizer ref file header
    out_file2.write("<tokens>\n")
 
    tokenizedSource = tokenizeFile(source_file) # Tokenize the source file
    print "Tokenized Source Code: \n"
    print tokenizedSource
    print "\n--------------------------------------------\n"
    
    # Unit Testing
    while (hasMoreTokens()):
        currentToken = advance()
        currentTokenType = tokenType()
        print "\n\nCurrent Pos = " + str(currentPos - 1) + ", Current Token Type: " + currentTokenType + "\n"
        print "Current Token is: " + currentToken + "\n"

        if currentTokenType == "KEYWORD":
            temp = keyWord()
            print "Keyword: ",
            out_file2.write("\t<keyword>" + currentToken + "</keyword>\n") # tokenizer ref file
        
        if currentTokenType == "SYMBOL":
            temp = symbol()
            print "Symbol: ",
            
            # Handle the 3 exceptions for <,<,&
            if currentToken == "<":
                out_file2.write("\t<symbol>&lt;</symbol>\n")
            elif currentToken == ">":
                out_file2.write("\t<symbol>&gt;</symbol>\n")
            elif currentToken == "&":
                out_file2.write("\t<symbol>&amp;</symbol>\n")
            else:
                out_file2.write("\t<symbol>" + currentToken + "</symbol>\n")
                
                
        if currentTokenType == "IDENTIFIER":
            temp = identifier()
            print "Identifier: ",
            out_file2.write("\t<identifier>" + currentToken + "</identifier>\n") # tokenizer ref file
        
        if currentTokenType == "INT_CONST":
            temp = str(intVal())
            print "Integer Constant: ",
            out_file2.write("\t<integerConstant>" + currentToken + "</integerConstant>\n") # tokenizer ref file
        
        if currentTokenType == "STRING_CONST":
            temp = stringVal()
            print "String Constant: ",
            out_file2.write("\t<stringConstant>" + currentToken + "</stringConstant>\n") # tokenizer ref file
        
        print temp + "\n"

    # This is not needed, should just call the complilatonEngineConstructor() when removing unit testing
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
        out_file.write(stringToExport)
    
        incrementTab()
        
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)
        
        performBasicCheck()
            
        # Write className
        if currentTokenType == "IDENTIFIER":
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)

            performBasicCheck()
            
            # Write {
            if ((currentTokenType == "SYMBOL") & (currentToken == "{")):
                stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n\n" # DELETE EXTRA LINE BREAK
                out_file.write(stringToExport)
                        
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
                    stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                    out_file.write(stringToExport)

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
        stringToExport = tabInsert() + "</class>\n\n" # DELETE EXTRA LINE BREAK
        out_file.write(stringToExport)

    else:
        print "E5"
        error()

    return


def compileClassVarDec():

    print "compileClassVarDec()\n"
    
    # Write classVarDec header
    stringToExport = tabInsert() + "<classVarDec>\n"
    out_file.write(stringToExport)
    
    incrementTab()
    
    if ((currentTokenType == "KEYWORD") & ((currentToken == "static") | (currentToken == "field"))):
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)
        
        performBasicCheck()
        
        # Write type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
            stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
            out_file.write(stringToExport)
        
        elif ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)
        
        else:
            print "E6"
            error()
    
        performBasicCheck()
        
        # Write varName
        if ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)

        else:
            print "E7"
            error()
        
        performBasicCheck()
    
        # Loop to write multiple varNames
        while ((currentTokenType == "SYMBOL") & (currentToken == ",")):
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
        
            performBasicCheck()
        
            # Write varName
            if ((currentTokenType == "IDENTIFIER")):
                stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
                out_file.write(stringToExport)
            
            else:
                print "E8"
                error()
                    
            performBasicCheck()
        
        # Writing a ; statement close
        if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)

        else:
            print "E9"
            error()

        decrementTab()

        # Write classVarDec footer
        stringToExport = tabInsert() + "</classVarDec>\n\n" # DELETE EXTRA LINE BREAK
        out_file.write(stringToExport)
    
    else:
        print "E10"
        error()

    return


def compileSubroutine():
    
    print "compileSubroutine()\n"
    
    # Write subroutineDec header
    stringToExport = tabInsert() + "<subroutineDec>\n"
    out_file.write(stringToExport)
    
    incrementTab()
    
    if ((currentTokenType == "KEYWORD") & ((currentToken == "function") | (currentToken == "method") | (currentToken == "constructor"))):
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)
    
        performBasicCheck()
    
        # Write return type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean") | (currentToken == "void"))):
            stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
            out_file.write(stringToExport)
 
        elif ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)

        else:
            print "E11"
            error()
                
        performBasicCheck()
            
        # Write subroutineName
        if ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)
  
        else:
            print "E12"
            error()
                
        performBasicCheck()
            
        # Write (
        if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)

            performBasicCheck()

            compileParameterList()
            
            # Write )
            if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
                stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                out_file.write(stringToExport)
                
                # Write subroutineBody header
                stringToExport = tabInsert() + "<subroutineBody>\n"
                out_file.write(stringToExport)

                performBasicCheck()
            
                # Write {
                if ((currentTokenType == "SYMBOL") & (currentToken == "{")):
                    incrementTab()
                    stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                    out_file.write(stringToExport)
            
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
                        stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                        out_file.write(stringToExport)
                    
                        # Write subroutineBody footer
                        decrementTab()
                        stringToExport = tabInsert() + "</subroutineBody>\n"
                        out_file.write(stringToExport)

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
    stringToExport = tabInsert() + "</subroutineDec>\n\n" # DELETE EXTRA LINE BREAK
    out_file.write(stringToExport)
    
    return


def compileParameterList():
    
    print "compileParameterList()\n"

    # Write parameterList header
    stringToExport = tabInsert() + "<parameterList>\n"
    out_file.write(stringToExport)
    
    # Found an empty parameterList
    if ((currentTokenType == "SYMBOL") & (currentToken == ")")):

        # Write parameterList footer
        stringToExport = tabInsert() + "</parameterList>\n"
        out_file.write(stringToExport)

        return

    else:
        
        # Write parameter type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
            incrementTab()
            stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
            out_file.write(stringToExport)

        elif ((currentTokenType == "IDENTIFIER")):
            incrementTab()
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)

        else:
            print "E19"
            error()

        performBasicCheck()
            
        # Write parameter varName
        if ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)

        else:
            print "E20"
            error()

        performBasicCheck()

        # Loop to write multiple parameter varNames
        while ((currentTokenType == "SYMBOL") & (currentToken == ",")):

            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
            
            performBasicCheck()

            # Write parameter type
            if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
                stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
                out_file.write(stringToExport)
        
            elif ((currentTokenType == "IDENTIFIER")):
                stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
                out_file.write(stringToExport)
        
            else:
                print "E21"
                error()
                    
            performBasicCheck()
                
            # Write parameter varName
            if ((currentTokenType == "IDENTIFIER")):
                stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
                out_file.write(stringToExport)

            else:
                print "E22"
                error()
            
            performBasicCheck()
    
        # Write parameterList footer
        decrementTab()
        stringToExport = tabInsert() + "</parameterList>\n"
        out_file.write(stringToExport)

        return


def compileVarDec():
    
    print "compileVarDec()\n"
    
    # Write varDec header
    stringToExport = tabInsert() + "<varDec>\n"
    out_file.write(stringToExport)
    
    if ((currentTokenType == "KEYWORD") & (currentToken == "var")):
        incrementTab()
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)
        
        performBasicCheck()
    
        # Write varDec type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
            stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
            out_file.write(stringToExport)

        elif ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)

        else:
            print "E23"
            error()
        
        performBasicCheck()
        
        # Write varDec varName
        if ((currentTokenType == "IDENTIFIER")):
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)
        
        else:
            print "E24"
            error()
    
        performBasicCheck()
        
        # Loop to write multiple varNames
        while ((currentTokenType == "SYMBOL") & (currentToken == ",")):
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
            
            performBasicCheck()
            
            # Write varName
            if ((currentTokenType == "IDENTIFIER")):
                stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
                out_file.write(stringToExport)
            else:
                print "E25"
                error()
            
            performBasicCheck()
        
        # Writing a ; statement close
        if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
        else:
            print "E26"
            error()
    else:
        print "E27"
        error()
    
    # Write varDec footer
    decrementTab()
    stringToExport = tabInsert() + "</varDec>\n"
    out_file.write(stringToExport)
    
    return


def compileStatements():
    
    print "compileStatements()\n"
    
    # Write compileStatements header
    stringToExport = tabInsert() + "<statements>\n"
    out_file.write(stringToExport)
    
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
    out_file.write(stringToExport)

    return


def compileDo():
    
    print "compileDo()\n"
    
    # Write compileDo header
    stringToExport = tabInsert() + "<doStatement>\n"
    out_file.write(stringToExport)
    
    incrementTab()
    
    # Write do keyword
    if ((currentTokenType == "KEYWORD") & (currentToken == "do")):
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)
    
        performBasicCheck()
    
        # Found a subroutineCall
        if (currentTokenType == "IDENTIFIER"):
            lookAhead = tokenizedSource[currentPos] # Not currentPos + 1 due to advance() counting...
    
            if ((lookAhead == "(") | (lookAhead == ".")):
            # Writing a subroutineName/className/varName
                stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
                out_file.write(stringToExport)
            
                performBasicCheck()

                # Write a . symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == ".")):
                    stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                    out_file.write(stringToExport)
                
                    performBasicCheck()
                
                    # Write a subroutineName
                    stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
                    out_file.write(stringToExport)
                
                    performBasicCheck()
        
        
                # Writing ( symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
                    stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                    out_file.write(stringToExport)
                
                    performBasicCheck()
                
                    # Write expressionList
                    compileExpressionList()
                
                    # Write ) symbol
                    if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
                        stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                        out_file.write(stringToExport)
                    
                        performBasicCheck()
                        
                        # Write ; end of statement
                        if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
                            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                            out_file.write(stringToExport)
                        
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
    out_file.write(stringToExport)
    
    return


def compileLet():
    
    print "compileLet()\n"
    
    # Write compileLet header
    stringToExport = tabInsert() + "<letStatement>\n"
    out_file.write(stringToExport)
    
    incrementTab()
    
    # Write let keyword
    if ((currentTokenType == "KEYWORD") & (currentToken == "let")):
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)
        
        performBasicCheck()
    
        # Write varName
        if (currentTokenType == "IDENTIFIER"):
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)
        
            performBasicCheck()
            
            # Found an expression/array & write [ symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == "[")):
                stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                out_file.write(stringToExport)
            
                performBasicCheck()
            
                # Write expression
                compileExpression()
                
                # Write ] symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == "]")):
                    stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                    out_file.write(stringToExport)
                
                    performBasicCheck()
        
        
            # Write = symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == "=")):
                stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                out_file.write(stringToExport)
            
                performBasicCheck()
            
                # Compile expression
                compileExpression()
            
                # Write ; end of statement
                if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
                    stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                    out_file.write(stringToExport)
                
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
    out_file.write(stringToExport)
    
    return


def compileWhile():

    print "compileWhile()\n"

    # Write compileWhile header
    stringToExport = tabInsert() + "<whileStatement>\n"
    out_file.write(stringToExport)

    incrementTab()
    
    # Write while keyword
    if ((currentTokenType == "KEYWORD") & (currentToken == "while")):
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)
        
        performBasicCheck()
    
        # Write ( symbol
        if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
        
            performBasicCheck()
        
            # Write expression
            compileExpression()
        
            # Write ) symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
                stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                out_file.write(stringToExport)
            
                performBasicCheck()
            
                # Write { symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == "{")):
                    stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                    out_file.write(stringToExport)
                
                    performBasicCheck()
                
                    # Write statement(s)
                    compileStatements()
                
                    # Write } symbol
                    if ((currentTokenType == "SYMBOL") & (currentToken == "}")):
                        stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                        out_file.write(stringToExport)
                    
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
    out_file.write(stringToExport)
    
    return


def compileReturn():
    
    print "compileReturn()\n"
    
    # Write compileReturn header
    stringToExport = tabInsert() + "<returnStatement>\n"
    out_file.write(stringToExport)
    
    # Write return keyword
    if ((currentTokenType == "KEYWORD") & (currentToken == "return")):
        incrementTab()
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)
    
    performBasicCheck()

    while not currentToken == ";":
        compileExpression()

    # Write ; end of statement
    if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
        stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
        out_file.write(stringToExport)
        
    else:
        print "E44"
        error()

    # Write compileReturn footer
    decrementTab()
    stringToExport = tabInsert() + "</returnStatement>\n"
    out_file.write(stringToExport)
    
    return


def compileIf():

    print "compileIf()\n"
    
    # Write compileIf header
    stringToExport = tabInsert() + "<ifStatement>\n"
    out_file.write(stringToExport)
    
    incrementTab()
    
    # Write if keyword
    if ((currentTokenType == "KEYWORD") & (currentToken == "if")):
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)
        
        performBasicCheck()
        
        # Write ( symbol
        if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
            
            performBasicCheck()
            
            # Write expression
            compileExpression()
            
            # Write ) symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
                stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                out_file.write(stringToExport)
                
                performBasicCheck()
                
                # Write { symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == "{")):
                    stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                    out_file.write(stringToExport)
                    
                    performBasicCheck()
                    
                    # Write statement(s)
                    compileStatements()
                    
                    # Write } symbol
                    if ((currentTokenType == "SYMBOL") & (currentToken == "}")):
                        stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                        out_file.write(stringToExport)
                        
                        performBasicCheck()
                    
                        # Check if there's an additional else statement...
                        if ((currentTokenType == "KEYWORD") & (currentToken == "else")):
                            stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
                            out_file.write(stringToExport)
                        
                            performBasicCheck()
                        
                            # Write { symbol
                            if ((currentTokenType == "SYMBOL") & (currentToken == "{")):
                                stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                                out_file.write(stringToExport)
        
                                performBasicCheck()
                
                                # Write statement(s)
                                compileStatements()
                    
                                # Write } symbol
                                if ((currentTokenType == "SYMBOL") & (currentToken == "}")):
                                    stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                                    out_file.write(stringToExport)
                        
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
    out_file.write(stringToExport)

    return


def compileExpression():
    
    print "compileExpression()\n"
    
    # Write compileExpression header
    stringToExport = tabInsert() + "<expression>\n"
    out_file.write(stringToExport)
    
    incrementTab()

    compileTerm()
    
    # Write an Op
    if ((currentTokenType == "SYMBOL") & ((currentToken == "+") | (currentToken == "-") | (currentToken == "*") | (currentToken == "/") | (currentToken == "&") | (currentToken == "|") | (currentToken == "<") | (currentToken == ">") | (currentToken == "="))):
        # Account for the 3 op XML exceptions, <,>,&
        if currentToken == "<":
            stringToExport = tabInsert() + "<symbol>&lt;</symbol>\n"
            out_file.write(stringToExport)
        elif currentToken == ">":
            stringToExport = tabInsert() + "<symbol>&gt;</symbol>\n"
            out_file.write(stringToExport)
        elif currentToken == "&":
            stringToExport = tabInsert() + "<symbol>&amp;</symbol>\n"
            out_file.write(stringToExport)
        else:
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
                
        performBasicCheck()
        
        # Write a second term
        compileTerm()
    
    decrementTab()

    # Write compileExpression footer
    stringToExport = tabInsert() + "</expression>\n"
    out_file.write(stringToExport)

    return


def compileTerm():
    
    print "compileTerm()\n"
    
    # Write compileTerm header
    stringToExport = tabInsert() + "<term>\n"
    out_file.write(stringToExport)
    
    incrementTab()
    
    # Analyze the term components...

    # Found an integerConstant...
    if currentTokenType == "INT_CONST":
        stringToExport = tabInsert() + "<integerConstant>" + currentToken + "</integerConstant>\n"
        out_file.write(stringToExport)
    
        performBasicCheck()

    # Found a stringConstant...
    elif currentTokenType == "STRING_CONST":
        stringToExport = tabInsert() + "<stringConstant>" + currentToken.strip("\"") + "</stringConstant>\n"
        out_file.write(stringToExport)

        performBasicCheck()
    
    # Found a keywordConstant...
    elif ((currentTokenType == "KEYWORD") & ((currentToken == "true") | (currentToken == "false") | (currentToken == "null") | (currentToken == "this"))):
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)

        performBasicCheck()

    # Found a unaryOp term
    elif ((currentTokenType == "SYMBOL") & ((currentToken == "-") | (currentToken == "~"))):
        stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
        out_file.write(stringToExport)

        performBasicCheck()

        compileTerm()

    # Found an Identifier...
    elif (currentTokenType == "IDENTIFIER"):
        lookAhead = tokenizedSource[currentPos] # Not currentPos + 1 due to advance() counting...
        
        # Found a varName[array]
        if lookAhead == "[":
            # Writing the varName
            stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
            out_file.write(stringToExport)
        
            performBasicCheck()
        
            if ((currentTokenType == "SYMBOL") & (currentToken == "[")):
                
                # Writing [ symbol
                stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                out_file.write(stringToExport)
                
                performBasicCheck()
                
                # Writing the expression...
                incrementTab()
                compileExpression()
                decrementTab()
                
                if ((currentTokenType == "SYMBOL") & (currentToken == "]")):
                    # Writing ] symbol
                    stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                    out_file.write(stringToExport)
                
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
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)

            performBasicCheck()
            
            # Write a . symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == ".")):
                stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                out_file.write(stringToExport)
            
                performBasicCheck()
            
                # Write a subroutineName
                stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
                out_file.write(stringToExport)
            
                performBasicCheck()
            

            # Writing ( symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
                stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                out_file.write(stringToExport)
                
                performBasicCheck()
                
                # Write expressionList
                compileExpressionList()

                # Writing ) symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
                    stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                    out_file.write(stringToExport)
        
                    performBasicCheck()
                
                else:
                    print "E54"
                    error()
            else:
                print "E55"
                error()


        # Found a varName
        elif ((lookAhead != "(") & (lookAhead != ".")):
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)
        
            performBasicCheck()

        else:
            print "E56"
            error()


    # Found an (expression)...
    elif ((currentTokenType == "SYMBOL") & (currentToken == "(")):
        stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
        out_file.write(stringToExport)

        performBasicCheck()

        compileExpression()
        
        if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
        
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
    out_file.write(stringToExport)

    return


def compileExpressionList():
    
    print "compileExpressionList()\n"
    
    # Write expressionList header
    stringToExport = tabInsert() + "<expressionList>\n"
    out_file.write(stringToExport)
    
    incrementTab()
    
    if not ((currentTokenType == "SYMBOL") & (currentToken == ")")):
        
        compileExpression()
    
        # Loop to write multiple expressions
        while ((currentTokenType == "SYMBOL") & (currentToken == ",")):
        
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
            
            performBasicCheck()
            
            compileExpression()

    decrementTab()

    # Write expressionList footer
    stringToExport = tabInsert() + "</expressionList>\n"
    out_file.write(stringToExport)
    
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
