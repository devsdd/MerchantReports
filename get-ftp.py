#!/usr/bin/python

import os
import pysftp
import paramiko
import datetime
from yamlConfig import load_config
from syslog_writer import log_action
from make_local_dirs import create_local_dirs_if_missing

def date_format_yesterday(formatString):

    today = datetime.datetime.today()
    one_day = datetime.timedelta(days=1)
    yesterday = today - one_day
    yesterFormat = yesterday.strftime(formatString)

    return yesterFormat


def construct_filename(config, gateway, access_method):
    files = []

    fileStrings = config["SFTP"][gateway]["fileStrings"]
    dateFormat = config["SFTP"][gateway]["dateFormat"]
    fileExtension = config["SFTP"][gateway]["fileExtension"]

    yesterdayFormatString = date_format_yesterday(dateFormat)

    for f in fileStrings:
        completeFileName = f + yesterdayFormatString + fileExtension
        files.append(completeFileName)
    return files


def get_files_using_pysftp(gateway, config, files):

    gatewayServer = config["SFTP"][gateway]["URL"]
    gatewayUser = config["SFTP"][gateway]["user"]
    gatewayPassword = config["SFTP"][gateway]["password"]
    ftpDir = config["SFTP"][gateway]["ftpDir"]
    dateFormat = config["SFTP"][gateway]["dateFormat"]

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    try:
        with pysftp.Connection(host=gatewayServer, username=gatewayUser, password=gatewayPassword, cnopts=cnopts) as sftp:
            # change to appropriate directory for each server
            try:
                # Alipay makes new date-stamped folders everyday:
                if gateway == "Alipay":
                    ftpDir = ftpDir + "/" + date_format_yesterday(dateFormat)
                    sftp.cwd(ftpDir)
                else:
                    sftp.cwd(ftpDir)
            except:
                log_action("ERROR", "Failed to change directory to %s on %s" %(ftpDir, gatewayServer), "SFTP_download")
                raise

            for f in files:
                if sftp.isfile(f):  # check if file exists on remote location
                    try:            
                        sftp.get(f)
                    except:
                        log_action("ERROR", "Error downloading file " + f, "SFTP_download")
                        raise
                    else:
                        os.rename(f,  gateway + "_" + f)
                else:
                    log_action("ERROR", "File %s not found on server %s" % (f, gatewayServer), "SFTP_download")
    except:
        log_action("ERROR", "Failed to establish %s connection to server %s" % ("SFTP", gatewayServer), "SFTP_download")
        raise

    return


if __name__ == "__main__":

    yamlConfig = load_config("creds.yaml")
    sftpGateways = list(yamlConfig["SFTP"])

    for gateway in sftpGateways:
        if yamlConfig["SFTP"][gateway]["active"] == "True":
            files = construct_filename(yamlConfig, gateway, "SFTP")
            localDir = <YOUR_REPORTS_DIR> + gateway + "/"
            # change working directory to per gateway Dir
            if not os.path.isdir(localDir):
                os.makedirs(localDir)
            os.chdir(localDir)
            get_files_using_pysftp(gateway, yamlConfig, files)

