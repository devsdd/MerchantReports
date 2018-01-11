import logging
import logging.handlers

def log_action(status, message, access_method):

    logger = logging.getLogger(access_method)
    handler = logging.FileHandler("/home/sid/code/action.log")

    #add formatter to the handler
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: "%(message)s"', datefmt="%Y-%m-%d %H:%M:%S")

    handler.formatter = formatter
    logger.addHandler(handler)

    if status == "ERROR":
        logger.setLevel(logging.ERROR)
        logger.error(message)
    elif status == "SUCCESS":
        logger.setLevel(logging.INFO)
        logger.info(message)

    return

if __name__ == "__main__":
    raise Exception(__file__ + " is not supposed to be run in standalone mode.")
