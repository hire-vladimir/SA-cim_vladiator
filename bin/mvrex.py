# /usr/bin/env python
welcomeText = '''#
# hire.vladimir@gmail.com
#
# allow regex matches on MV fields + passing in regex values via field/token
#
# rev. history
# 10/20/15 1.0 initial write
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
LOG_FILE_NAME = "mvrex.log"


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
    exit("mvrex: %s" % msg)


def validate_args(keywords, argvals):
    logger.info('function="validate_args" calling getKeywordsAndOptions keywords="%s" args="%s"' % (str(keywords), str(argvals)))

    # validate keywords
    if len(keywords) != 1:
        die("One argument needs be specified; see command for usage details. Arguments passed: %d" % len(keywords))

    # validate args
    ALLOWED_OPTIONS = ['debug', 'field', 'showunmatched', 'prefix', 'showcount', 'labelfield']
    MANDATORY_OPTIONS = ['field']

    if len([x for x in argvals if x in MANDATORY_OPTIONS]) < len(MANDATORY_OPTIONS):
        die("Insuffucient number of mandatory arguments found. Mandatory argumets are: %s" % MANDATORY_OPTIONS)

    illegal_args = [x for x in argvals if x not in ALLOWED_OPTIONS]
    if len(illegal_args) != 0:
        die("The argument(s) '%s' is invalid. Supported arguments are: %s" % (illegal_args, ALLOWED_OPTIONS))


def get_count(d):
    ret = 1  # this will take care of cases when no mv is involved
    if (d is "") or (d == ['']) or (d == []):
        ret = 0
    elif isinstance(d, list):
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

        regex = keywords[0]
        logger.debug('will be applying regex="%s", to field="%s"' % (regex, argvals['field']))

        output_column_name = "mvrex"
        if arg_on_and_enabled(argvals, "labelfield"):
            output_column_name = argvals['labelfield']

        if arg_on_and_enabled(argvals, "prefix"):
            output_column_name = argvals['prefix'] + output_column_name

        for row in results:
            regex = keywords[0]
            if regex in row:
                regex = row[regex]
                logger.debug('found substitution oppty, will be applying regex="%s", to field="%s"' % (regex, argvals['field']))

            input_data = ""
            if argvals['field'] in row:
                input_data = row[argvals['field']]

            # perform match
            if isinstance(input_data, list):
                logger.debug("dealing wiht mv field, will match per mv value")
                row[output_column_name + "_matches"] = [x for x in input_data if re.findall(regex, x)]

                if arg_on_and_enabled(argvals, "showunmatched", is_bool=True):
                    row[output_column_name + "_unmatched"] = [x for x in input_data if x not in row[output_column_name + "_matches"]]
            else:
                logger.debug("dealing with string, will match string")
                row[output_column_name + "_matches"] = re.findall(regex, input_data)

                if arg_on_and_enabled(argvals, "showunmatched", is_bool=True) and get_count(row[output_column_name + "_matches"]) == 0:
                    row[output_column_name + "_unmatched"] = input_data
            logger.debug('applying regex="%s" to dataset="%s", matches="%d"' % (regex, input_data, len(row[output_column_name + "_matches"])))

            if arg_on_and_enabled(argvals, "showcount", is_bool=True):
                row[output_column_name + "_matched_count"] = get_count(row[output_column_name + "_matches"])
                row[output_column_name + "_input_count"] = get_count(input_data)
                if arg_on_and_enabled(argvals, "showunmatched", is_bool=True):
                    row[output_column_name + "_unmatched_count"] = int(row[output_column_name + "_input_count"]) - int(row[output_column_name + "_matched_count"])

        # logger.debug('results="%s"' % results)
        logger.info('sending events to splunk count="%s"' % len(results))
        si.outputResults(results)
    except Exception as e:
        logger.error('error while processing events, exception="%s"' % e)
        si.generateErrorResults(e)
        raise Exception(e)
    finally:
        logger.info('exiting, execution duration=%s seconds' % (time.time() - eStart))
