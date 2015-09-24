################################
####### JRD JACK ANALYZER ######
################################

## JACK TOKENIZER MODULE ##

# Global variable declarations
currentPos = 0
currentToken = ""
currentTokenType = ""
out_file = ""
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
    source_input = "UnitTest.jack" # Uncomment to test without user input
    
    ## These are the test Jack files.  Uncomment to substitute for source_input ##
    #...
    
    print "\nThis is the Source: " + source_input
    
    jackTokenizerConstructor(source_input)

    return


def jackTokenizerConstructor(input_file_or_stream):
    
    global out_file
    
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
    else:
        out_filename = input_file_or_stream + ".xml" # for directory input...

    # Open the out_file
    out_file = open(out_filename, 'w')
    print "Writing the Destination File (.xml): " + out_filename + "\n"

    # Get date/time stamp
    from time import localtime, strftime
    temp = strftime("%a, %d, %b, %Y, %X", localtime())

    # Write comment header into out_file
    out_file.write("<!-- \nJACK ANALYZED\nFROM: " + input_file_or_stream + "\nINPUT TYPE: " + input_type + "\nON: " + temp + "\n-->\n\n")

    # Process file(s)...
    if input_type == "file":
        processFile(input_file_or_stream, out_file)
    if input_type == "directory":
        import glob
        files = glob.glob(source_path)
        for file in files:
            processFile(file,out_file)

    # Close the out_file
    out_file.write("\n<!-- \nEND OF FILE\n-->")
    out_file.close()
    print "\n----------------------------\n** JACK ANALYZER Complete **"

    return


def processFile(source_file, out_file):
    
    # Import global variables since they are being modified within this routing and not 'read-only'
    global tokenizedSource, currentPos, currentToken, currentTokenType
    
    print "Processing: " + source_file + "\n"
    out_file.write("<!--\nSOURCE JACK CODE FOR: " + source_file + "\n-->\n\n")
    
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
        if currentTokenType == "SYMBOL":
            temp = symbol()
            print "Symbol: ",
        if currentTokenType == "IDENTIFIER":
            temp = identifier()
            print "Identifier: ",
        if currentTokenType == "INT_CONST":
            temp = str(intVal())
            print "Integer Constant: ",
        if currentTokenType == "STRING_CONST":
            temp = stringVal()
            print "String Constant: ",
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
            print stringToExport

            performBasicCheck()
            
            # Write {
            if ((currentTokenType == "SYMBOL") & (currentToken == "{")):
                stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n\n" # DELETE EXTRA LINE BREAK
                out_file.write(stringToExport)
                print stringToExport
                        
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
                        error()
                        
                    performBasicCheck()

                # End Recursion...
                
                # Write }
                if ((currentTokenType == "SYMBOL") & (currentToken == "}")):
                    stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                    out_file.write(stringToExport)
                    print stringToExport
                else:
                    error()
            else:
                error()
        else:
            error()

        # Write class footer
        decrementTab()
        stringToExport = tabInsert() + "</class>\n\n" # DELETE EXTRA LINE BREAK
        out_file.write(stringToExport)

    else:
        error()

    return


def compileClassVarDec():

    print "compileClassVarDec"
    
    # Write classVarDec header
    stringToExport = tabInsert() + "<classVarDec>\n"
    out_file.write(stringToExport)
    
    if ((currentTokenType == "KEYWORD") & ((currentToken == "static") | (currentToken == "field"))):
        incrementTab()
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)
        print stringToExport
        
        performBasicCheck()
        
        # Write type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
            print "Writing an int/char/boolean"
            stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
            out_file.write(stringToExport)
            print stringToExport
        elif ((currentTokenType == "IDENTIFIER")):
            print "Writing className"
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)
            print stringToExport
        else:
            error()
    
        performBasicCheck()
        
        # Write varName
        if ((currentTokenType == "IDENTIFIER")):
            print "Writing varName"
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)
            print stringToExport

        else:
            error()
        
        performBasicCheck()
    
        # Loop to write multiple varNames
        while ((currentTokenType == "SYMBOL") & (currentToken == ",")):
            print "Writing a , multiple varName"
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
            print stringToExport
        
            performBasicCheck()
        
            # Write varName
            if ((currentTokenType == "IDENTIFIER")):
                print "Writing varName"
                stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
                out_file.write(stringToExport)
                print stringToExport
            else:
                error()
                    
            performBasicCheck()
        
        # Writing a ; statement close
        if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
            print "Writing a ; statement close"
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
            print stringToExport
        else:
            error()
    
        # Write classVarDec footer
        decrementTab()
        stringToExport = tabInsert() + "</classVarDec>\n\n" # DELETE EXTRA LINE BREAK
        out_file.write(stringToExport)
        print stringToExport
    
    else:
        error()

    return


