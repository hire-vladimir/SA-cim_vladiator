# /usr/bin/env python
welcomeText = '''#
# hire.vladimir@gmail.com
#
# shared helpers for mvrex / mvmath custom search commands
#
# rev. history
# 06/12/26 1.0 initial write - extracted from mvrex.py / mvmath.py
#
'''
import os
import re
import logging
import logging.handlers

LOG_LEVEL = logging.INFO


def configure_logger(log_file_name):
    """Set up a logger that writes to $SPLUNK_HOME/var/log/splunk/<log_file_name>.

    Falls back to a NullHandler (no-op) if SPLUNK_HOME isn't set or the log
    path can't be opened, so logging setup never crashes the command.
    """
    splunk_home = os.environ.get("SPLUNK_HOME")

    log_format = "%(asctime)s %(levelname)-s\t%(module)s[%(process)d]:%(lineno)d - %(message)s"
    logger = logging.getLogger('v')
    logger.setLevel(LOG_LEVEL)

    handler = None
    if splunk_home:
        try:
            log_path = os.path.join(splunk_home, 'var', 'log', 'splunk', log_file_name)
            handler = logging.handlers.RotatingFileHandler(log_path, mode='a', maxBytes=1000000, backupCount=2)
            handler.setFormatter(logging.Formatter(log_format))
        except (OSError, IOError):
            handler = None

    if handler is not None:
        logger.addHandler(handler)
    else:
        logger.addHandler(logging.NullHandler())

    logger.propagate = False
    return logger


def abort_command(logger, prefix, msg):
    logger.error('event="command_abort" command="%s" reason="%s"', prefix, msg)
    exit("%s: %s" % (prefix, msg))


def validate_command_args(logger, command_name, keywords, argvals, allowed_options, mandatory_options=None, require_single_keyword=False):
    """Return an error message string if args are invalid, else None."""
    mandatory_options = mandatory_options or []
    logger.info('event="validate_args" command="%s" keywords="%s" args="%s"', command_name, keywords, argvals)

    if require_single_keyword and len(keywords) != 1:
        return "One argument needs be specified; see command for usage details. Arguments passed: %d" % len(keywords)

    if len([x for x in argvals if x in mandatory_options]) < len(mandatory_options):
        return "Insufficient number of mandatory arguments found. Mandatory argumets are: %s" % (mandatory_options,)

    illegal_args = [x for x in argvals if x not in allowed_options]
    if len(illegal_args) != 0:
        return "The argument(s) '%s' is invalid. Supported arguments are: %s" % (illegal_args, allowed_options)

    return None


def value_count(d):
    # this will take care of cases when no mv is involved
    if isinstance(d, list):
        ret = len(d)
        if ret == 1 and not d[0]:
            ret = 0
    else:
        ret = 1
    return ret


def option_enabled(argvals, arg, rex=None, is_bool=False):
    result = False
    if is_bool:
        rex = "^(?:t|true|1|yes)$"

    if (rex is None and arg in argvals) or (arg in argvals and re.match(rex, argvals[arg])):
        result = True
    return result


def safe_pct(numerator, denominator):
    """Return numerator/denominator formatted as a percentage string, or
    None if the inputs aren't usable numbers (non-numeric, denominator is
    zero, etc.). Callers should treat None as "couldn't compute" and decide
    how to represent that for the row, rather than letting the exception
    propagate and abort the whole command."""
    try:
        return "{:.2%}".format(float(numerator) / float(denominator))
    except (ValueError, ZeroDivisionError, TypeError):
        return None
