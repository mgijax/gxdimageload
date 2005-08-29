#!/usr/local/bin/python

# $Header$
# $Name$
#
#  tr6739assoc.py
###########################################################################
#
#  Purpose:
#
#      This script will use the data in the result/image file (created
#      by the insituload) to create associations between an assay result
#      and 1 or more images.
#
#  Usage:
#
#      tr6739assoc.py
#
#  Env Vars:  None
#
#  Inputs:
#
#      The input file (Result_Image.txt) that contains the following
#      tab-delimited fields:
#
#      1) Result Key
#      2) Figure label part of the image name
#      3) Pane label part of the image name
#
#  Outputs:
#
#      BCP file:
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
#  08/18/2005  DBM  Initial development
#
###########################################################################

import sys
import os
import string
import db
import accessionlib
import loadlib

#
#  CONSTANTS
#

TAB = '\t'
CRT = '\n'
NULL = ''

J_NUMBER = 'J:93300'


#
#  FUNCTIONS
#

# Purpose: Perform initialization for the script.
# Returns: Nothing
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing

def initialize():
    global refKey, loadDate
    global dbServer, dbName, dbUser, dbPasswordFile
    global fpResultImage, bcpFile, fpBCP

    print 'Perform initialization'
    sys.stdout.flush()

    #
    #  Initialize global variables.
    #
    refKey = accessionlib.get_Object_key(J_NUMBER, 'Reference')
    loadDate = loadlib.loaddate
    dbServer = os.environ['DBSERVER']
    dbName = os.environ['DBNAME']
    dbUser = os.environ['DBUSER']
    dbPasswordFile = os.environ['DBPASSWORDFILE']
    dbPassword = string.strip(open(dbPasswordFile,'r').readline())

    #
    #  Set up a connection to the database.
    #
    db.useOneConnection(1)
    db.set_sqlLogin(dbUser, dbPassword, dbServer, dbName)

    #
    #  Open the result/image file.
    #
    resultImageFile =  os.environ['INSITUDATADIR'] + '/Result_Image.txt'

    try:
        fpResultImage = open(resultImageFile,'r')
    except:
        sys.stderr.write('Could not open result/image file: ' + resultImageFile)
        exit(1)

    #
    #  Open the bcp file.
    #
    bcpFile =  os.environ['DATADIR'] + '/GXD_InSituResultImage.bcp'

    try:
        fpBCP = open(bcpFile,'w')
    except:
        sys.stderr.write('Could not open bcp file: ' + bcpFile)
        exit(1)

    return


# Purpose: Perform cleanup steps for the script.
# Returns: Nothing
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing

def finalize():
    global fpResultImage

    db.useOneConnection(0)

    #
    #  Close the result/image file.
    #
    fpResultImage.close()

    return


# Purpose: Load the TMP_ProbeMarker table.
# Returns: Nothing
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing

def process():
    global refKey, loadDate
    global dbServer, dbName, dbUser, dbPasswordFile
    global fpResultImage, bcpFile, fpBCP

    print 'Create a dictionary to lookup image pane keys'
    sys.stdout.flush()

    #
    #  Create a dictionary that can be used to look up the image pane key
    #  for a given figure label and pane label.
    #
    results = db.sql('select i.figureLabel, ip.paneLabel, ' + \
                            'ip._ImagePane_key ' + \
                     'from mgd_dbm..IMG_Image i, ' + \
                          'mgd_dbm..IMG_ImagePane ip ' + \
                     'where i._Refs_key = ' + str(refKey) + ' and ' + \
                           'i._Image_key = ip._Image_key','auto')

    imageLookup = {}
    for r in results:
        imageLookup[string.strip(r['figureLabel']) + ':' + \
                    string.strip(r['paneLabel'])] = r['_ImagePane_key']

    print 'Create the bcp file for the GXD_InSituResultImage table'
    sys.stdout.flush()

    #
    #  Get the result key, figure label and pane label from each input
    #  record and use the labels to look up the image pane key.  The
    #  result key and image pane key are written to the bcp file.
    #
    for line in fpResultImage.readlines():
        tokens = string.split(line[:-1],TAB)
        labelString = tokens[1] + ':' + tokens[2]
        if imageLookup.has_key(labelString):
            fpBCP.write(tokens[0] + TAB +
                        str(imageLookup[labelString]) + TAB +
                        loadDate + TAB + loadDate + CRT)

    #
    #  Close the bcp file.
    #
    fpBCP.close()

    print 'Load the GXD_InSituResultImage table'
    sys.stdout.flush()

    #
    #  Load the GXD_InSituResultImage table with the bcp file.
    #
    bcpCmd = 'cat ' + dbPasswordFile + ' | bcp ' + dbName + \
             '..GXD_InSituResultImage in ' + bcpFile + \
             ' -c -S' + dbServer + ' -U' + dbUser
    os.system(bcpCmd)

    return


#
#  MAIN
#
initialize()
process()
finalize()


#  $Log$
#  Revision 1.1.2.1  2005/08/18 14:33:14  dbm
#  New for TR 6739
#
#
###########################################################################
#
# Warranty Disclaimer and Copyright Notice
#
#  THE JACKSON LABORATORY MAKES NO REPRESENTATION ABOUT THE SUITABILITY OR
#  ACCURACY OF THIS SOFTWARE OR DATA FOR ANY PURPOSE, AND MAKES NO WARRANTIES,
#  EITHER EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY AND FITNESS FOR A
#  PARTICULAR PURPOSE OR THAT THE USE OF THIS SOFTWARE OR DATA WILL NOT
#  INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS, OR OTHER RIGHTS.
#  THE SOFTWARE AND DATA ARE PROVIDED "AS IS".
#
#  This software and data are provided to enhance knowledge and encourage
#  progress in the scientific community and are to be used only for research
#  and educational purposes.  Any reproduction or use for commercial purpose
#  is prohibited without the prior express written permission of The Jackson
#  Laboratory.
#
# Copyright \251 1996, 1999, 2002, 2005 by The Jackson Laboratory
#
# All Rights Reserved
#
###########################################################################
