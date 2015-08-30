################################
####### JRD JACK ANALYZER ######
################################

## JACK TOKENIZER MODULE ##


def main():
    
    # Import Jack file form command line script
    from sys import argv
    print "JRD Nand-2-Tetris Jack Analyzer, 2015\n"
    print "Enter the Source Jack File (.jack) or Source Jack Directory (within this path) to be analyzed:"
    source_input = raw_input(">") # User inputs source...
    
    ## These are the test Jack files.  Uncomment to substitute for source_input ##
    #...
    
    print "\nThis is the Source: " + source_input
    
    if source_input.find(".jack") == -1: # Directory input
        input_type = "directory"
        print "(Source is a Directory Input)\n"
        import os
        script_path = os.path.dirname(ps.path.abspath(__file__))
        source_path = script_path + "/" + source_input + "/*.jack"
        print "Source Path = " + source_path + "\n"
    
    if source_input.find(".jack") != -1:
        input_type = "file"
        print "(Source is a File Input)\n"
        source_path = ""
    
    source_name = source_input
    print "This is the Source Name: " + source_name

    return


def constructor(input_file_or_stream):
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
