# /usr/bin/env python
welcomeText = '''#
# hire.vladimir@gmail.com
#
# allows for math operations on MV fields
#
# rev. history
# 10/25/15 1.0 initial write / quick hack to solve one task
#
'''
import time, os, re
import logging, logging.handlers
import splunk.Intersplunk as si

# Mini 'six'-like compat layer
import six
if sys.version_info[0] == 2:
    string_types = (six.string_types,)
else:
    string_types = (str,)


#######################################
# SCRIPT CONFIG
#######################################
# set log level valid options are: (NOTSET will disable logging)
# CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
SPLUNK_HOME = "../../../../"
LOG_LEVEL = logging.INFO
LOG_FILE_NAME = "mvmath.log"


def setup_logging():  # setup logging
    global SPLUNK_HOME, LOG_LEVEL, LOG_FILE_NAME

    log_format = "%(asctime)s %(levelname)-s\t%(module)s[%(process)d]:%(lineno)d - %(message)s"
    logger = logging.getLogger('v')
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(logging.NullHandler())

    # l = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, 'var', 'log', 'splunk', LOG_FILE_NAME), mode='a', maxBytes=1000000, backupCount=2)
    # l.setFormatter(logging.Formatter(log_format))
    # logger.addHandler(l)

    # ..and (optionally) output to console
    # logH = logging.StreamHandler()
    # logH.setFormatter(logging.Formatter(fmt=log_format))
    # logger.addHandler(logH)

    logger.propagate = False
    return logger


def die(msg):
    logger.error(msg)
    exit("mvmath: %s" % (msg,))


def validate_args(keywords, argvals):
    logger.info('function="validate_args" calling getKeywordsAndOptions keywords="%s" args="%s"', keywords, argvals)

    # validate keywords
    # if len(keywords) != 1:
    #     die("One argument needs be specified; see command for usage details. Arguments passed: %d" % len(keywords))

    # validate args
    ALLOWED_OPTIONS = ['debug', 'field', 'field2', 'labelfield', 'prefix']
    MANDATORY_OPTIONS = []

    if len([x for x in argvals if x in MANDATORY_OPTIONS]) < len(MANDATORY_OPTIONS):
        die("Insufficient number of mandatory arguments found. Mandatory argumets are: %s" % (MANDATORY_OPTIONS,))

    illegal_args = [x for x in argvals if x not in ALLOWED_OPTIONS]
    if len(illegal_args) != 0:
        die("The argument(s) '%s' is invalid. Supported arguments are: %s" % (illegal_args, ALLOWED_OPTIONS))


def arg_on_and_enabled(argvals, arg, rex=None, is_bool=False):
    result = False
    if is_bool:
        rex = "^(?:t|true|1|yes)$"

    if (rex is None and arg in argvals) or (arg in argvals and re.match(rex, argvals[arg])):
        result = True
    return result


if __name__ == '__main__':
    logger = setup_logging()
    logger.info('starting..')
    eStart = time.time()
    try:
        results = si.readResults(None, None, False)
        keywords, argvals = si.getKeywordsAndOptions()
        validate_args(keywords, argvals)

        if arg_on_and_enabled(argvals, "debug", is_bool=True):
            logger.setLevel(logging.DEBUG)
            logger.debug("detecting debug argument passed, setting command log_level=DEBUG")

        output_column_name = "mvmath"
        if arg_on_and_enabled(argvals, "labelfield"):
            output_column_name = argvals['labelfield']

        if arg_on_and_enabled(argvals, "prefix"):
            output_column_name = argvals['prefix'] + output_column_name

        for row in results:
            if argvals['field'] in row and argvals['field2'] in row:
                tally = float(row[argvals['field2']])
                vdata = row[argvals['field']]
                res = ["{:.2%}".format(float(x) / tally) for x in vdata]
                if isinstance(vdata, string_types) and vdata:
                    res = "{:.2%}".format(float(vdata) / tally)

                row[output_column_name + "_result"] = res
                logger.debug('---> %s = vdata="%s", tally="%s", out="%s"', row['field'], vdata, tally, res)

        # logger.debug('results="%s"' % results)
        logger.info('sending events to splunk count="%d"', len(results))
        si.outputResults(results)
    except Exception as e:
        logger.exception('error while processing events, exception="%s"', e)
        si.generateErrorResults(e)
        raise
    finally:
        logger.info('exiting, execution duration=%s seconds', time.time() - eStart)
