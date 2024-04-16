import configparser
import os
import sys
from time import sleep
from utils import char_from_vk_code
from constants import MAP_KEY_CODE, MAP_KEY_NAME


def print_current_keymap():
    # Print current keymap
    print('Current key bindings:')
    for k, v in config['Keybinds'].items():
        print(f'{k}: {char_from_vk_code(int(v))}')
    print()

def quit():
    sleep(4)
    os.system('cmd /k')
    sys.exit()


# Determine if the application is a frozen `.exe` (e.g. pyinstaller --onefile)
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
# or a script file (e.g. `.py` / `.pyw`)
elif __file__:
    application_path = os.path.dirname(__file__)

os.chdir(application_path)

config = configparser.ConfigParser(allow_no_value=True)
config.optionxform = str

if not os.path.isfile('config.ini'):
    print('config.ini missing! Creating with default values. Configure the URL and restart as admin.\n')
    config.add_section('Keybinds')
    config.set('Keybinds', f'# Keycode ints. Press {MAP_KEY_NAME} in the running program to bind keys or use')
    config.set('Keybinds', '# the lookup table here https://xoax.net/sub_javascript/ref_core/apx_key_code_table/')
    config.set('Keybinds', '# Mapped to Space, 1, 2, 3, 4, by default.')
    config.set('Keybinds', 'current stage', '32')
    config.set('Keybinds', 'stage 1', '49')
    config.set('Keybinds', 'stage 2', '50')
    config.set('Keybinds', 'stage 3', '51')
    config.set('Keybinds', 'stage 4', '52')

    config['Misc'] = {
        'scorecard generator url': 'http://changeme',
        'save images': 'True',
        'image folder': './scorecards',
        'discord upload': 'False',
        'discord webhook url': '',
        'enable OSD': 'True',
        'OSD duration': '120',
        'print stagedata': 'False'
    }

    with open('config.ini', 'w') as f:
        config.write(f)
        quit()

else:
    config.read('config.ini')
    # print('Loaded config.ini')
    # Verify there are no duplicate key mappings
    values = list(config['Keybinds'].values())
    if any(values.count(x) > 1 for x in values):
        print('Duplicate keybind values detected in config.ini.\nPlease resolve and '
              'restart the program as admin.\n')
        quit()
    if str(MAP_KEY_CODE) in values:
        print(f'{MAP_KEY_NAME}: {MAP_KEY_CODE} is reserved.\nPlease resolve and '
              'restart the program as admin.\n')

    url = config['Misc']['scorecard generator url']
    if not url or url == 'http://changeme':
        print('Scorecard generator URL not configured in config.ini!\nPlease configure and '
              'restart the program as admin.\n')
        quit()

    if config['Misc'].getboolean('discord upload') and not config['Misc']['discord webhook url']:
        print('Discord upload enabled but no webhook url is set!\nPlease configure and '
              'restart the program as admin.\n')

    print_current_keymap()


def update_file():
    # Gotta do some stupid shit to keep comments
    newconfig = configparser.ConfigParser(allow_no_value=True)
    newconfig.optionxform = str
    newconfig.add_section('Keybinds')
    newconfig.set('Keybinds', f'# Keycode ints. Press {MAP_KEY_NAME} in the running program to bind keys or use')
    newconfig.set('Keybinds', '# the lookup table here https://xoax.net/sub_javascript/ref_core/apx_key_code_table/')
    newconfig.set('Keybinds', '# Mapped to Space, 1, 2, 3, 4, by default.')
    newconfig._sections['Keybinds'].update(config._sections['Keybinds'])
    newconfig.add_section('Misc')
    newconfig._sections['Misc'].update(config._sections['Misc'])

    with open('config.ini', 'w') as f:
        newconfig.write(f)
