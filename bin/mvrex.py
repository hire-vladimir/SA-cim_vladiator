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
from cim_vladiator_common import configure_logger, abort_command, validate_command_args, value_count, option_enabled

#######################################
# SCRIPT CONFIG
#######################################
LOG_FILE_NAME = "mvrex.log"
COMMAND_NAME = "mvrex"

ALLOWED_OPTIONS = ['debug', 'field', 'showunmatched', 'prefix', 'showcount', 'labelfield']
MANDATORY_OPTIONS = ['field']


if __name__ == '__main__':
    logger = configure_logger(LOG_FILE_NAME)
    logger.info('event="command_start" command="%s"', COMMAND_NAME)
    eStart = time.time()
    try:
        results = si.readResults(None, None, False)
        keywords, argvals = si.getKeywordsAndOptions()

        err = validate_command_args(logger, COMMAND_NAME, keywords, argvals, ALLOWED_OPTIONS, MANDATORY_OPTIONS, require_single_keyword=True)
        if err:
            abort_command(logger, COMMAND_NAME, err)

        if option_enabled(argvals, "debug", is_bool=True):
            logger.setLevel(logging.DEBUG)
            logger.debug('event="debug_enabled" command="%s"', COMMAND_NAME)

        regex = keywords[0]
        logger.debug('event="args_resolved" command="%s" regex="%s" field="%s"', COMMAND_NAME, regex, argvals['field'])

        output_column_name = "mvrex"
        if option_enabled(argvals, "labelfield"):
            output_column_name = argvals['labelfield']

        if option_enabled(argvals, "prefix"):
            output_column_name = argvals['prefix'] + output_column_name

        for row in results:
            regex = keywords[0]
            if regex in row:
                regex = row[regex]
                logger.debug('event="regex_substitution" command="%s" regex="%s" field="%s"', COMMAND_NAME, regex, argvals['field'])

            input_data = ""
            if argvals['field'] in row:
                input_data = row[argvals['field']]

            # perform match
            if isinstance(input_data, list):
                logger.debug('event="match_field" command="%s" field="%s" field_type="multivalue"', COMMAND_NAME, argvals['field'])
                row[output_column_name + "_matches"] = [x for x in input_data if re.findall(regex, x)]

                if option_enabled(argvals, "showunmatched", is_bool=True):
                    row[output_column_name + "_unmatched"] = [x for x in input_data if x not in row[output_column_name + "_matches"]]
            else:
                logger.debug('event="match_field" command="%s" field="%s" field_type="single"', COMMAND_NAME, argvals['field'])
                row[output_column_name + "_matches"] = re.findall(regex, input_data)

                if option_enabled(argvals, "showunmatched", is_bool=True) and value_count(row[output_column_name + "_matches"]) == 0:
                    row[output_column_name + "_unmatched"] = input_data
            logger.debug('event="match_complete" command="%s" regex="%s" input="%s" matches="%d"', COMMAND_NAME, regex, input_data, len(row[output_column_name + "_matches"]))

            if option_enabled(argvals, "showcount", is_bool=True):
                row[output_column_name + "_matched_count"] = value_count(row[output_column_name + "_matches"])
                row[output_column_name + "_input_count"] = value_count(input_data)
                if option_enabled(argvals, "showunmatched", is_bool=True):
                    row[output_column_name + "_unmatched_count"] = int(row[output_column_name + "_input_count"]) - int(row[output_column_name + "_matched_count"])

        # logger.debug('event="results" command="%s" results="%s"', COMMAND_NAME, results)
        logger.info('event="command_complete" command="%s" result_count="%d"', COMMAND_NAME, len(results))
        si.outputResults(results)
    except Exception as e:
        logger.exception('event="command_error" command="%s" error="%s"', COMMAND_NAME, e)
        si.generateErrorResults(e)
        raise
    finally:
        logger.info('event="command_end" command="%s" duration_sec="%.3f"', COMMAND_NAME, time.time() - eStart)
