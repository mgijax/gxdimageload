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
#  09/19/2007  DBM  Initial development
#
###########################################################################

import sys
import os
import string
import re
import db
import mgi_utils
import loadlib

#
#  CONSTANTS
#
BCP_DELIM = '\t'

#
#  GLOBALS
#
user = os.environ['MGD_DBUSER']
passwordFile = os.environ['MGD_DBPASSWORDFILE']
resultImageFile = os.environ['RESULT_IMAGE_FILE']
jNumber = os.environ['REFERENCE']

FULLSIZE_IMAGE_TYPE_KEY = 1072158

assocTable = 'GXD_InSituResultImage'

#
# The bcp file should be created in the same directory as the input file.
#
dir, file = os.path.split(resultImageFile)
bcpFile = dir + '/' + assocTable + '.bcp'

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
    db.set_sqlUser(user)
    db.set_sqlPasswordFromFile(passwordFile)

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

    paneKeyLookup = {}

    #
    # Get the reference key for the J-Number.
    #
    refKey = loadlib.verifyReference(jNumber, 0, None)

    #
    # Get all the figure labels and associated image pane keys for the
    # reference.
    #
    results = db.sql('select i.figureLabel, ip._ImagePane_key ' + \
                     'from IMG_Image i, IMG_ImagePane ip ' + \
                     'where i._Image_key = ip._Image_key ' + \
			   'and i._ImageType_key = %d ' % (FULLSIZE_IMAGE_TYPE_KEY) + \
                           'and i._Refs_key = %d' % (refKey), 'auto')

    for r in results:
        figureLabel = r['figureLabel']
        paneKey = r['_ImagePane_key']
        paneKeyLookup[figureLabel] = paneKey
        #print 'paneKeyLookup[' + figureLabel + '] = ' + str(paneKey)

    return


#
# Purpose: Open the files.
# Returns: Nothing
# Assumes: The names of the files are set in the environment.
# Effects: Sets global variables
# Throws: Nothing
#
def openFiles ():
    global fpResultImageFile, fpBCPFile

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

    bcpCmd = 'cat %s | bcp %s..%s in %s -c -t"%s" -S%s -U%s' % (passwordFile, db.get_sqlDatabase(), assocTable, bcpFile, BCP_DELIM, db.get_sqlServer(), db.get_sqlUser())
    os.system(bcpCmd)

    db.sql('update statistics %s' % (assocTable), None)

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
        tokens = re.split('\t', line[:-1])
        resultKey = tokens[0]
        figureLabel = tokens[1]

        #
        # Find the image pane key for the figure label and write it to the
        # bcp file to associate it with the result. If the figure label is
        # not in the lookup, print an error message.
        #
        if paneKeyLookup.has_key(figureLabel):
            paneKey = paneKeyLookup[figureLabel]
            fpBCPFile.write(str(resultKey) + '\t' + str(paneKey) + '\t' +
                            cdate + '\t' + cdate + '\n')
        else:
            print 'Missing pane key for figure label: ' + figureLabel

        line = fpResultImageFile.readline()

    #
    # need to update the hasImage bit in the expression cache
    # the expression cache is created by the assayload
    # but since the images are not attached until AFTER the assayload is run,
    # the hasImage bit needs to be re-set to "1".
    #

    execSQL='''update GXD_Expression set hasImage = 1
            from IMG_Image i, IMG_ImagePane p, 
            GXD_Specimen s, GXD_InSituResult ir, GXD_InSituResultImage iri, GXD_Expression e
            where i._MGIType_key = 8 
            and i._ImageType_key = 1072158
            and i.xDim is not null
            and i._Image_key = p._Image_key
            and p._ImagePane_key = iri._ImagePane_key
            and iri._Result_key = ir._Result_key
            and ir._Specimen_key = s._Specimen_key
            and s._Assay_key = e._Assay_key
            and e.hasImage = 0
            and e._Refs_key = %s''' % (refsKey)

    print execSQL
    db.sql(execSQL, None)

    return 0


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
