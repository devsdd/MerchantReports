# Merchant Reports Automation

Any E-commerce site may be using multiple banks and/or payment gateways for their customers' transactions. All these financial institutions usually supply consolidated daily reports of these transactions to the site (called "Merchant"). These reports vary according to the whims of these institutions - some are CSV files, some are XLS(X), some are zipped and so on. The way the reports are distributed to the merchants also varies similarly - some are emailed to the merchant by the institution, some are kept on FTP servers with dedicated directories per merchant for the merchant to log into (usually securely, over SFTP), while some may be available through HTTP API's.

This project is for automating the process of manually logging into multiple FTP servers and Email accounts, downloading the reports to a single location, and then uploading them all to another FTP server of our own. Though the code can be institution-specific (marked as such in the comments) due to each institution's quirks, it is intended to also be generic enough that it shouldn't be too difficult to modify it to suit another payment gateway or bank.

The [download_settings.yaml](https://github.com/devsdd/MerchantReports/blob/master/download_settings.yaml) file contains a hash of gateways and providers organized according to the method in which we access their reports (SFTP, Email etc.) along with the credentials, FTP locations and filenames for each of them. This is used by the scripts [get-ftp.py](https://github.com/devsdd/MerchantReports/blob/master/get-ftp.py) and [extract_email_reports.py](https://github.com/devsdd/MerchantReports/blob/master/extract_email_reports.py).

The [email-creds.yaml](https://github.com/devsdd/MerchantReports/blob/master/email-creds.yaml) file contains the credentials to access the email account to which the institutions send the reports. This is used by the script [extract_email_reports.py](https://github.com/devsdd/MerchantReports/blob/master/extract_email_reports.py).

The [ftp_upload_creds.yaml](https://github.com/devsdd/MerchantReports/blob/master/ftp_upload_creds.yaml) file contains the credentials to access our own preferred FTP server. This is used by the script [put-ftp.py](https://github.com/devsdd/MerchantReports/blob/master/put-ftp.py). This step is needed only you are running this code on a machine other than the ultimate destination (FTP server) of all your report files.

A syslog-wrapper is used to generate logs of all error conditions since these scripts are typically run as once-a-day crons, and without logs, it becomes almost impossible to figure out if there were failures at any stage.

### Variables

Strings in caps enclosed by "<>" symbols are supposed to be variables which you substitute in as per your environment. For example, "</PATH/TO/LOG/FILE>".
