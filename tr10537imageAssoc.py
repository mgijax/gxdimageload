#!/usr/local/bin/python

#
#  tr10537imageAssoc.py
###########################################################################
#
#  Purpose:
#
#      This script will create accession IDs that are associated with the
#      fullsize images. Each accession ID is the same as the figure label.
#
#  Usage:
#
#      tr10537imageAssoc.py
#
#  Env Vars:
#
#      MGD_DBUSER
#      MGD_DBPASSWORDFILE
#      IMAGE_ACCESSION
#      REFERENCE
#      CREATEDBY
#      BGEM_LOGICALDB
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
import re
import db
import mgi_utils

#
#  CONSTANTS
#
BCP_DELIM = '\t'

FULLSIZE_IMAGE_TYPE_KEY = 1072158

IMAGE_MGITYPE_KEY = '9'
ACC_PRIVATE = '0'
ACC_PREFERRED = '1'

#
#  GLOBALS
#
user = os.environ['MGD_DBUSER']
passwordFile = os.environ['MGD_DBPASSWORDFILE']
imageAccFile = os.environ['IMAGE_ACCESSION']
jNumber = os.environ['REFERENCE']
createdBy = os.environ['CREATEDBY']
logicalDBKey = os.environ['BGEM_LOGICALDB']

createdByKey = 0
refKey = 0
accKey = 0
cdate = mgi_utils.date('%m/%d/%Y')


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
    results = db.sql('select _User_key ' + \
                     'from MGI_User ' + \
                     'where login = "%s"' % (createdBy), 'auto')
    if len(results) > 0:
        createdByKey = results[0]['_User_key']
    else:
        sys.stderr.write('Could not find user: ' + createdBy + '\n')
        sys.exit(1)

    #
    # Get the reference key for the J-Number.
    #
    results = db.sql('select _Object_key ' + \
                     'from ACC_Accession ' + \
                     'where accID = "' + jNumber + '" and ' + \
                           '_LogicalDB_key = 1 and ' + \
                           '_MGIType_key = 1', 'auto')
    if len(results) > 0:
        refKey = results[0]['_Object_key']
    else:
        sys.stderr.write('Could not find reference: ' + jNumber + '\n')
        sys.exit(1)

    #
    # Get the next available accession key.
    #
    results = db.sql('select max(_Accession_key) + 1 "maxKey" ' + \
                     'from ACC_Accession', 'auto')
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
    # Get all the figure labels and image keys for each fullsize image
    # that has been loaded for the reference.
    #
    # NOTE: There was an additional set of images added after the initial
    #       batch, so the last condition to the "where" clause was added
    #       to this query to exclude the original batch.
    #
    results = db.sql('select figureLabel, _Image_key ' + \
                     'from IMG_Image ' + \
                     'where figureLabel like "g%" and ' + \
                           '_Refs_key = ' + str(refKey) + ' and ' + \
                           '_ImageType_key = ' + str(FULLSIZE_IMAGE_TYPE_KEY) + ' and ' + \
                           'creation_date > "2/24/2011"',
                     'auto')

    #
    # Create an accession record for each fullsize image.
    #
    for r in results:
        figureLabel = r['figureLabel']
        imageKey = r['_Image_key']

        #
        # The first part of the figure label prior to the '_' is used for
        # the acc ID (e.g. use "G00001" for "g00001_sj_g27_049_e11").
        # There can be many accession records created with the same acc ID,
        # but they will all be associated with different images.
        #
        accID = re.split('_',figureLabel)[0].upper()
        prefixPart = accID[0]
        numericPart = accID[1:]

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
                             cdate + '\t' + cdate + '\n')
        accKey += 1

    return 0


#
# Main
#
init()
openFiles()
process()
closeFiles()
runBCP()

sys.exit(0)
