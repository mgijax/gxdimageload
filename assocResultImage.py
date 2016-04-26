#!/usr/local/bin/python

#
#  assocResultImage.py
###########################################################################
#
#  Purpose:
#
#      This script associate assay results to images, using the result
#      keys and figure labels defined in the input file.
#
#  Usage:
#
#      assocResultImage.py
#
#  Env Vars:
#
#      MGD_DBUSER
#      MGD_DBPASSWORDFILE
#      RESULT_IMAGE_FILE
#      REFERENCE
#
#  Inputs:
#
#      Result_Image.txt - Tab-delimited fields:
#
#          1) Result key
#          2) Figure label
#
#  Outputs:
#
#      GXD_InSituResultImage.bcp
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
#  01/22/2009  LEC  add updateExpressionCache
#
#  09/19/2007  DBM  Initial development
#
###########################################################################

import sys
import os
import string
import db
import mgi_utils
import loadlib

#
#  GLOBALS
#
resultImageFile = os.environ['RESULT_IMAGE_FILE']
jNumber = os.environ['REFERENCE']

FULLSIZE_IMAGE_TYPE_KEY = 1072158
refKey = ''
paneKeyLookup = {}
assocTable = 'GXD_InSituResultImage'
bcpFile = assocTable + '.bcp'
cdate = mgi_utils.date('%m/%d/%Y')

#
# Purpose: Perform initialization steps.
# Returns: Nothing
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing
#
def init ():
    db.useOneConnection(1)
    return

#
# Purpose: Create a dictionary for looking up the image pane key for a
#          figure label. All figure labels for the given reference are
#          included.
# Returns: Nothing
# Assumes: Nothing
# Effects: Sets global variable
# Throws: Nothing
#
def buildPaneKeyLookup ():
    global paneKeyLookup, refKey

    #
    # Get the reference key for the J-Number.
    #
    refKey = loadlib.verifyReference(jNumber, 0, None)

    #
    # Get all the figure labels and associated image pane keys for the
    # reference.
    #
    results = db.sql('''select i.figureLabel, ip._ImagePane_key
                     from IMG_Image i, IMG_ImagePane ip
                     where i._Image_key = ip._Image_key
		     and i._ImageType_key = %d 
                     and i._Refs_key = %d''' % (FULLSIZE_IMAGE_TYPE_KEY, refKey), 'auto')

    for r in results:
        figureLabel = r['figureLabel']
        paneKey = r['_ImagePane_key']
        paneKeyLookup[figureLabel] = paneKey
        print 'paneKeyLookup[' + figureLabel + '] = ' + str(paneKey)

    return

#
# Purpose: Open the files.
# Returns: Nothing
# Assumes: The names of the files are set in the environment.
# Effects: Sets global variables
# Throws: Nothing
#
def openFiles ():
    global eResultImageFile, fpBCPFile

    #
    # Open the input file.
    #
    try:
        fpResultImageFile = open(resultImageFile, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + resultImageFile + '\n')
        sys.exit(1)

    #
    # Open the output file.
    #
    try:
        fpBCPFile = open(bcpFile, 'w')
    except:
        sys.stderr.write('Cannot open output file: ' + bcpFile + '\n')
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
    fpResultImageFile.close()
    fpBCPFile.close()
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
    db.commit()
    db.useOneConnection(0)

    bcpCommand = os.environ['PG_DBUTILS'] + '/bin/bcpin.csh'
    currentDir = os.getcwd()

    bcpCmd =  '%s %s %s %s %s %s "\\t" "\\n" mgd' \
        % (bcpCommand, db.get_sqlServer(), db.get_sqlDatabase(), assocTable, currentDir, bcpFile)

    diagFile.write('%s\n' % bcpCmd)
    os.system(bcpCmd)

    return

#
# Purpose: Create the bcp file from the results/image data in the input file.
# Returns: 0 if successful, 1 for an error
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing
#
def process ():

    #
    # Check each result key/figure label pair in the input file.
    #

    line = fpResultImageFile.readline()

    while line:
        tokens = string.split(line[:-1], '\t')
        resultKey = tokens[0]
        figureLabel = tokens[1]

        #
        # Find the image pane key for the figure label and write it to the
        # bcp file to associate it with the result. If the figure label is
        # not in the lookup, print an error message.
        #
        if paneKeyLookup.has_key(figureLabel):
            paneKey = paneKeyLookup[figureLabel]
            fpBCPFile.write(str(resultKey) + '\t' + str(paneKey) + '\t' + cdate + '\t' + cdate + '\n')
        else:
            print 'Missing pane key for figure label: ' + figureLabel

        line = fpResultImageFile.readline()

    return

#
# Main
#
init()
buildPaneKeyLookup()
openFiles()
process()
closeFiles()
runBCP()
sys.exit(0)

