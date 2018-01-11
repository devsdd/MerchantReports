#!/usr/bin/python

import yaml
import datetime
import imaplib
import smtplib
import email
import os
import glob
import zipfile
from yamlConfig import load_config
from syslog_writer import log_action
from make_local_dirs import create_local_dirs_if_missing

def list_email_gateways(config):
    emailGateways = list(config["Email"])
    return emailGateways

def connect_IMAP(yamlConfig):

    IMAPuserName = yamlConfig["emailAddress"]
    IMAPpassword = yamlConfig["password"]
    IMAPserver = yamlConfig["IMAPserver"]

    try:
        connection = imaplib.IMAP4_SSL(IMAPserver)
    except:
        log_action("ERROR", "Failed to establish %s connection to server %s" % ("IMAP", IMAPserver), "Email")
        raise
    else:
        try:
            connection.login(IMAPuserName, IMAPpassword)
        except:
            log_action("ERROR", "IMAP authentication failed for user %s on %s" % (IMAPuserName, IMAPserver), "Email")
            raise

    return connection

def forward_email(yamlConfig, to_addr, msg):

    SMTPuserName = yamlConfig["emailAddress"]
    SMTPpassword = yamlConfig["password"]
    SMTPserver = yamlConfig["SMTPserver"]

    try:
        smtpObj = smtplib.SMTP(SMTPserver, 587)
    except:
        log_action("ERROR", "Failed to establish %s connection to server %s" % ("SMTP", SMTPserver), "Email")
        raise
    else:
        try:
            smtpObj.login(SMTPuserName, SMTPpassword)
        except:
            log_action("ERROR", "SMTP authentication failed for user %s on %s" % (SMTPuserName, SMTPserver), "Email")
            raise

    smtpObj.sendmail(SMTPuserName, to_addr, msg.as_string())
    smtpObj.quit

    return


def parse_emails(conn, gateway, config, mailboxConfig):
    fromAddress = config["Email"][gateway]["fromAddress"]

    retVal, data = conn.select("INBOX")
    if retVal != "OK":
        log_action("ERROR", "Failed to select Inbox folder, aborting...", "Email")
        sys.exit(1)

    retVal, data = conn.search(None, "FROM", fromAddress, "UNSEEN")
    if retVal != "OK":
        log_action("ERROR", "No new emails", "Email")
        sys.exit(1)

    for num in data[0].split():
        try:
            retVal, data = conn.fetch(num, '(RFC822)')
        except:
            log_action("ERROR", "ERROR fetching message %s From %s" % (num, fromAddress), "Email")
            raise

	if retVal != 'OK':
            log_action("ERROR", "ERROR getting message %s" % num, "Email")
            continue

        msg = email.message_from_string(data[0][1])

        # Messages with attachments are multipart messages
        if msg.get_content_maintype() == 'multipart':
            for part in msg.walk():
                # multipart are just containers, so we skip them
                if part.get_content_maintype() == 'multipart':
                    continue
#                if part.get('Content-Disposition') is None:
#                    print("Malformed Content-Disposition")
#                    continue
                #save the attachment in the program directory
                mailboxFilename = part.get_filename()
                if mailboxFilename != None:
                    localFileName = gateway + "_" + mailboxFilename
                    uploadedFileName = localFileName + ".uploaded"
                    if not os.path.isfile(uploadedFileName):
                        fp = open(localFileName, 'wb')
                        try:
                           fp.write(part.get_payload(decode=True))
                        except:
                           log_action("ERROR", "Failed to download attachment from email with subject %s" % msg['Subject'], "Email")
                           continue
                        else:
                            # Look at unread messages only
                            conn.uid('store', num, '+FLAGS', '(\\Unread)') 
                            conn.copy(num, 'Archive')
                            conn.expunge()
                        finally:
                           fp.close()
                        if localFileName.endswith('.zip'):
                           if zipfile.is_zipfile(localFileName):
                               fz = zipfile.ZipFile(localFileName, 'r')
                               fz.extractall()
                               # get names of files in archive:
                               filesInZipFile = fz.namelist()
                               # rename unzipped files
                               for f in filesInZipFile:
                                   if not f.startswith(gateway):
                                       # Deal with PayU credit card file separately
                                       if (<YOUR_DOMAIN_NAME> + "_CC_") in localFileName:
                                           fileNamePart1 = f.split("_")[0]
                                           fileNamePart2 = f.split("_")[1]
                                           fileNamePart3 = f.split("_")[2]
                                           os.rename(f, gateway + "_" + fileNamePart1 + "_" + fileNamePart2 + "_CC_" + fileNamePart3)
                                       else:
                                           os.rename(f, gateway + "_" + f)
                               fz.close()
                               # delete zip file
                               os.remove(localFileName)
                           else:
                               log_action("ERROR", "Invalid attachment file %s received from %s" % (localFileName, gateway), "Email")
                    else:
                        log_action("INFO","is already uploaded" % uploadedFileName, "Email")

                else:
                    print("Invalid mailboxFilename")
                # WebMoney sends mail to one email address only, so we fwd those mails from here to whoever needs them:
                if gateway == "WebMoney":
                    toAddress = <OTHER_RCPT>
                    forward_email(mailboxConfig, toAddress, msg)
        else:
            log_action("ERROR", "Not a Multipart message")

    return

if __name__ == "__main__":

    gatewayConfig = load_config("download_settings.yaml")
    mailboxConfig = load_config("email-creds.yaml")
    emailGateways = list_email_gateways(gatewayConfig)

    conn = connect_IMAP(mailboxConfig)
    for gw in emailGateways:
        localDir = create_local_dirs_if_missing(gw)
        os.chdir(localDir)
        parse_emails(conn, gw, gatewayConfig, mailboxConfig)

    conn.logout()
