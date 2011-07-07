#!/usr/local/bin/python

#
#  tr10629imageAssoc.py
###########################################################################
#
#  Purpose:
#
#      This script will create accession IDs that are associated with the
#      fullsize images. Each accession ID is the same as the figure label.
#
#  Usage:
#
#      tr10629imageAssoc.py
#
#  Env Vars:
#
#      MGD_DBUSER
#      MGD_DBPASSWORDFILE
#      IMAGE_ACCESSION
#      REFERENCE
#      CREATEDBY
#      GUDMAP_LOGICALDB
#
#  Inputs:  None
#
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

import sys
import os
import db
import mgi_utils
import loadlib

#
#  CONSTANTS
#
BCP_DELIM = '\t'

FULLSIZE_IMAGE_TYPE_KEY = 1072158

IMAGE_MGITYPE_KEY = '9'
ACC_PRIVATE = '0'
ACC_PREFERRED = '1'

loaddate = loadlib.loaddate

#
#  GLOBALS
#
user = os.environ['MGD_DBUSER']
passwordFile = os.environ['MGD_DBPASSWORDFILE']
imageAccFile = os.environ['IMAGE_ACCESSION']
jNumber = os.environ['REFERENCE']
createdBy = os.environ['CREATEDBY']
logicalDBKey = os.environ['GUDMAP_LOGICALDB']

createdByKey = 0
refKey = 0
accKey = 0


#
# Purpose: Perform initialization steps.
# Returns: Nothing
# Assumes: Nothing
# Effects: Sets global variables
# Throws: Nothing
#
def init ():
    global createdByKey, refKey, accKey

    db.useOneConnection(1)
    db.set_sqlUser(user)
    db.set_sqlPasswordFromFile(passwordFile)

    #
    # Get the created by key for the user.
    #
    createdByKey = loadlib.verifyUser(createdBy, 0, None)

    #
    # Get the reference key for the J-Number.
    #
    refKey = loadlib.verifyReference(jNumber, 0, None)

    #
    # Get the next available accession key.
    #
    results = db.sql('select max(_Accession_key) + 1 as maxKey from ACC_Accession', 'auto')
    accKey = results[0]['maxKey']

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
# Purpose: Load the bcp file into the database.
# Returns: Nothing
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing
#
def bcpFiles ():

    fpImageAccFile.close()

    bcpCmd = 'cat %s | bcp %s..ACC_Accession in %s -c -t"%s" -S%s -U%s' \
	% (passwordFile, db.get_sqlDatabase(), imageAccFile, BCP_DELIM, db.get_sqlServer(), db.get_sqlUser())
    os.system(bcpCmd)

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
    # Get all the figure labels and image keys for each fullsize image
    # that has been loaded for the reference.
    #
    results = db.sql('''select figureLabel, _Image_key
                     from IMG_Image
                     where _Refs_key = %s
                     and _ImageType_key = %s''' % (str(refKey), str(FULLSIZE_IMAGE_TYPE_KEY)), 'auto')

    #
    # Create an accession record for each fullsize image.
    #
    for r in results:

        figureLabel = r['figureLabel']
        imageKey = r['_Image_key']

        #
        # The figure label is used for the acc ID (e.g. "GUDMAP:10").
        #
        accID = figureLabel;
        prefixPart = ''
        numericPart = accID

        fpImageAccFile.write(str(accKey) + '\t' +
                             accID + '\t' +
                             prefixPart + '\t' +
                             numericPart + '\t' +
                             str(logicalDBKey) + '\t' +
                             str(imageKey) + '\t' +
                             IMAGE_MGITYPE_KEY + '\t' +
                             ACC_PRIVATE + '\t' +
                             ACC_PREFERRED + '\t' +
                             str(createdByKey) + '\t' +
                             str(createdByKey) + '\t' +
                             loaddate + '\t' + loaddate + '\n')
        accKey += 1

    return


#
# Main
#

init()
openFiles()
process()
bcpFiles()

sys.exit(0)
