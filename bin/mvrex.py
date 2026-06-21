# /usr/bin/env python
welcomeText = '''#
# hire.vladimir@gmail.com
#
# allow regex matches on MV fields + passing in regex values via field/token
#
'''
import time, re, logging
import splunk.Intersplunk as si
from cim_vladiator_common import (
    configure_logger,
    abort_command,
    validate_command_args,
    value_count,
    option_enabled,
    validate_strict_ip,
    validate_polymorphic_ip,
    derive_validation_mode,
    MAX_SAMPLE_LENGTH,
)

#######################################
# SCRIPT CONFIG
#######################################
LOG_FILE_NAME = "mvrex.log"
COMMAND_NAME = "mvrex"

ALLOWED_OPTIONS = ['debug', 'field', 'showunmatched', 'prefix', 'showcount', 'labelfield', 'parseip']
MANDATORY_OPTIONS = ['field']


def _stage2_passes(value, validation_mode):
    if validation_mode == 'ip_strict':
        return validate_strict_ip(value)
    if validation_mode == 'ip_polymorphic':
        return validate_polymorphic_ip(value)
    return True


def _normalize_sample_value(value):
    if value is None:
        return ''
    if not isinstance(value, str):
        return str(value)
    return value


def _stage1_passes(regex, value, validation_mode):
    if validation_mode in ('ip_strict', 'ip_polymorphic'):
        if len(value) > MAX_SAMPLE_LENGTH:
            return False
        return bool(re.fullmatch(regex, value))
    return bool(re.findall(regex, value))


def _element_passes(regex, value, validation_mode):
    value = _normalize_sample_value(value)
    if not _stage1_passes(regex, value, validation_mode):
        return False
    if validation_mode in ('ip_strict', 'ip_polymorphic'):
        return _stage2_passes(value, validation_mode)
    return True


def process_mvrex_row(row, regex_field_key, sample_field, output_column_name, argvals):
    regex = regex_field_key
    if regex_field_key in row:
        regex = row[regex_field_key]

    parse_enabled = option_enabled(argvals, 'parseip', is_bool=True)
    validation_mode = derive_validation_mode(
        row.get('field', ''),
        row.get('datamodel', ''),
        parse_enabled,
    )
    input_data = row.get(sample_field, '')

    if isinstance(input_data, list):
        row[output_column_name + "_matches"] = [
            x for x in input_data if _element_passes(regex, x, validation_mode)
        ]
        if option_enabled(argvals, "showunmatched", is_bool=True):
            row[output_column_name + "_unmatched"] = [
                x for x in input_data if x not in row[output_column_name + "_matches"]
            ]
    else:
        if validation_mode in ('ip_strict', 'ip_polymorphic'):
            row[output_column_name + "_matches"] = (
                [input_data] if _element_passes(regex, input_data, validation_mode) else []
            )
        else:
            row[output_column_name + "_matches"] = re.findall(
                regex, _normalize_sample_value(input_data)
            )

        if option_enabled(argvals, "showunmatched", is_bool=True) and value_count(row[output_column_name + "_matches"]) == 0:
            row[output_column_name + "_unmatched"] = input_data

    if option_enabled(argvals, "showcount", is_bool=True):
        row[output_column_name + "_matched_count"] = value_count(row[output_column_name + "_matches"])
        row[output_column_name + "_input_count"] = value_count(input_data)
        if option_enabled(argvals, "showunmatched", is_bool=True):
            row[output_column_name + "_unmatched_count"] = (
                int(row[output_column_name + "_input_count"]) - int(row[output_column_name + "_matched_count"])
            )


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

        logger.debug('event="args_resolved" command="%s" regex="%s" field="%s"', COMMAND_NAME, keywords[0], argvals['field'])

        output_column_name = "mvrex"
        if option_enabled(argvals, "labelfield"):
            output_column_name = argvals['labelfield']

        if option_enabled(argvals, "prefix"):
            output_column_name = argvals['prefix'] + output_column_name

        for row in results:
            regex_field_key = keywords[0]
            logger.debug(
                'event="regex_substitution" command="%s" regex="%s" field="%s"',
                COMMAND_NAME,
                row.get(regex_field_key, regex_field_key),
                argvals['field'],
            )
            process_mvrex_row(row, regex_field_key, argvals['field'], output_column_name, argvals)
            input_data = row.get(argvals['field'], '')
            logger.debug(
                'event="match_complete" command="%s" regex="%s" input="%s" matches="%d"',
                COMMAND_NAME,
                row.get(regex_field_key, regex_field_key),
                input_data,
                len(row.get(output_column_name + "_matches", [])),
            )

        logger.info('event="command_complete" command="%s" result_count="%d"', COMMAND_NAME, len(results))
        si.outputResults(results)
    except Exception as e:
        logger.exception('event="command_error" command="%s" error="%s"', COMMAND_NAME, e)
        si.generateErrorResults(e)
        raise
    finally:
        logger.info('event="command_end" command="%s" duration_sec="%.3f"', COMMAND_NAME, time.time() - eStart)