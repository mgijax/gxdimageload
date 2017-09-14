#!/usr/local/bin/python
#
#  gudmapimageAssoc.py
###########################################################################
#
#  Purpose:
#
#      This script will create accession IDs that are associated with the
#      fullsize images. Each accession ID is the same as the figure label.
#
#  Usage:
#
#      gudmapimageAssoc.py
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
import string
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

    bcpScript = os.environ['PG_DBUTILS'] + '/bin/bcpin.csh'

    db.commit()

    fpImageAccFile.close()

    bcpI = '%s %s %s' % (bcpScript, db.get_sqlServer(), db.get_sqlDatabase())
    bcpII = '"\\t" "\\n" mgd'

    accTable = 'ACC_Accession'

    bcpCmd = '%s %s "/" %s %s' % (bcpI, accTable, imageAccFile, bcpII)

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
    results = db.sql('''
	select i._Image_key, i.figureLabel
	from IMG_Image i, IMG_ImagePane ii, ACC_Accession a
	where i._Refs_key = 172505
	and i._Image_key = ii._Image_key
	and i._Image_key = a._Object_key 
	and a._MGIType_key = 9 
	and a._LogicalDB_key = 19
	and not exists (select 1
    	from GXD_Assay a, GXD_Specimen s, GXD_InSituResult isr, GXD_InSituResultImage p 
    	where i._Refs_key = a._Refs_key 
    	and a._AssayType_key in (1,6,9,10,11) 
    	and a._Assay_key = s._Assay_key 
    	and s._Specimen_key = isr._Specimen_key 
    	and isr._Result_key = p._Result_key
    	and ii._ImagePane_key = p._ImagePane_key
	)
    	''', 'auto')

    #
    # Create an accession record for each fullsize image.
    #
    for r in results:

        imageKey = r['_Image_key']
        figureLabel = r['figureLabel']

        #
        # The figure label is used for the acc ID (e.g. "GUDMAP:10").
        #
        accID = figureLabel;
	prefixPart, numericPart = string.split(accID, ':')
        prefixPart = prefixPart + ':'

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

