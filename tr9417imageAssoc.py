#!/usr/local/bin/python

#
#  tr9417imageAssoc.py
###########################################################################
#
#  Purpose:
#
#      This script will create accession IDs that are associated with the
#      fullsize images.
#
#  Usage:
#
#      tr9417imageAssoc.py
#
#  Env Vars:
#
#      MGD_DBUSER
#      MGD_DBPASSWORDFILE
#      IMAGE_LIST_FIG_FILE
#      IMAGE_ACCESSION
#      REFERENCE
#      CREATEDBY
#
#  Inputs:
#
#       assayload.txt, a tab-delimited file in the format:
#               field 1: Probe ID
#               field 2: MGI symbol
#               field 3: Marker ID
#               field 4: Specimen Label
#               field 5: Genotype ID
#               field 6: Tissue Strength
#               field 7: Figure Label   (see gxdimageload/tr9417fullsize.py/tr9417thumbnail.py)
#               field 8: Image File Name        (see gxdimageload/tr9417fullsize.py/tr9417thumbnail.py)
#               field 9: Image link     (see gxdimageload/tr9417fullsize.py/tr9417thumbnail.py)
#  Outputs:
#
#      ACC_Accession_Image.bcp
#
#  Exit Codes:
#
#      0:  Successful completion
#      1:  An exception occurred
#
#  Assumes:  Nothing
#
#  Notes:  None
#
###########################################################################
#
#  Modification History:
#
#  Date        SE   Change Description
#  ----------  ---  -------------------------------------------------------
#
#  01/07/2009  lec  Initial development
#
###########################################################################

import sys
import os
import string
import db
import mgi_utils
import loadlib

#
#  CONSTANTS
#
BCP_DELIM = '\t'

FULLSIZE_IMAGE_TYPE_KEY = 1072158

GENEPAINT_LOGICALDB_KEY = '105'
IMAGE_MGITYPE_KEY = '9'
ACC_PRIVATE = '0'
ACC_PREFERRED = '1'

#
#  GLOBALS
#
user = os.environ['MGD_DBUSER']
passwordFile = os.environ['MGD_DBPASSWORDFILE']
imageListFile = os.environ['IMAGE_LIST_FIG_FILE']
imageAccFile = os.environ['IMAGE_ACCESSION']
jNumber = os.environ['REFERENCE']
createdBy = os.environ['CREATEDBY']

createdByKey = 0
cdate = mgi_utils.date('%m/%d/%Y')


#
# Purpose: Perform initialization steps.
# Returns: Nothing
# Assumes: Nothing
# Effects: Sets global variables
# Throws: Nothing
#
def init ():
    global createdByKey, accKey

    db.useOneConnection(1)
    db.set_sqlUser(user)
    db.set_sqlPasswordFromFile(passwordFile)

    createdByKey = loadlib.verifyUser(createdBy, 0, None)

    if createdByKey == 0:
        sys.stderr.write('Could not find user: ' + createdBy + '\n')
        sys.exit(1)

    results = db.sql('select max(_Accession_key) + 1 "maxKey" ' + \
                     'from ACC_Accession', 'auto')
    accKey = results[0]['maxKey']

    return


#
# Purpose: Create a dictionary for looking up the image file name for a
#          given figure label.
# Returns: Nothing
# Assumes: Nothing
# Effects: Sets global variable
# Throws: Nothing
#
def buildImageFileLookup ():
    global imageFileLookup

    #
    # Open the input file.
    #
    try:
        fp = open(imageListFile, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + imageListFile + '\n')
        sys.exit(1)

    #
    # Skip the heading record and process the remaining line of the file.
    #
    imageFileLookup = {}
    lineNum = 0
    for line in fp.readlines():

	lineNum = lineNum + 1

	if lineNum == 1:
	    continue

        tokens = string.split(line[:-1], '\t')
        figureLabel = tokens[6]
        imageFileLookup[figureLabel] = tokens
    fp.close()

    return


#
# Purpose: Open the files.
# Returns: Nothing
# Assumes: The names of the files are set in the environment.
# Effects: Sets global variables
# Throws: Nothing
#
def openFiles ():
    global fpImageAccFile

    #
    # Open the output file.
    #
    try:
        fpImageAccFile = open(imageAccFile, 'w')
    except:
        sys.stderr.write('Cannot open output file: ' + imageAccFile + '\n')
        sys.exit(1)

    return


#
# Purpose: Close the files.
# Returns: Nothing
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing
#
def closeFiles ():
    fpImageAccFile.close()

    return


#
# Purpose: Load the bcp file into the database.
# Returns: Nothing
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing
#
def runBCP ():

    sys.stdout.flush()

    bcpCmd = 'cat %s | bcp %s..ACC_Accession in %s -c -t"%s" -S%s -U%s' % (passwordFile, db.get_sqlDatabase(), imageAccFile, BCP_DELIM, db.get_sqlServer(), db.get_sqlUser())
    os.system(bcpCmd)

    db.sql('update statistics ACC_Accession', None)

    return


#
# Purpose: Create a bcp file for adding image accession IDs.
# Returns: 0 if successful, 1 for an error
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing
#
def process ():
    global accKey

    #
    # Get all the figure labels and image keys for the reference.
    #
    results = db.sql('''select i.figureLabel, i._Image_key
                     from IMG_Image i, BIB_Citation_Cache b
                     where b.jnumID = "%s"
		     and b._Refs_key = i._Refs_key
                     and _ImageType_key = %s''' % (jNumber, str(FULLSIZE_IMAGE_TYPE_KEY)), 'auto')

    for r in results:
        figureLabel = r['figureLabel']
        imageKey = r['_Image_key']

        if not imageFileLookup.has_key(figureLabel):
            print 'Missing image file name for figure label: ' + figureLabel

        accID = imageFileLookup[figureLabel][8]
        prefixPart = accID
        numericPart = ""

        fpImageAccFile.write(str(accKey) + '\t' +
                             accID + '\t' +
                             prefixPart + '\t' +
                             str(numericPart) + '\t' +
                             GENEPAINT_LOGICALDB_KEY + '\t' +
                             str(imageKey) + '\t' +
                             IMAGE_MGITYPE_KEY + '\t' +
                             ACC_PRIVATE + '\t' +
                             ACC_PREFERRED + '\t' +
                             str(createdByKey) + '\t' +
                             str(createdByKey) + '\t' +
                             cdate + '\t' + cdate + '\n')
        accKey += 1

    return 0


#
# Main
#
init()
buildImageFileLookup()
openFiles()
process()
closeFiles()
runBCP()

sys.exit(0)
