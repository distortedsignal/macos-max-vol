
import collections
import sys

from enum import Enum

class Constants(object):
    TIME_UNIT = 'time_unit'
    TIME_UNIT_SHORT = 'tu'
    TIME_AMOUNT = 'time_amount'
    TIME_AMOUNT_SHORT = 'ta'
    SLEEP_TIME = 'sleep_time'
    MAX_VOLUME = 'max_volume'
    MAX_VOLUME_SHORT = 'mv'
    CONTROL_FILE_PATH = 'control_file_path'
    CONTROL_FILE_PATH_SHORT = 'cfp'
    SCRIPT_FILE = 'max_vol.py'
    DEBUG = 'debug'
    DEBUG_SHORT = 'd'
    SECOND = 'second'
    MINUTE = 'minute'
    MILLISECOND = 'millisecond'

SleepTime = collections.namedtuple('SleepTime', ['time_unit', 'time_amount'])
Options = collections.namedtuple('Options', ['sleep_time', 'max_volume', 'debug'])

class ExitCodes(Enum):
    CONTROL_FILE_READ_FAIL = 1
    MISSING_TIME_UNIT = 2
    MISSING_TIME_AMOUNT = 4
    MISSING_MAX_VOLUME = 8
    INVALID_TIME_UNIT = 16
    INVALID_TIME_AMOUNT = 32
    INVALID_MAX_VOLUME = 64
    GET_VOLUME_FAIL = 128

SIMPLE_RUN_EXAMPLE = f'> python ./{Constants.SCRIPT_FILE}'
LONG_FLAGS_EXAMPLE = f'> python ./{Constants.SCRIPT_FILE} --{Constants.TIME_UNIT} second --{Constants.TIME_AMOUNT} 0.1 --{Constants.MAX_VOLUME} 10 --{Constants.DEBUG} --{Constants.CONTROL_FILE_PATH} ./control.json'
SHORT_FLAGS_EXAMPLE = f'> python ./{Constants.SCRIPT_FILE} -{Constants.TIME_UNIT_SHORT} second -{Constants.TIME_AMOUNT_SHORT} 0.1 -{Constants.MAX_VOLUME_SHORT} 10 -{Constants.DEBUG_SHORT} -{Constants.CONTROL_FILE_PATH_SHORT} ./control.json'
DESCRIPTION_TEXT = '''Set a max volume for MacOS.

This program should be used to set a maximum volume for MacOS volume output.

EXAMPLES:
Start the daemon relying on the included control file.
    ''' + SIMPLE_RUN_EXAMPLE + '''

Start the daemon passing in arguments via flags.
    ''' + LONG_FLAGS_EXAMPLE + '''

Start the daemon passing in arguments via short flags.
    ''' + SHORT_FLAGS_EXAMPLE + '''

The control file should have the following structure:
{
    "''' + Constants.SLEEP_TIME + '''": { "''' + Constants.TIME_UNIT + '''": "''' + Constants.MILLISECOND + '''"|"''' + Constants.SECOND + '''"|"''' + Constants.MINUTE + '''", "''' + Constants.TIME_AMOUNT + '''": [float] },
    "''' + Constants.MAX_VOLUME + '''": [int],
    "''' + Constants.DEBUG + '''": [bool]
}

Any values not specified in the control file must be specified by flags passed into the daemon.

Flags passed in to the daemon will override the control file.
'''

def print_debug(msg: str) -> None:
    print(f'DEBUG: {msg}')

def get_arg_tuple() -> Options:
    args = set_args_and_parse()

    control_dict, exit_code, error_list = get_control_dict_from_file(args)
    
    control_dict, exit_code, error_list = update_control_dict_with_flags(args, exit_code, error_list, control_dict)
    
    exit_code, error_list = validate_options(exit_code, error_list, control_dict)
    
    exit_if_errors(exit_code, error_list)

    if control_dict[Constants.DEBUG]:
        print_debug(f'control_dict: {control_dict}')

    
    return Options(
                    SleepTime(
                                control_dict[Constants.SLEEP_TIME][Constants.TIME_UNIT],
                                control_dict[Constants.SLEEP_TIME][Constants.TIME_AMOUNT]
                    ),
                    control_dict[Constants.MAX_VOLUME],
                    control_dict[Constants.DEBUG]
            )

