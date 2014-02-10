from __future__ import with_statement
from dtree import *
from id3 import *
import sys
import os.path

def get_filenames():
    """
    Tries to extract the training and test data filenames from the command
    line.  If none are present, it prompts the user for both filenames and
    and makes sure that both exist in the system before returning the names
    back to the calling function.
    """
    # If no filenames were given at the command line, ask for them
    if len(sys.argv) < 3:
        training_filename = raw_input("Training Filename: ")
        test_filename = raw_input("Test Filename: ")
        module_filename =raw_input("Module Filename:")
    # otherwise, read the filenames from the command line
    else:
        training_filename = sys.argv[1]
        test_filename = sys.argv[2]
        module_filename = sys.argv[3]

    # This is a local function that takes a filename and returns true or false
    # depending on whether or not the file exists in the system.
    def file_exists(filename):
        if os.path.isfile(filename):
            return True
        else:
            print "Error: The file '%s' does not exist." % filename
            return False

    # Make sure both files exist, otherwise print an error and exit execution
    if ((not file_exists(training_filename)) or
        (not file_exists(test_filename))):
        sys.exit(0)

    # Return the filenames of the training and test data files
    return training_filename, test_filename,module_filename

def get_attributes(filename):
    """
    Parses the attribute names from the header line of the given file.
    """
    # Create a list of all the lines in the training file
    with open(filename, 'r') as fin:
        header = fin.readline().strip()

    # Parse the attributes from the header
    attributes = [attr.strip() for attr in header.split(",")]

    return attributes
    
def get_data(filename, attributes):
    """
    This function takes a file and list of attributes and returns a list of
    dict objects that represent each record in the file.
    """
    # Create a list of all the lines in the training file
    with open(filename) as fin:
        lines = [line.strip() for line in fin.readlines()]

    # Remove the attributes line from the list of lines
    del lines[0]

    # Parse all of the individual data records from the given file
    data = []
    for line in lines:
        data.append(dict(zip(attributes,
                             [datum.strip() for datum in line.split(",")])))
    
    return data
    
def print_tree(tree, str,module):
    """
        This function recursively crawls through the d-tree and prints it out in a
        more readable format than a straight print of the Python dict object.
        """

    if type(tree) == dict:
        for item in tree.values()[0].keys():
            module.write("%s%s" % (str,tree.keys()[0])+"= %s:" % (item))
            print_tree(tree.values()[0][item],str+"| ",module)

    else:
        module.write("%s"%(tree))
   
    

if __name__ == "__main__":
    # Get the training and test data filenames from the user
    training_filename, test_filename,module_filename = get_filenames()
    Info = {}
    # Extract the attribute names and the target attribute from the training
    # data file.
    attributes = get_attributes(training_filename)
    
    target_attr = attributes[-1]

    # Get the training and test data from the given files
    training_data = get_data(training_filename, attributes)
    test_data = get_data(test_filename, attributes)
    print(len(training_data))
    print(len(test_data))
    for attr in attributes:
        print(attr)
        Info[attr]=gain(training_data,attr,target_attr)
        print(Info[attr])
    print(len(attributes))
    # Create the decision tree
    chi_square = ChiSquareTest(6.635)
    dtree = create_decision_tree(training_data, attributes, target_attr, gain,chi_square)

    # Classify the records in the test data
    classification = classify(dtree, test_data)
    count1 = 0
    count2 = 0
    for item in classification:
        #print item
        count1 = count1+1
    for i in range(1,count1):
        if(cmp(classification[i],test_data[i][attributes[-1]])==0):
            count2 = count2 +1
    print "------------------------\n"
    print("the accuracy of the decision tree using Entropy on test data is:")
    print(float(count2)/count1)
    
    module_data = open(module_filename,'w')
    print_tree(dtree," \n",module_data)
    module_data.close()
