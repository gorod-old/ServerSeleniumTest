import inspect

from colorama import Fore, Style


def print_exception_msg(msg: str = '', stream: int = None):
    func = inspect.stack()[1].function
    location = f'in {func}' if func else ''
    stream = Fore.BLUE + f' [{stream}]' if stream else ''
    print(Fore.MAGENTA + '[ERROR]' + stream, Fore.CYAN + location,
          Style.RESET_ALL + f'{msg}')


def print_info_msg(msg: str = '', stream: int = None):
    func = inspect.stack()[1].function
    location = f'in {func}' if func else ''
    stream = Fore.BLUE + f' [{stream}]' if stream else ''
    print(Fore.YELLOW + '[INFO]' + stream, Fore.CYAN + location,
          Style.RESET_ALL + f'{msg}')


def print_progress_msg(msg: str = ''):
    print(Fore.BLUE + '[PROGRESS]', Style.RESET_ALL + f'{msg}')
    print('________________________________________________________')