def compileSubroutine():
    print "compileSubroutine"
    
    # Write subroutineDec header
    stringToExport = tabInsert() + "<subroutineDec>\n"
    out_file.write(stringToExport)
    print stringToExport
    
    if ((currentTokenType == "KEYWORD") & ((currentToken == "function") | (currentToken == "method") | (currentToken == "constructor"))):
        incrementTab()
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)
        print stringToExport
    
        performBasicCheck()
    
        # Write return type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean") | (currentToken == "void"))):
            print "Writing a int/boolean/char/void return type"
            stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
            out_file.write(stringToExport)
            print stringToExport
        elif ((currentTokenType == "IDENTIFIER")):
            print "Writing a className return type"
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)
            print stringToExport
        else:
            error()
                
        performBasicCheck()
            
        # Write subroutineName
        if ((currentTokenType == "IDENTIFIER")):
            print "Writing subroutineName"
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)
            print stringToExport
        else:
            error()
                
        performBasicCheck()
            
        # Write (
        if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
            print stringToExport

            performBasicCheck()

            compileParameterList()
            
            # Write )
            if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
                stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                out_file.write(stringToExport)
                print stringToExport
                
                # Write subroutineBody header
                stringToExport = tabInsert() + "<subroutineBody>\n"
                out_file.write(stringToExport)
                print stringToExport

                performBasicCheck()
            
                # Write {
                if ((currentTokenType == "SYMBOL") & (currentToken == "{")):
                    incrementTab()
                    stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                    out_file.write(stringToExport)
                    print stringToExport
            
                    # Begin recursion for subroutineBody...
                    performBasicCheck()
            
                    # Loop to find either a varDec or a Statement initial keyword
                    while (currentToken != "}"):
                        
                        if ((currentTokenType == "KEYWORD") & (currentToken == "var")):
                            compileVarDec()
                        elif ((currentTokenType == "KEYWORD") & ((currentToken == "let") | (currentToken == "if") | (currentToken == "while") | (currentToken == "do") | (currentToken == "return"))):
                            compileStatements()
                        else:
                            error()
                                
                        performBasicCheck ()
                    
                    # Write }
                    if ((currentTokenType == "SYMBOL") & (currentToken == "}")):
                        stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                        out_file.write(stringToExport)
                        print stringToExport
                    
                        # Write subroutineBody footer
                        decrementTab()
                        stringToExport = tabInsert() + "</subroutineBody>\n"
                        out_file.write(stringToExport)
                        print stringToExport

                    else:
                        error()
                else:
                    error()
            else:
                error()
        else:
            error()
    else:
        error()
    
    # Write subroutineDec footer
    decrementTab()
    stringToExport = tabInsert() + "</subroutineDec>\n\n" # DELETE EXTRA LINE BREAK
    out_file.write(stringToExport)
    print stringToExport
    
    return


def compileParameterList():
    
    print "compileParameterList"

    # Write parameterList header
    stringToExport = tabInsert() + "<parameterList>\n"
    out_file.write(stringToExport)
    print stringToExport
    
    # Found an empty parameterList
    if ((currentTokenType == "SYMBOL") & (currentToken == ")")):

        # Write parameterList footer
        stringToExport = tabInsert() + "</parameterList>\n"
        out_file.write(stringToExport)
        print stringToExport

        return

    else:
        
        # Write parameter type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
            print "Writing a int/boolean/char parameter type"
            incrementTab()
            stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
            out_file.write(stringToExport)
            print stringToExport

        elif ((currentTokenType == "IDENTIFIER")):
            print "Writing a className parameter type"
            incrementTab()
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)
            print stringToExport

        else:
            error()

        performBasicCheck()
            
        # Write parameter varName
        if ((currentTokenType == "IDENTIFIER")):
            print "Writing varName"
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)
            print stringToExport

        else:
            error()

        performBasicCheck()

        # Loop to write multiple parameter varNames
        while ((currentTokenType == "SYMBOL") & (currentToken == ",")):

            print "Writing a , multiple varName"
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
            print stringToExport
            
            performBasicCheck()

            # Write parameter type
            if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
                print "Writing a int/boolean/char parameter type"
                stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
                out_file.write(stringToExport)
                print stringToExport
        
            elif ((currentTokenType == "IDENTIFIER")):
                print "Writing a className parameter type"
                stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
                out_file.write(stringToExport)
                print stringToExport
        
            else:
                error()
                    
            performBasicCheck()
                
            # Write parameter varName
            if ((currentTokenType == "IDENTIFIER")):
                print "Writing varName"
                stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
                out_file.write(stringToExport)
                print stringToExport

            else:
                error()
            
            performBasicCheck()
    
        # Write parameterList footer
        decrementTab()
        stringToExport = tabInsert() + "</parameterList>\n"
        out_file.write(stringToExport)
        print stringToExport

        return


