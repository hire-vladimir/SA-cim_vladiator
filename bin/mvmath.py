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
import time, re, logging
import splunk.Intersplunk as si
from cim_vladiator_common import setup_logging, die, validate_args, arg_on_and_enabled

#######################################
# SCRIPT CONFIG
#######################################
LOG_FILE_NAME = "mvmath.log"

ALLOWED_OPTIONS = ['debug', 'field', 'field2', 'labelfield', 'prefix']
MANDATORY_OPTIONS = []


if __name__ == '__main__':
    logger = setup_logging(LOG_FILE_NAME)
    logger.info('starting..')
    eStart = time.time()
    try:
        results = si.readResults(None, None, False)
        keywords, argvals = si.getKeywordsAndOptions()

        err = validate_args(logger, keywords, argvals, ALLOWED_OPTIONS, MANDATORY_OPTIONS)
        if err:
            die(logger, "mvmath", err)

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
                if isinstance(vdata, str) and vdata:
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
