#!/usr/bin/python

# pysftp module acting buggy so using paramiko directly
# do not unzip files - Alipay sending files with Chinese character filenames in archive, causing zipfile module to barf

import os
# import pysftp
import paramiko
import datetime
import zipfile
from yamlConfig import load_config
from syslog_writer import log_action

# where all our config data is located relative to our code:
CONFIG_DIR = "config/"

def files_list(baseDir):
    fullPathsFileList = []

    for root, dir, files in os.walk(baseDir):
        for name in files:
            fullPathsFileList.append(os.path.join(root, name))

    return fullPathsFileList

# This function is currently buggy and useless
def connect_sftp():
    uploadConfig = load_config(CONFIG_DIR + "ftp_upload_creds.yaml")

    ftpServer = uploadConfig["ftpServer"]
    ftpPort = uploadConfig["port"]
    ftpUser = uploadConfig["user"]
    ftpPassword = uploadConfig["password"]
    ftpUploadDir = uploadConfig["uploadDir"]

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    try:
        sftp = open(pysftp.Connection(host=ftpServer, username=ftpUser, password=ftpPassword, port=ftpPort, cnopts=cnopts))
    except:
	log_action("ERROR", "Failed to establish %s connection to server %s" % ("SFTP", ftpServer), "SFTP_upload")
        raise
    # change to appropriate directory for server
    try:
        sftp.cwd(ftpUploadDir)
    except:
        log_action("ERROR", "Failed to change directory to %s on %s" %(ftpUploadDir, ftpServer), "SFTP_upload")
        raise
    return sftp

def upload_files(files):
    uploadConfig = load_config(CONFIG_DIR + "ftp_upload_creds.yaml")

    ftpServer = uploadConfig["ftpServer"]
    ftpPort = uploadConfig["port"]
    ftpUser = uploadConfig["user"]
    ftpPassword = uploadConfig["password"]
    ftpUploadDir = uploadConfig["uploadDir"]

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ftpServer, username=ftpUser, password=ftpPassword, port=ftpPort)
    except paramiko.SSHException:
        log_action("ERROR", "Failed to establish %s connection to server %s" % ("SFTP", ftpServer), "SFTP_upload")
        raise
        # change to appropriate directory for server
    sftp = ssh.open_sftp()
    try:
        sftp.chdir(ftpUploadDir)
    except:
        log_action("ERROR", "Failed to change directory to %s on %s" %(ftpUploadDir, ftpServer), "SFTP_upload")
        raise

    for f in files:
        if not f.endswith(".uploaded"):
            remoteFilePath = os.path.basename(f)
#            if f.endswith('.zip'):
#               if zipfile.is_zipfile(f):
#                   fz = zipfile.ZipFile(f, 'r')
#                   fz.extractall()
#                   # get names of files in archive:
#                   filesInZipFile = fz.namelist()
#                   # rename unzipped files
#                   for fu in filesInZipFile:
#                       if not fu.startswith(gateway):
#                           os.rename(f, gateway + "_" + fu)
#                   fz.close()
#                   # delete zip file
#                   os.remove(localFileName)
#               else:
#                   log_action("ERROR", "Invalid attachment file %s received from %s" % (localFileName, gateway), "Email")

            try:
                sftp.put(f, remoteFilePath)
            except:
                log_action("ERROR", "Error uploading file " + f, "SFTP_upload")
                raise
            else:
                log_action("SUCCESS",  f + " uploaded successfully", "SFTP_upload")
                os.rename(f, f + ".uploaded")

    ssh.close()
    return


if __name__ == "__main__":
    files = files_list(<YOUR_DOWNLOADS_DIR>)
    upload_files(files)
