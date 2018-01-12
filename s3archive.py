from __future__ import print_function
import json
import botocore
import boto3
import os
import sys
import logging
import re
from subprocess import run, CalledProcessError

s3 = boto3.resource('s3')

STDERR = sys.stderr
BUCKET_NAME = 'test'
SH_FILE = 's3toarchive_shudder.txt'
SN_FILE = 's3toarchive_sundance.txt'
TMP_DIR = '/tmp'
shudder_dest = "{}/{}".format(TMP_DIR, SH_FILE)
sundance_dest = "{}/{}".format(TMP_DIR, SN_FILE)
topic_arn = "arn:aws:sns:us-east-1:923250093194:ContentS3ArchiveSucess"
files_moved = []
SN_CHANNEL = 'test'
SH_CHANNEL = 'test'
all_items={
    SN_CHANNEL: {},
    SH_CHANNEL: {}
}

client = boto3.client(
    "sns",
    region_name='us-east-1'
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start():
    try:
        s3.Bucket(BUCKET_NAME).download_file(SH_FILE, shudder_dest)
    except botocore.exceptions.ClientError as ex:
        if ex.response['Error']['Code'] == "404":
            logger.info("Shudder archive file not present in s3 ")
            #LOGGER("ContentOps Archive", "Shudder archive file does not exist", "info")
        else:
            logger.error(ex)
            #LOGGER("ContentOps Archive", ex, "error")
            raise

    try:
        s3.Bucket(BUCKET_NAME).download_file(SN_FILE, sundance_dest)
    except botocore.exceptions.ClientError as ex:
        if ex.response['Error']['Code'] == "404":
            logger.info("SundanceNow archive file not present in s3 ")
            sys.exit()
            #LOGGER("ContentOps Archive", "Sundancenow archive file does not exist", "info")
        else:
            logger.error(ex)
            #LOGGER("ContentOps Archive", ex, "error")
            raise


    shudder_handle = open(shudder_dest, 'r')
    sundance_handle = open(sundance_dest, 'r')


    for channel, filename in (('shudder', shudder_handle), ('sundancenow', sundance_handle)):

        for line in filename:
            strip_line = line.strip()
            if not strip_line:
                continue
            (source_filename, dest_id_title) = strip_line.split(',')

            if dest_id_title not in all_items[channel]:
                all_items[channel][dest_id_title] = []

            all_items[channel][dest_id_title].append(source_filename)


    for dest_id_titles, channel_dir in (all_items[SH_CHANNEL].keys(), SH_CHANNEL) , (all_items[SN_CHANNEL].keys(), SN_CHANNEL):
        for dest_id_title in dest_id_titles:
        #    print (dest_id_title, channel_dir)
            for source_filename in (all_items[channel_dir][dest_id_title]):

                extra_opt=""
                if not re.search("\.\w+$", source_filename, flags=re.IGNORECASE):
                    extra_opt="--recursive"

                s3mv = 'aws s3 mv s3://amctest1/{} s3://amcarchives/{}/{}/{} {}'.format(source_filename, channel_dir, dest_id_title, source_filename, extra_opt)
                logger.info(s3mv)
            try:
                run(s3mv, shell=True, check=True)
                logger.info(s3mv)
                #LOGGER("S3Archive", s3mv, "info")
            except CalledProcessError as ex:
                logger.error(ex)
                #LOGGER("ContentOps Archive", ex, "error")

    #Cleanup s3
    try:
        s3.Object(BUCKET_NAME, SH_FILE).delete()
        s3.Object(BUCKET_NAME, SN_FILE).delete()
    except:
        logger.error("Unable to remove s3 archive text files for cleanup")

    #Cleanup Local File

    os.remove(shudder_dest)
    os.remove(sundance_dest)


    logger.info("ContentOps Archive S3 Move complete!")
#LOGGER("ContentOps Archive", "S3 Move complete!", "info")

if __name__ == '__main__':
    start()
