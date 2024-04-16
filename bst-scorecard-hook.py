import welcome_version
import configutils
from configutils import config
from osd import tOSD
import pymem
from bytechomp import Reader
import utils
import os
import sys
import pynput
from pynput.keyboard import Listener
from pprint import pprint
from lxml import etree
from lxml.builder import E
from dataclasses import asdict
import requests
import traceback
import aiohttp
import asyncio
import psutil
import time
from constants import *


# Prevent multiple instances
exe = os.path.basename(sys.executable)
ls = []
for p in psutil.process_iter(['name']):
    if p.info['name'] != 'python.exe' and p.info['name'] == exe:
        ls.append(p)
if len(ls) > 2:
    print('Another instance is already running. Exiting.')
    time.sleep(3)
    sys.exit()


def get_stagedata(stage=None):
    pid = utils.pid_from_window("Beatstream")
    if pid:
        pm = pymem.Pymem(pid)
    else:
        raise ProcessLookupError('Could not find game window.')

    offset_datecode = 0x180AAE728
    offset_CMusicInfoData = 0x1816C47C8
    offset_CGameFullStageData = 0x1816C47D8
    offset_CPlayerInfoGameData = 0x1816C4778

    model = pm.read_string(offset_datecode)
    dest = pm.read_string(offset_datecode+4)
    spec = pm.read_string(offset_datecode+6)
    rev = pm.read_string(offset_datecode+8)
    ext = pm.read_string(offset_datecode+10)
    datecode = f'{model}:{dest}:{spec}:{rev}:{ext}'

    ptr_CGameFullStageData = pm.read_longlong(offset_CGameFullStageData)
    ptr_CMusicInfoData = pm.read_longlong(offset_CMusicInfoData)
    ptr_playerinfo = pm.read_longlong(offset_CPlayerInfoGameData)
    ptr_stagedata = pm.read_longlong(ptr_CGameFullStageData+8)
    stage_no = pm.read_int(ptr_CGameFullStageData + 16)

    if stage is not None:
        stage_no = stage
    stagedata_loc = ptr_stagedata + (stage_no * 56)
    # print(f'ptr_stagedata={hex(ptr_stagedata)}')
    stagedata_bytes = pm.read_bytes(stagedata_loc, 56)
    stagedata_bytes += b'\x00' * 11 # to make the reader happy
    reader = Reader[utils.StageData]().allocate()
    try:
        reader.feed(stagedata_bytes)
        if reader.is_complete():
            stagedata = reader.build()
        else:
            raise RuntimeError('Not enough bytes for dataclass reader!')
    except Exception as e:
        pprint(e)

    if stagedata.music_id == -1:
        osd_message("No stage data available.")
        raise RuntimeWarning("No stage data available.")
    if stagedata.fanta + stagedata.great + stagedata.fine + stagedata.miss == 0:
        osd_message("Stage data incomplete.")
        raise RuntimeWarning("Stage data incomplete.")

    stagedata.datecode = datecode
    stagedata.stage_no = stage_no
    stagedata.music_title = utils.get_title_from_int(pm, ptr_CMusicInfoData, stagedata.music_id)
    stagedata.artist_name = utils.get_artist_from_int(pm, ptr_CMusicInfoData, stagedata.music_id)
    stagedata.music_level = utils.musicinfodata_get(pm, ptr_CMusicInfoData, stagedata.music_id, stagedata.music_grade, 'music_level_int')
    if stagedata.music_level == 14: stagedata.music_level = 99
    stagedata.play_count = utils.musicinfodata_get(pm, ptr_CMusicInfoData, stagedata.music_id, stagedata.music_grade, 'play_count')
    stagedata.best_score = utils.musicinfodata_get(pm, ptr_CMusicInfoData, stagedata.music_id, stagedata.music_grade, 'best_score')
    stagedata.best_medal = utils.musicinfodata_get(pm, ptr_CMusicInfoData, stagedata.music_id, stagedata.music_grade, 'best_medal')
    stagedata.is_new_record = int(stagedata.play_count > 0 and stagedata.score >= 500000 and stagedata.score > stagedata.best_score)
    stagedata.player_name = pm.read_string(ptr_playerinfo+8, 17, encoding='shift-jis')
    stagedata.beast_rank = int.from_bytes(pm.read_bytes(ptr_playerinfo + 25, 1), 'little', signed=True)

    return stagedata


cooldown_timer = utils.CooldownTimer(cooldown_duration=5)
new_keymap = {'current stage': None, 'stage 1': None, 'stage 2': None, 'stage 3': None, 'stage 4': None}
restart_keymap = new_keymap.copy()
map_enable = True

