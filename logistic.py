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
    if len(sys.argv) < 5:
        training_filename = raw_input("Training Filename: ")
        test_filename = raw_input("Test Filename: ")
        eta = raw_input("eta:")
        sigma = raw_input("sigma:")
        module_filename =raw_input("Module Filename:")
    # otherwise, read the filenames from the command line
    else:
        training_filename = sys.argv[1]
        test_filename = sys.argv[2]
        eta = sys.argv[3]
        sigma = sys.argv[4]
        module_filename = sys.argv[5]
    
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
    
    return training_filename, test_filename,eta,sigma,module_filename

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
    
def get_weights(data,attributes,eta,sigma):
    weights = {}
    weights[0] = 0.0
    dw = {}
    for attr in attributes[:-1]:
        weights[attr] = 0.0
        dw[attr] = 0.0
 
    for record in data:
        record['pr'] = 0.0
        record['middle'] = 0.0
    count = 0
    convergence = 1.0
    while convergence >= 0.00001 and count<100:
        count += 1
        for record in data:
            record['middle'] = weights[0]
            for attr in attributes[:-1]:
                record['middle'] += float(record[attr])*weights[attr]
            #record['pr'] = math.exp(weights[0]+record['middle'])/(1+math.exp(weights[0]+record['middle']))
            record['pr'] = 1.0-1.0/(1+math.exp(record['middle']))
   
        for attr in attributes[:-1]:
            dw[attr] = 0.0
            for record in data:
                dw[attr] += float(record[attr])*(float(record[attributes[-1]])-record['pr'])
            dw[attr] -= weights[attr]/(float(sigma)*float(sigma))

        dw0 = 0
        for record in data:
            dw0 += float(record[attributes[-1]])-record['pr']
        dw0 -= weights[0]/(float(sigma)*float(sigma))

        weights[0] += float(eta)*dw0
        for attr in attributes[:-1]:
            weights[attr] += float(eta)*dw[attr]

        convergence = dw0*dw0
        for attr in attributes[:-1]:
            convergence += dw[attr]*dw[attr]
        convergence = math.sqrt(convergence)
                
    return weights

def get_classification(record,attributes,weights):
    classify = weights[0]
    prob = 0.0
    for attr in attributes[:-1]:
        classify += weights[attr]*float(record[attr])
    prob = 1-1.0/(1.0+math.exp(classify))
    return prob

def classify(data,attributes,weights):

    data = data[:]
    classification = []
    for record in data:
        classification.append(get_classification(record,attributes,weights))
    return classification

if __name__ == "__main__":
    # Get the training and test data filenames from the user
    training_filename, test_filename,eta,sigma,module_filename = get_filenames()
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
    
    weights = get_weights(training_data,attributes,eta,sigma)
    classification = classify(test_data,attributes,weights)
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
    module_data.write("%s"%weights[0]+"\n")
    
    for attr in attributes[:-1]:
        module_data.write("%s"%attr+" "+"%s"%weights[attr]+"\n")
    module_data.close()
