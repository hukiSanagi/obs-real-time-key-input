import obspython as obs

from pynput import keyboard

import threading
import time

# フラグの初期化
stop_flag = threading.Event()

listener_thread = None
text_name = ""

def script_description():
    return "キー入力をリアルタイムで受け取るスクリプトです。テストとして選択したText Sourceに入力キーが表示されるようになっています。"

def script_properties():
    props = obs.obs_properties_create()

    text_properties = obs.obs_properties_add_list(props, "text", "Text Source", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)

    sources = obs.obs_enum_sources()
    for source in sources:
        source_id = obs.obs_source_get_unversioned_id(source)
        if source_id == "text_gdiplus":
            name = obs.obs_source_get_name(source)
            obs.obs_property_list_add_string(text_properties, name, name)

    obs.source_list_release(sources)

    return props

def script_update(settings):
    global text_name
    
    text_name = obs.obs_data_get_string(settings, "text")

def start_listener():
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    # 定期的に停止フラグをチェック
    while not stop_flag.is_set():
        time.sleep(0.1)  

    listener.stop()

def on_press(key):    
    try:
        print("input_key:", str(key))
        
        text_source = obs.obs_get_source_by_name(text_name)
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", str(key))
        obs.obs_source_update(text_source, settings)
        obs.obs_source_release(text_source)

    except AttributeError:
        pass
    
def on_release(key):
    pass

def script_load(settings):
    print("Script loaded")

    global listener_thread
    listener_thread = threading.Thread(target=start_listener, daemon = True)
    listener_thread.start()

def script_unload():
    print("Script unloaded")    

    global stop_flag, listener_thread

    # 停止フラグをセットしてリスナースレッドを終了
    stop_flag.set()
    if listener_thread is not None:
        listener_thread.join()