def on_press(key):
    if isinstance(key, pynput.keyboard.Key):
        #special keys
        keycode = key.value.vk
    else:
        keycode = key.vk

    # Press ESC to quit
    if keycode == pynput.keyboard.Key.esc.value.vk:
        return False

    # Press MAP_KEY_NAME to start key mapper
    if keycode == MAP_KEY_CODE:
        print('Key Mapper enabled. Press ESC to cancel at any time.')
        global map_enable
        global new_keymap
        map_enable = True
        for k, v in new_keymap.items():
            if v is None:
                # attempt to map a key
                print(f'Press a key to remap "{k}": ', end='')
                sys.stdout.flush()
                with Listener(on_press=map_key) as map_listener:
                    map_listener.join()
                if map_enable is False:
                    new_keymap = restart_keymap.copy()
                    break
        if None in new_keymap.values():
            # Mapping was terminated early by the user
            return
        else:
            # Update keymap
            for k, v in new_keymap.items():
                config['Keybinds'][k] = str(v)
            configutils.update_file()
            print('\nMapping complete. Changes saved to config.ini.')
            configutils.print_current_keymap()
            map_enable = False
            new_keymap = restart_keymap.copy()


    cs = config['Keybinds'].getint('current stage')
    s1 = config['Keybinds'].getint('stage 1')
    s2 = config['Keybinds'].getint('stage 2')
    s3 = config['Keybinds'].getint('stage 3')
    s4 = config['Keybinds'].getint('stage 4')

    keymap = {cs: None, s1: 0, s2: 1, s3: 2, s4: 3}

    if keycode in keymap.keys():
        if cooldown_timer.is_ready():
            try:
                i = list(keymap.keys()).index(keycode)
                if i == 0:
                    i = 'current'
                print(f'Grabbing data for stage {i}')
                stagedata = get_stagedata(keymap[keycode])
                if config['Misc'].getboolean('print stagedata'):
                    pprint(stagedata)
                filename, image = generate_scorecard(stagedata)
                save_image(filename, image)
                if config['Misc'].getboolean('discord upload'):
                    print('Starting discord upload')
                    asyncio.run(upload_image(filename, image))
                cooldown_timer.reset()
            except Exception as e:
                exception_handler(e)
        else:
            print(f'Slow down! {cooldown_timer.cooldown_duration} seconds between calls.')


def generate_scorecard(stagedata):
    call = E.call(E.info2(method="result_image_write"), model=stagedata.datecode)
    info2 = call.find('info2')
    for k, v in asdict(stagedata).items():
        if k.startswith('unk') or k == 'datecode':
            continue
        etree.SubElement(info2, k).text = str(v)
    data = etree.tostring(call, encoding='UTF-8', xml_declaration=True)
    url = config['Misc'].get('scorecard generator url')
    r = requests.post(url, data=data)
    if r.status_code == 200:
        filename = r.headers['content-disposition'].split('filename=')[1].strip('"')
        return filename, r.content
    else:
        osd_message('Scorecard failed')
        raise RuntimeWarning(f"Failed to download scorecard: {r.status_code}")


def save_image(filename, image):
    if config['Misc'].getboolean('save images'):
        savepath = config['Misc'].get('image folder', fallback='./scorecards')
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        with open(f'{savepath}/{filename}', 'wb') as f:
            f.write(image)
            print(f'Image saved to {savepath}/{filename}')
            osd_message('Scorecard saved')


async def upload_image(filename, image):
    webhook_url = config['Misc']['discord webhook url']
    if webhook_url:
        try:
            async with aiohttp.ClientSession() as session:
                form_data = aiohttp.FormData()
                form_data.add_field('image/png', image, filename=filename)
                async with session.post(webhook_url, data=form_data) as response:
                    if response.status == 200:
                        print("Discord uploaded successful")
                        if not config['Misc'].getboolean('save images'):
                            osd_message('Scorecard uploaded')
                    else:
                        text = await response.text()
                        raise RuntimeError(f'Discord upload failed. Reason: {response.status} {text}')
        except Exception as e:
            raise RuntimeError(f"An error occurred during image upload: {repr(e)}")
    else:
        raise RuntimeWarning('Discord webhook url is empty!')


def osd_message(message):
    if config['Misc'].getboolean('enable OSD'):
        osd = tOSD()
        if not osd.find_window():
            print("OSD window not found!")
            return

        interval = config['Misc'].getint('OSD duration')
        sent = osd.send_message(message, interval)
        if not sent:
            print("Failed to send OSD message.")


def map_key(key):
    if isinstance(key, pynput.keyboard.Key):
        #special keys
        keycode = key.value.vk
    else:
        keycode = key.vk

    # Press ESC to quit
    if keycode == pynput.keyboard.Key.esc.value.vk:
        global map_enable
        map_enable = False
        print('\nKey mapping cancelled. No changes made.')
        return False

    global new_keymap
    # map a single key
    for k, v in new_keymap.items():
        if v is None:
            if keycode == MAP_KEY_CODE:
                print(f'{MAP_KEY_NAME} is reserved for the key mapper function. Try again.\nWaiting for input for {k}: ', end='')
                return
            if keycode in new_keymap.values():
                print(f'Duplicate keys not allowed. Try again.\nWaiting for input for {k}: ', end='')
                return
            print(f'{key}')
            new_keymap[k] = keycode
            return False


def exception_handler(e):
    if isinstance(e, ProcessLookupError):
        print('Could not find game window.')
    elif isinstance(e, pymem.exception.CouldNotOpenProcess):
        print(f'{e} Are you running as admin?')
    elif isinstance(e, RuntimeError):
        print(repr(e))
    elif isinstance(e, RuntimeWarning):
        print(e)
    else:
        traceback.print_exception(e)


#Main loop
print('Ready')
with Listener(on_press=on_press) as listener:
    listener.join()