def set_args_and_parse():
    import argparse

    parser = argparse.ArgumentParser(prog=f"python {Constants.SCRIPT_FILE}",
                                     description=DESCRIPTION_TEXT,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(f'--{Constants.CONTROL_FILE_PATH}', f'-{Constants.CONTROL_FILE_PATH_SHORT}',
                        action='store', metavar=Constants.CONTROL_FILE_PATH, dest=Constants.CONTROL_FILE_PATH, default='./control.json',
                        help='A filepath to use for the control file. Must be a json formatted file with the above specified structure. Defaults to "./control.json"')
    parser.add_argument(f'--{Constants.TIME_UNIT}', f'-{Constants.TIME_UNIT_SHORT}', action='store',
                        metavar=Constants.TIME_UNIT, dest=Constants.TIME_UNIT,
                        help=f'The time unit the program will be expected to wait for. Must be one of "{Constants.MILLISECOND}", "{Constants.SECOND}", or "{Constants.MINUTE}".')
    parser.add_argument(f'--{Constants.TIME_AMOUNT}', f'-{Constants.TIME_AMOUNT}', action='store',
                        metavar=Constants.TIME_AMOUNT, dest=Constants.TIME_AMOUNT, type=float,
                        help='The amount of time the program will be expected to wait for. Must be a positive number.')
    parser.add_argument(f'--{Constants.MAX_VOLUME}', f'-{Constants.MAX_VOLUME_SHORT}', action='store',
                        metavar=Constants.MAX_VOLUME, dest=Constants.MAX_VOLUME, type=int,
                        help='The maximum volume (in percentage) that the OS should report. Must be a positive integer.')
    parser.add_argument(f'--{Constants.DEBUG}', f'-{Constants.DEBUG_SHORT}', action='store_true',
                        help='Enable debug logging from the daemon.')

    return parser.parse_args()

def get_control_dict_from_file(args):
    try:
        with open(args.control_file_path) as f:
            import json
            return json.load(f), 0, []

    except Exception as e:
        import traceback
        print(f'Failed to read control file.', file=sys.stderr)
        print(f'Exception reason: {e.args}', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return {}, ExitCodes.CONTROL_FILE_READ_FAIL, ['Failed to read control file.']

def update_control_dict_with_flags(args, exit_code, error_list, control_dict):
    if (not args.time_unit) and (not control_dict.get(Constants.SLEEP_TIME, {}).get(Constants.TIME_UNIT)):
        exit_code += ExitCodes.MISSING_TIME_UNIT
        error_list.append('Failed to set time unit.')
    elif args.time_unit:
        # It's probably ok to blow away the sleep time if it's not a dict.
        if not (type(control_dict.get(Constants.SLEEP_TIME)) == dict):
            control_dict[Constants.SLEEP_TIME] = {}
        control_dict[Constants.SLEEP_TIME][Constants.TIME_UNIT] = args.time_unit
    
    if (not args.time_amount) and (not control_dict.get(Constants.SLEEP_TIME, {}).get(Constants.TIME_AMOUNT)):
        exit_code += ExitCodes.MISSING_TIME_AMOUNT
        error_list.append('Failed to set time amount.')
    elif args.time_amount:
        # Here we know we already have a SLEEP_TIME dict.
        control_dict[Constants.SLEEP_TIME][Constants.TIME_AMOUNT] = args.time_amount
    
    if (not args.max_volume) and (not control_dict.get(Constants.MAX_VOLUME)):
        exit_code += ExitCodes.MISSING_MAX_VOLUME
        error_list.append('Failed to set max volume.')
    elif args.max_volume:
        control_dict[Constants.MAX_VOLUME] = args.max_volume
    
    control_dict[Constants.DEBUG] = control_dict.get(Constants.DEBUG, False) or args.debug

    return control_dict, exit_code, error_list

def validate_options(exit_code, error_list, control_dict):
    if control_dict[Constants.SLEEP_TIME][Constants.TIME_UNIT] not in ['millisecond', 'second', 'minute']:
        exit_code += ExitCodes.INVALID_TIME_UNIT
        error_list.append(f'Time unit set to invalid value: {control_dict[Constants.SLEEP_TIME][Constants.TIME_UNIT]}')
    
    if control_dict[Constants.SLEEP_TIME][Constants.TIME_AMOUNT] <= 0:
        exit_code += ExitCodes.INVALID_TIME_AMOUNT
        error_list.append(f'Time amount set to less than 0. Value was: {control_dict[Constants.SLEEP_TIME][Constants.TIME_AMOUNT]}')
    
    if control_dict[Constants.MAX_VOLUME] <= 0 or control_dict[Constants.MAX_VOLUME] >= 100:
        exit_code += ExitCodes.INVALID_MAX_VOLUME
        error_list.append(f'Max Volume set to invalid value. Volume must be [0-100], exclusive of the ends. Value was: {control_dict[Constants.MAX_VOLUME]}')
    
    return exit_code, error_list

def exit_if_errors(exit_code, error_list):
    if exit_code > 1:
        # Something went fatally wrong.
        print('FATAL ERROR', file=sys.stderr)
        print('Could not continue program execution.', file=sys.stderr)
        print('Error list:', file=sys.stderr)
        newline_delimited_errors = "\n".join(error_list)
        print(f'{newline_delimited_errors}', file=sys.stderr)
        sys.exit(exit_code)

def loop_sound_monitor(arg_tuple: Options):
    if arg_tuple.debug:
        print_debug(f'Options: {arg_tuple}')
    
    sleep_timer: float = calculate_sleep_timer(arg_tuple.sleep_time)

    if arg_tuple.debug:
        print_debug(f'Sleep timer: {sleep_timer} seconds')
    
    previous_volume: float = 0

    spinner = spinning_cursor()

    import time
    import osascript
    try:
        while True:
            current_volume: float = get_current_volume(osascript, arg_tuple)

            if not arg_tuple.debug:
                sys.stdout.flush()
                sys.stdout.write('\b')
                sys.stdout.write(next(spinner))

            if current_volume > arg_tuple.max_volume:
                set_current_volume(previous_volume, osascript, arg_tuple)
            else:
                previous_volume = current_volume

            time.sleep(sleep_timer)
    except KeyboardInterrupt:
        print()
        print('Exiting...')


def get_current_volume(osascript, arg_tuple) -> float:
    (return_code, return_string, return_error) = osascript.run('get volume settings')
    if return_code != 0:
        print('FATAL ERROR', file=sys.stderr)
        print('Failed to get system volume', file=sys.stderr)
        print(f'Command exit code was: {return_code}', file=sys.stderr)
        print(f'Command output was: {return_string}', file=sys.stderr)
        print(f'Error returned was: {return_error}', file=sys.stderr)
        sys.exit(ExitCodes.GET_VOLUME_FAIL)
    
    if arg_tuple.debug:
        print_debug(f'\n\tReturn code: {return_code}\n\tReturn string: {return_string}\n\tReturn error: {return_error}')
    
    script_out_list = return_string.split(', ')
    [out_vol_line] = list(filter(lambda x: x.startswith('output volume'), script_out_list))
    [_, vol_string] = out_vol_line.split(':')
    if arg_tuple.debug:
        print_debug(f'Current volume: {float(vol_string)}')
    return float(vol_string)

def set_current_volume(volume: float, osascript, arg_tuple: Options) -> None:
    if arg_tuple.debug:
        print_debug(f'Setting volume to {volume}')
    
    (return_code, return_string, return_error) = osascript.run(f'set volume output volume {volume}')
    if return_code != 0:
        print('NON-FATAL ERROR', file=sys.stderr)
        print('Failed to set system volume', file=sys.stderr)
        print(f'Command exit code was: {return_code}', file=sys.stderr)
        print(f'Command output was: {return_string}', file=sys.stderr)
        print(f'Error returned was: {return_error}', file=sys.stderr)
    elif arg_tuple.debug:
        print_debug(f'\n\tReturn code: {return_code}\n\tReturn string: {return_string}\n\tReturn error: {return_error}')

def calculate_sleep_timer(sleep_time: SleepTime) -> float:
    if sleep_time.time_unit == Constants.SECOND:
        return sleep_time.time_amount
    if sleep_time.time_unit == Constants.MILLISECOND:
        return sleep_time.time_amount / 1000.0
    if sleep_time.time_unit == Constants.MINUTE:
        return sleep_time.time_amount * 60

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

def main():
    arg_tuple: Options = get_arg_tuple()

    loop_sound_monitor(arg_tuple)

if __name__ == "__main__":
    main()
