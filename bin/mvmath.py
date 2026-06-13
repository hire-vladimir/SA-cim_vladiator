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
import time, logging
import splunk.Intersplunk as si
from cim_vladiator_common import configure_logger, abort_command, validate_command_args, option_enabled, safe_pct

#######################################
# SCRIPT CONFIG
#######################################
LOG_FILE_NAME = "mvmath.log"
COMMAND_NAME = "mvmath"

ALLOWED_OPTIONS = ['debug', 'field', 'field2', 'labelfield', 'prefix']
MANDATORY_OPTIONS = []


if __name__ == '__main__':
    logger = configure_logger(LOG_FILE_NAME)
    logger.info('event="command_start" command="%s"', COMMAND_NAME)
    eStart = time.time()
    try:
        results = si.readResults(None, None, False)
        keywords, argvals = si.getKeywordsAndOptions()

        err = validate_command_args(logger, COMMAND_NAME, keywords, argvals, ALLOWED_OPTIONS, MANDATORY_OPTIONS)
        if err:
            abort_command(logger, COMMAND_NAME, err)

        if option_enabled(argvals, "debug", is_bool=True):
            logger.setLevel(logging.DEBUG)
            logger.debug('event="debug_enabled" command="%s"', COMMAND_NAME)

        output_column_name = "mvmath"
        if option_enabled(argvals, "labelfield"):
            output_column_name = argvals['labelfield']

        if option_enabled(argvals, "prefix"):
            output_column_name = argvals['prefix'] + output_column_name

        for row in results:
            if argvals['field'] in row and argvals['field2'] in row:
                vdata = row[argvals['field']]
                tally = row[argvals['field2']]

                if isinstance(vdata, list):
                    res = []
                    skipped = 0
                    for x in vdata:
                        pct = safe_pct(x, tally)
                        if pct is None:
                            skipped += 1
                            res.append("")
                        else:
                            res.append(pct)
                    if skipped:
                        logger.warning(
                            'event="pct_conversion_skipped" command="%s" field="%s" field2="%s" skipped="%d" total="%d"',
                            COMMAND_NAME, argvals['field'], argvals['field2'], skipped, len(vdata))
                else:
                    pct = safe_pct(vdata, tally)
                    if pct is None:
                        logger.warning(
                            'event="pct_conversion_failed" command="%s" field="%s" field2="%s" value="%s" field2_value="%s"',
                            COMMAND_NAME, argvals['field'], argvals['field2'], vdata, tally)
                        pct = ""
                    res = pct

                row[output_column_name + "_result"] = res
                logger.debug('event="pct_computed" command="%s" field="%s" value="%s" field2="%s" field2_value="%s" result="%s"',
                              COMMAND_NAME, argvals['field'], vdata, argvals['field2'], tally, res)

        # logger.debug('event="results" command="%s" results="%s"', COMMAND_NAME, results)
        logger.info('event="command_complete" command="%s" result_count="%d"', COMMAND_NAME, len(results))
        si.outputResults(results)
    except Exception as e:
        logger.exception('event="command_error" command="%s" error="%s"', COMMAND_NAME, e)
        si.generateErrorResults(e)
        raise
    finally:
        logger.info('event="command_end" command="%s" duration_sec="%.3f"', COMMAND_NAME, time.time() - eStart)
