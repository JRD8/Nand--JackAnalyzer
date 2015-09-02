################################
####### JRD JACK ANALYZER ######
################################

## JACK TOKENIZER MODULE ##


def main():
    
    # Import Jack file form command line script
    from sys import argv
    print "JRD Nand-2-Tetris Jack Analyzer, 2015\n"
    print "Enter the Source Jack File (.jack) or Source Jack Directory (within this path) to be analyzed:"
    #source_input = raw_input(">") # User inputs source...
    source_input = "test.jack" # Uncomment to test without user input
    
    ## These are the test Jack files.  Uncomment to substitute for source_input ##
    #...
    
    print "\nThis is the Source: " + source_input
    
    constructor(source_input)

    return


def constructor(input_file_or_stream):
    
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
    print "** JACK ANALYZER Complete"

    return


def processFile(source_file, out_file):
    
    print "Processing: " + source_file + "\n"
    out_file.write("<!--\nSOURCE JACK CODE FOR: " + source_file + "\n-->\n\n")
    
    tokenizedSource = tokenizeFile(source_file) # Tokenize the source file
    print tokenizedSource
    print "\n"
    
    return

def tokenizeFile(source_file):
    
    firstStep = open(source_file, "r")
    firstPass = firstStep.read()
    print firstPass

    # Remove \n carriage returns
    secondPass = firstPass.split("\n")
    print secondPass
    print "\n"
    
    # remove // Comment lines
    thirdPass = []
    for e in secondPass:
        if (e.find("//") != 0):
            thirdPass.append(e)
    print thirdPass
    print "\n"

    # remove \r and \t\r elements
    fourthPass = []
    for e in thirdPass:
        if ((e != "\r") & (e != "\t\r") & (e != "")):
            fourthPass.append(e)
    print fourthPass
    print "\n"

    # Recombine into single string
    fifthPass = ""
    for e in fourthPass:
        fifthPass = fifthPass + e
    print fifthPass
    print "\n"
    
    # Remove white spaces, tabs
    sixthPass = fifthPass.split()
    print sixthPass
    print "\n"
    
    # Remove /** and /* ... */ comments
    seventhPass = []
    include = True
    i = 0
    while (i < len(sixthPass)):
        if ((sixthPass[i] == "/**") | (sixthPass[i] == "/*")):
            include = False
        if (include):
            seventhPass.insert(i, sixthPass[i])
        if (sixthPass[i] == "*/"):
            include = True
        i = i + 1
    print seventhPass
    print "\n"

    # Split out the symbol elements
    symbols = ['}', '{', ')', '(', ']', '[', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~', '"']
    temp = seventhPass
    for symbol in symbols:
        newTemp = []
        for e in temp:
            if e.find(symbol) == -1:
                newTemp.append(e)
            else:
                temp = e.split(symbol)
                newTemp.append(temp[0])
                newTemp.append(symbol)
                newTemp.append(temp[1])
        temp = newTemp
    eightPass = []
    for e in temp: # clean out the blank list elements
        if len(e) != 0:
            eightPass.append(e)
    print eightPass
    print "\n"
    
    # TODO Combine String elements into one token

    return eightPass


def hasMoreTokens():
    result = false
    return result


def advance():
    return


def tokenType():
    current_token_type = ""
    return current_token_type


def keyWord():
    current_token_keyword = ""
    return current_token_keyword


def symbol():
    current_token_char = ""
    return current_token_char


def identifier():
    current_token_identifier = ""
    return current_token_identifier


def intVal():
    current_intVal = 0 # Null Int?
    return current_intVal


def stringVal():
    current_stringVal = ""
    return current_stringVal


# Process main routine
main()
