from __future__ import with_statement
import math
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
    if len(sys.argv) < 4:
        training_filename = raw_input("Training Filename: ")
        test_filename = raw_input("Test Filename: ")
        beta = raw_input("Beta:")
        module_filename =raw_input("Module Filename:")
    # otherwise, read the filenames from the command line
    else:
        training_filename = sys.argv[1]
        test_filename = sys.argv[2]
        beta = sys.argv[3]
        module_filename = sys.argv[4]
    
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
    
    return training_filename, test_filename,beta,module_filename

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
        dict objects,each dict object is a each recode like 'XB':'1'.
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
    #print data
    return data
def get_baselog(data,attributes,beta):
    #keep track of the number of the class equals to 0
    count0 = 0.0
    #keep track of the number of the class equals to 1
    count1 = 0.0
    #keep track of the number of the attr equals to 0 given class is 1 for each attribute
    count2 = {}
    #keep track of the number of the attr equals to 0 given class is 0 for each attribute
    count3 = {}
    #base log odds
    w0 = 0.0
    
    for record in data:
        if record[attributes[-1]]== '0':
            count0 = count0+1
        else:
            count1 = count1+1
    w0 += math.log((float(count1+float(beta)-1)/(count0+float(beta)-1)))
    
    for attr in attributes:
        count2[attr] = 0.0
        count3[attr] = 0.0

    for record in data:
        if record[attributes[-1]]=='1':
            for attr in attributes:
                if record[attr]=='0':
                    count2[attr] += 1.0
# print attr+":"
#print count2[attr]

    for record in data:
        if record[attributes[-1]]=='0':
            for attr in attributes:
                if record[attr]=='0':
                    count3[attr] += 1.0
#print attr+":"
#print count3[attr]
    

    for attr in attributes[:-1]:
        w0 += math.log((count2[attr]+float(beta)-1)/(count1+float(beta)+float(beta)-2)/(count3[attr]+float(beta)-1)*(count0+float(beta)+float(beta)-2))
    return w0
def get_weights(data,attributes,beta):
    weights = {}
    middle1 = {}
    middle2 = {}
    #keep track of the number of the class equals to 0
    count0 = 0.0
    #keep track of the number of the class equals to 1
    count1 = 0.0
    #keep track of the number of the attr equals to 0 given class is 1 for each attribute
    count2 = {}
    #keep track of the number of the attr equals to 0 given class is 0 for each attribute
    count3 = {}

    for record in data:
        if record[attributes[-1]]== '0':
            count0 = count0+1
        else:
            count1 = count1+1
    for attr in attributes[:-1]:
        count2[attr] = 0.0
        count3[attr] = 0.0
    for record in data:
        if record[attributes[-1]]=='1':
            for attr in attributes[:-1]:
                if record[attr]=='0':
                    count2[attr] += 1.0
    for record in data:
        if record[attributes[-1]]=='0':
            for attr in attributes[:-1]:
                if record[attr]=='0':
                    count3[attr] += 1.0
    for attr in attributes[:-1]:
        middle1[attr] = (count2[attr]+float(beta)-1)/(count1+float(beta)+float(beta)-2)
        middle2[attr] = (count3[attr]+float(beta)-1)/(count0+float(beta)+float(beta)-2)
        weights[attr] = math.log((1-middle1[attr])/(1-middle2[attr]))-math.log(middle1[attr]/middle2[attr])
#print weights[attr]
    return weights

def get_classification(record,attributes,weights,w0):
    classify = w0
    prob = 0.0
    for attr in attributes[:-1]:
        if record[attr] == '1':
            classify += weights[attr]
    prob = 1.0/(1.0+math.exp(-classify))
    return prob

def classify(data,attributes,weights,w0):
    data = data[:]
    classification = []
    for record in data:
        classification.append(get_classification(record,attributes,weights,w0))
    return classification

if __name__ == "__main__":
    # Get the training and test data filenames from the user
    training_filename, test_filename,beta,module_filename = get_filenames()
    # Extract the attribute names and the target attribute from the training
    # data file.
    attributes = get_attributes(training_filename)
    classification = []
    target_attr = attributes[-1]
    result = []
    count = 0
    # Get the training and test data from the given files
    training_data = get_data(training_filename, attributes)
    test_data = get_data(test_filename, attributes)
    #for attr in attributes:
    #print(attr)
    w0 = get_baselog(training_data,attributes,beta)
    weights = get_weights(training_data,attributes,beta)
    classification = classify(test_data,attributes,weights,w0)
    for i in range(len(test_data)):
        print classification[i]
    #calculate the result 1 or 0 given the probabilites
    for i in range(len(test_data)):
        if classification[i] > 0.5:
            result.append('1')
        else:
            result.append('0')
    #compute accuracy
    for i in range(len(test_data)):
        if(cmp(result[i],test_data[i][attributes[-1]])==0):
            count += 1
    print "------------------------\n"
    print("the accuracy is:")
    print(float(count)/len(test_data))
    module_data = open(module_filename,'w')
    module_data.write("%s"%w0+"\n")
    
    for attr in attributes[:-1]:
        module_data.write("%s"%attr+" "+"%s"%weights[attr]+"\n")
    module_data.close()