def compileVarDec():
    
    print "compileVarDec"
    
    # Write varDec header
    stringToExport = tabInsert() + "<varDec>\n"
    out_file.write(stringToExport)
    print stringToExport
    
    if ((currentTokenType == "KEYWORD") & (currentToken == "var")):
        incrementTab()
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)
        print stringToExport
        
        performBasicCheck()
    
        # Write varDec type
        if ((currentTokenType == "KEYWORD") & ((currentToken == "int") | (currentToken == "char") | (currentToken == "boolean"))):
            print "Writing an int/char/boolean"
            stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
            out_file.write(stringToExport)
            print stringToExport
        elif ((currentTokenType == "IDENTIFIER")):
            print "Writing className"
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)
            print stringToExport
        else:
            error()
        
        performBasicCheck()
        
        # Write varDec varName
        if ((currentTokenType == "IDENTIFIER")):
            print "Writing varDec varName"
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)
            print stringToExport
        
        else:
            error()
    
        performBasicCheck()
        
        # Loop to write multiple varNames
        while ((currentTokenType == "SYMBOL") & (currentToken == ",")):
            print "Writing a , multiple varName"
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
            print stringToExport
            
            performBasicCheck()
            
            # Write varName
            if ((currentTokenType == "IDENTIFIER")):
                print "Writing varName"
                stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
                out_file.write(stringToExport)
                print stringToExport
            else:
                error()
            
            performBasicCheck()
        
        # Writing a ; statement close
        if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
            print "Writing a ; statement close"
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
            print stringToExport
        else:
            error()
    else:
        error()
    
    # Write varDec footer
    decrementTab()
    stringToExport = tabInsert() + "</varDec>\n"
    out_file.write(stringToExport)
    print stringToExport
    
    return


def compileStatements():
    
    print "compileStatements"
    
    # Write compileStatements header
    stringToExport = tabInsert() + "<statements>\n"
    out_file.write(stringToExport)
    print stringToExport
    
    while ((currentTokenType != "SYMBOL") & (currentToken != "}")):
        
        incrementTab()
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
            error()
        decrementTab()
              
        performBasicCheck()
    
    # Write compileStatements footer
    stringToExport = tabInsert() + "</statements>\n"
    out_file.write(stringToExport)
    print stringToExport

    return


def compileDo():
              
    print "compile do"
    return


def compileLet():
    print "compile let"
    return


def compileWhile():
    print "compile while"
    return


def compileReturn():
    print "compile return"
    
    # Write compileReturn header
    stringToExport = tabInsert() + "<returnStatement>\n"
    out_file.write(stringToExport)
    print stringToExport
    
    if ((currentTokenType == "KEYWORD") & (currentToken == "return")):
        incrementTab()
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)
        print stringToExport
    
    performBasicCheck()

    while not currentToken == ";":
        print "current token" + currentToken
        compileExpression()

    # Writing a ; statement close
    if ((currentTokenType == "SYMBOL") & (currentToken == ";")):
        print "Writing a ; statement close"
        stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
        out_file.write(stringToExport)
        print stringToExport
    else:
        error()

    # Write compileReturn header
    decrementTab()
    stringToExport = tabInsert() + "</returnStatement>\n"
    out_file.write(stringToExport)
    print stringToExport
    
    return


def compileIf():
    print "compile if"
    return


