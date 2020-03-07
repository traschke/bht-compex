#!/bin/bash
set -e

# Setup variables
CORENLP_VERION=2018-10-05
CORENLPURLPREFIX=http://nlp.stanford.edu/software
CORENLPFILENAME=stanford-corenlp-full-$CORENLP_VERION
CORENLPFILENAMEEXT=$CORENLPFILENAME.zip
MODELFILENAMEEXT=stanford-german-corenlp-$CORENLP_VERION-models.jar
CORENLPURL=$CORENLPURLPREFIX/$CORENLPFILENAMEEXT
MODELURL=$CORENLPURLPREFIX/$MODELFILENAMEEXT
DESTDIR=.corenlp

# Remove old dirs and zips
if [ -f "$CORENLPFILENAMEEXT" ]; then rm $CORENLPFILENAMEEXT; fi
if [ -d "$CORENLPFILENAME" ]; then rm -rf $CORENLPFILENAME; fi
if [ -d "$DESTDIR" ]; then rm -rf $DESTDIR; fi

# Download corenlp and unzip it
curl -L -O $CORENLPURL
unzip $CORENLPFILENAMEEXT
# Remove the downloaded zip
rm $CORENLPFILENAMEEXT
# Rename folder to .corenlp
mv $CORENLPFILENAME $DESTDIR
# Download german models
cd $DESTDIR && { curl -L -O $MODELURL ; cd -; }
