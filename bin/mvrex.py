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
import time, re, logging
import splunk.Intersplunk as si
from cim_vladiator_common import setup_logging, die, validate_args, get_count, arg_on_and_enabled

#######################################
# SCRIPT CONFIG
#######################################
LOG_FILE_NAME = "mvrex.log"

ALLOWED_OPTIONS = ['debug', 'field', 'showunmatched', 'prefix', 'showcount', 'labelfield']
MANDATORY_OPTIONS = ['field']


if __name__ == '__main__':
    logger = setup_logging(LOG_FILE_NAME)
    logger.info('starting..')
    eStart = time.time()
    try:
        results = si.readResults(None, None, False)
        keywords, argvals = si.getKeywordsAndOptions()

        err = validate_args(logger, keywords, argvals, ALLOWED_OPTIONS, MANDATORY_OPTIONS, require_single_keyword=True)
        if err:
            die(logger, "mvrex", err)

        if arg_on_and_enabled(argvals, "debug", is_bool=True):
            logger.setLevel(logging.DEBUG)
            logger.debug("detecting debug argument passed, setting command log_level=DEBUG")

        regex = keywords[0]
        logger.debug('will be applying regex="%s", to field="%s"', regex, argvals['field'])

        output_column_name = "mvrex"
        if arg_on_and_enabled(argvals, "labelfield"):
            output_column_name = argvals['labelfield']

        if arg_on_and_enabled(argvals, "prefix"):
            output_column_name = argvals['prefix'] + output_column_name

        for row in results:
            regex = keywords[0]
            if regex in row:
                regex = row[regex]
                logger.debug('found substitution oppty, will be applying regex="%s", to field="%s"', regex, argvals['field'])

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
            logger.debug('applying regex="%s" to dataset="%s", matches="%d"', regex, input_data, len(row[output_column_name + "_matches"]))

            if arg_on_and_enabled(argvals, "showcount", is_bool=True):
                row[output_column_name + "_matched_count"] = get_count(row[output_column_name + "_matches"])
                row[output_column_name + "_input_count"] = get_count(input_data)
                if arg_on_and_enabled(argvals, "showunmatched", is_bool=True):
                    row[output_column_name + "_unmatched_count"] = int(row[output_column_name + "_input_count"]) - int(row[output_column_name + "_matched_count"])

        # logger.debug('results="%s"' % results)
        logger.info('sending events to splunk count="%d"', len(results))
        si.outputResults(results)
    except Exception as e:
        logger.exception('error while processing events, exception="%s"', e)
        si.generateErrorResults(e)
        raise
    finally:
        logger.info('exiting, execution duration=%s seconds', time.time() - eStart)
