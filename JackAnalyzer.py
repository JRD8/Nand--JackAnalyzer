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
    source_input = "test" # Uncomment to test without user input
    
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

    out_file = open(out_filename, 'w')
    print "Writing the Destination File (.xml): " + out_filename + "\n"

    # Get date/time stamp
    from time import localtime, strftime
    temp = strftime("%a, %d, %b, %Y, %X", localtime())

    # Write header as comments
    out_file.write("<!-- \nJACK ANALYZED FROM: " + input_file_or_stream + "\n ON: " + temp + "\n-->\n\n")

    return


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
