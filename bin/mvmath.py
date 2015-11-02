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

#######################################
# SCRIPT CONFIG
#######################################
# set log level valid options are: (NOTSET will disable logging)
# CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
SPLUNK_HOME = "."
LOG_LEVEL = logging.INFO
LOG_FILE_NAME = "mvmath.log"


def setup_logging():  # setup logging
    global SPLUNK_HOME, LOG_LEVEL, LOG_FILE_NAME
    if 'SPLUNK_HOME' in os.environ:
        SPLUNK_HOME = os.environ['SPLUNK_HOME']

    log_format = "%(asctime)s %(levelname)-s\t%(module)s[%(process)d]:%(lineno)d - %(message)s"
    logger = logging.getLogger('v')
    logger.setLevel(LOG_LEVEL)

    l = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, 'var', 'log', 'splunk', LOG_FILE_NAME), mode='a', maxBytes=1000000, backupCount=2)
    l.setFormatter(logging.Formatter(log_format))
    logger.addHandler(l)

    # ..and (optionally) output to console
    logH = logging.StreamHandler()
    logH.setFormatter(logging.Formatter(fmt=log_format))
    # logger.addHandler(logH)

    logger.propagate = False
    return logger


def die(msg):
    logger.error(msg)
    exit("mvmath: %s" % msg)


def validate_args(keywords, argvals):
    logger.info('function="validate_args" calling getKeywordsAndOptions keywords="%s" args="%s"' % (str(keywords), str(argvals)))

    # validate keywords
    # if len(keywords) != 1:
    #     die("One argument needs be specified; see command for usage details. Arguments passed: %d" % len(keywords))

    # validate args
    ALLOWED_OPTIONS = ['debug', 'field', 'field2', 'labelfield', 'prefix']
    MANDATORY_OPTIONS = []

    if len(filter(lambda x: x in MANDATORY_OPTIONS, argvals)) < len(MANDATORY_OPTIONS):
        die("Insuffucient number of mandatory arguments found. Mandatory argumets are: %s" % MANDATORY_OPTIONS)

    illegal_args = filter(lambda x: x not in ALLOWED_OPTIONS, argvals)
    if len(illegal_args) != 0:
        die("The argument(s) '%s' is invalid. Supported arguments are: %s" % (illegal_args, ALLOWED_OPTIONS))


def get_count(d):
    ret = 1
    if (d is "") or (d == ['']) or (d == []):
        ret = 0
    elif isinstance(row[argvals['field']], list):
        ret = len(d)
    return ret


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



        # regex = keywords[0]
        # logger.debug('will be applying regex="%s", to field="%s"' % (regex, argvals['field']))

        output_column_name = "mvmath"
        if arg_on_and_enabled(argvals, "labelfield"):
            output_column_name = argvals['labelfield']

        if arg_on_and_enabled(argvals, "prefix"):
            output_column_name = argvals['prefix'] + output_column_name

        for row in results:
            tally = float(row[argvals['field2']])
            vdata = row[argvals['field']]
            logger.debug('---> fdata="%s", tally="%s"' % (vdata, tally))
            row[output_column_name + "_result"] = map(lambda x: str(round(float(x) / tally * 100, 2)) + "%", vdata)

            # regex = keywords[0]
            # if regex in row:
            #     regex = row[regex]
            #     logger.debug('found substitution oppty, will be applying regex="%s", to field="%s"' % (regex, argvals['field']))
            #
            # # perform match
            # if isinstance(row[argvals['field']], list):
            #     logger.debug("dealing wiht mv field, will match per mv value")
            #     row[output_column_name + "_matches"] = filter(lambda x: re.findall(regex, x), row[argvals['field']])
            #
            #     if arg_on_and_enabled(argvals, "showunmatched", is_bool=True):
            #         row[output_column_name + "_unmatched"] = filter(lambda x: x not in row[output_column_name + "_matches"], row[argvals['field']])
            # else:
            #     logger.debug("dealing with string, will match string")
            #     row[output_column_name + "_matches"] = re.findall(regex, row[argvals['field']])
            #
            #     if arg_on_and_enabled(argvals, "showunmatched", is_bool=True) and get_count(row[output_column_name + "_matches"]) == 0:
            #         row[output_column_name + "_unmatched"] = row[argvals['field']]
            # logger.debug('applying regex="%s" to dataset="%s", matches="%d"' % (regex, row[argvals['field']], len(row[output_column_name + "_matches"])))
            #
            # if arg_on_and_enabled(argvals, "showcount", is_bool=True):
            #     row[output_column_name + "_count"] = get_count(row[output_column_name + "_matches"])
            #     row[output_column_name + "_input_count"] = get_count(row[argvals['field']])

        logger.debug('results="%s"' % results)
        logger.info('sending events to splunk count="%s"' % len(results))
        si.outputResults(results)
    except Exception, e:
        logger.error('error while processing events, exception="%s"' % e)
        si.generateErrorResults(e)
        raise Exception(e)
    finally:
        logger.info('exiting, execution duration=%s seconds' % (time.time() - eStart))