def compileExpression():
    print "compile expression"
    
    # Write compileExpression header
    stringToExport = tabInsert() + "<expression>\n"
    out_file.write(stringToExport)
    print stringToExport
    
    print "currentToken = " + currentToken
    incrementTab()
    compileTerm()
    
    performBasicCheck()
    
    # Write an Op
    if ((currentTokenType == "SYMBOL") & ((currentToken == "+") | (currentToken == "-") | (currentToken == "*") | (currentToken == "/") | (currentToken == "&") | (currentToken == "|") | (currentToken == "<") | (currentToken == ">") | (currentToken == "="))):
        # Account for the 3 op XML exceptions, <,>,&
        if currentToken == "<":
            stringToExport = tabInsert() + "<symbol>&lt</symbol>\n"
            out_file.write(stringToExport)
        elif currentToken == ">":
            stringToExport = tabInsert() + "<symbol>&gt</symbol>\n"
            out_file.write(stringToExport)
        elif currentToken == "&":
            stringToExport = tabInsert() + "<symbol>&amp</symbol>\n"
            out_file.write(stringToExport)
        else:
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
                
        performBasicCheck()
        
        # Write a second term
        compileTerm()

        performBasicCheck()
    
    decrementTab()

    # Write compileExpression footer
    stringToExport = tabInsert() + "</expression>\n"
    out_file.write(stringToExport)
    print stringToExport

    return


def compileTerm():
    
    # Write compileTerm header
    stringToExport = tabInsert() + "<term>\n"
    out_file.write(stringToExport)
    print stringToExport
    
    incrementTab()
    
    # Analyze the term components...

    # Found an integerConstant...
    if currentTokenType == "INT_CONST":
        print "Writing an Integer Constant"
        stringToExport = tabInsert() + "<integerConstant>" + currentToken + "</integerConstant>\n"
        out_file.write(stringToExport)
        print stringToExport

    # Found a stringConstant...
    elif currentTokenType == "STRING_CONST":
        print "Writing a String Constant"
        stringToExport = tabInsert() + "<stringConstant>" + currentToken.strip("\"") + "</stringConstant>\n"
        out_file.write(stringToExport)
        print stringToExport
    
    # Found a keywordConstant...
    elif ((currentTokenType == "KEYWORD") & ((currentToken == "true") | (currentToken == "false") | (currentToken == "null") | (currentToken == "this"))):
        print "Writing a Keyword Constant"
        stringToExport = tabInsert() + "<keyword>" + currentToken + "</keyword>\n"
        out_file.write(stringToExport)
        print stringToExport

    # Found a unaryOp term
    elif ((currentTokenType == "SYMBOL") & ((currentToken == "-") | (currentToken == "~"))):
        print "Writing a unaryOp term"
        stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
        out_file.write(stringToExport)
        print stringToExport

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
                else:
                    error()
            else:
                error()

        # Found a subroutineCall
        elif ((lookAhead == "(") | (lookAhead == ".")):
            # Writing a subroutineName/className/varName
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)

            performBasicCheck()
            
            if ((currentTokenType == "SYMBOL") & (currentToken == ".")):
                stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                out_file.write(stringToExport)
            
                performBasicCheck()
            
                stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
                out_file.write(stringToExport)
            
                performBasicCheck()
            

            # Writing ( symbol
            if ((currentTokenType == "SYMBOL") & (currentToken == "(")):
                stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                out_file.write(stringToExport)
                
                performBasicCheck()
                
                # Compiling expressionList
                compileExpressionList()

                # Writing ) symbol
                if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
                    stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
                    out_file.write(stringToExport)
                else:
                    error()
            else:
                error()


        # Found a varName
        elif ((lookAhead != "(") & (lookAhead != ".")):
            stringToExport = tabInsert() + "<identifier>" + currentToken + "</identifier>\n"
            out_file.write(stringToExport)

        else:
            error()


    # Found an (expression)...
    elif ((currentTokenType == "SYMBOL") & (currentToken == "(")):
        print "Writing a (expression)"
        stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
        out_file.write(stringToExport)
        print stringToExport

        performBasicCheck()

        compileExpression()
        
        if ((currentTokenType == "SYMBOL") & (currentToken == ")")):
            stringToExport = tabInsert() + "<symbol>" + currentToken + "</symbol>\n"
            out_file.write(stringToExport)
            print stringToExport
        else:
            error()

    else:
        error()
    
    decrementTab()

    # Write compileTerm footer
    stringToExport = tabInsert() + "</term>\n"
    out_file.write(stringToExport)
    print stringToExport

    return


def compileExpressionList():
    
    # Write expressionList header
    stringToExport = tabInsert() + "<expressionList>\n"
    out_file.write(stringToExport)
    print stringToExport
    
    if ((currentTokenType != "SYMBOL") & (currentToken != ")")):
    
        incrementTab()
    
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
    print stringToExport
    
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
        error()
    
    return


def error():
    print "ERROR!"
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
