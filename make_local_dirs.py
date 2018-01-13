import os

def create_local_dirs_if_missing(gateway):

    gatewaySpecificDir = <YOUR_REPORTS_DIR> + gateway + "/"
    if not os.path.isdir(gatewaySpecificDir):
        os.makedirs(gatewaySpecificDir)

    return gatewaySpecificDir
