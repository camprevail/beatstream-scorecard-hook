import ctypes
from dataclasses import dataclass
from bytechomp.datatypes import I32, I8
import time


@dataclass
class StageData:
    music_id: I32
    music_grade: I32
    unk1: I32
    unk2: I32
    unk3: I32
    gauge: I32
    score: I32
    max_combo: I32
    unk4: I32
    medal: I32
    fanta: I32
    great: I32
    fine: I32
    miss: I32
    # placeholders to be filled later
    datecode: I8
    stage_no: I8
    music_title: I8
    artist_name: I8
    music_level: I8
    play_count: I8
    best_score: I8
    best_medal: I8
    is_new_record: I8
    player_name: I8
    beast_rank: I8


class CooldownTimer:
    def __init__(self, cooldown_duration):
        self.cooldown_duration = cooldown_duration
        self.last_used_time = 0

    def reset(self):
        self.last_used_time = time.time()

    def is_ready(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_used_time
        return elapsed_time >= self.cooldown_duration

    def remaining_time(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_used_time
        remaining_time = max(0, self.cooldown_duration - elapsed_time)
        return remaining_time

def pid_from_window(windowName):
    hwnd = ctypes.windll.user32.FindWindowW(windowName, None)

    if hwnd:
        process_id = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
        return process_id.value
    else:
        return None

def char_from_vk_code(vk_code):
    scan_code = ctypes.windll.user32.MapVirtualKeyW(vk_code, 0)
    buf = ctypes.create_unicode_buffer(32)
    ctypes.windll.user32.GetKeyNameTextW(scan_code << 16, buf, 32)
    return buf.value


def music_level_to_int(pm, CMusicInfoData, music_id, music_type):
    mtype = music_type
    m_id = music_id

    if music_id == -1 or mtype == -1:
        return -1

    if music_id < 0 or music_id >= pm.read_int(CMusicInfoData+24):
        m_id = 0

    v6 = pm.read_longlong(CMusicInfoData+16)
    v7 = pm.read_longlong(v6+8)
    while not pm.read_bool(v7+1713):
        # scan the db for music ids
        a = pm.read_int(v7 + 24) # music id
        if a >= m_id:
            v6 = v7
            v7 = pm.read_longlong(v7)
        else:
            v7 = pm.read_longlong(v7+16)

    v8 = pm.read_longlong(CMusicInfoData+16)

    if v6 != v8 and m_id >= pm.read_int(v6+24):
        result = pm.read_int(v6 + (mtype<<2) + 168)
        # print(f'v6: {hex(v6)}')
    else:
        result = pm.read_int(v8 + (mtype<<2) + 168)
        # print(f'v8: {hex(v8)}')

    return result

def get_title_from_int(pm, CMusicInfoData, music_id):
    m_id = music_id

    if music_id < 0 or music_id >= pm.read_int(CMusicInfoData+24):
        m_id = 0

    v6 = pm.read_longlong(CMusicInfoData+16)
    v7 = pm.read_longlong(v6+8)
    while not pm.read_bool(v7+1713):
        # scan the db for music ids
        a = pm.read_int(v7 + 24) # music id
        if a >= m_id:
            v6 = v7
            v7 = pm.read_longlong(v7)
        else:
            v7 = pm.read_longlong(v7+16)

    v8 = pm.read_longlong(CMusicInfoData+16)

    if v6 != v8 and m_id >= pm.read_int(v6+24):
        addr = v6
        # print(f'v6: {hex(v6)}')
    else:
        addr = v8
#         print(f'v8: {hex(v8)}')

    str_loc = addr+40
    v9 = pm.read_int(str_loc+24)
    if v9 >= 16:
        title_ptr = pm.read_longlong(str_loc)
    else:
        title_ptr = str_loc
    result = pm.read_string(title_ptr, 129, encoding='shift-jis')

    return result

def get_artist_from_int(pm, CMusicInfoData, music_id):
    m_id = music_id

    if music_id < 0 or music_id >= pm.read_int(CMusicInfoData+24):
        m_id = 0

    v6 = pm.read_longlong(CMusicInfoData+16)
    v7 = pm.read_longlong(v6+8)
    while not pm.read_bool(v7+1713):
        # scan the db for music ids
        a = pm.read_int(v7 + 24) # music id
        if a >= m_id:
            v6 = v7
            v7 = pm.read_longlong(v7)
        else:
            v7 = pm.read_longlong(v7+16)

    v8 = pm.read_longlong(CMusicInfoData+16)

    if v6 != v8 and m_id >= pm.read_int(v6+24):
        addr = v6
    else:
        addr = v8

    str_loc = addr+120
    v9 = pm.read_int(str_loc+24)
    if v9 >= 16:
        title_ptr = pm.read_longlong(str_loc)
    else:
        title_ptr = str_loc
    result = pm.read_string(title_ptr, 129, encoding='shift-jis')

    return result

def musicinfodata_get(pm, CMusicInfoData, m_id, mtype, datatype:str):

    if m_id < 0 or m_id >= pm.read_int(CMusicInfoData+24):
        m_id = 0

    v6 = pm.read_longlong(CMusicInfoData+16)
    v7 = pm.read_longlong(v6+8)
    while not pm.read_bool(v7+1713):
        # scan the db for music ids
        a = pm.read_int(v7 + 24) # music id
        if a >= m_id:
            v6 = v7
            v7 = pm.read_longlong(v7)
        else:
            v7 = pm.read_longlong(v7+16)

    v8 = pm.read_longlong(CMusicInfoData+16)

    if v6 != v8 and m_id >= pm.read_int(v6+24):
        addr = v6
        # print(f'v6: {hex(v6)}')
    else:
        addr = v8
        # print(f'v8: {hex(v8)}')

    dtypes = {
        'music_level_int': 168,
        'play_count': 1188,
        'clear_count': 1204,
        'best_gauge': 1220,
        'best_score': 1236,
        'best_medal': 1268,
    }

    final_addr = (addr + (mtype<<2)) + dtypes.get(datatype)
    # print(f'final_addr =  {hex(final_addr)}')
    return pm.read_int(final_addr)

