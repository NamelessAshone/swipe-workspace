from pynput.keyboard import Key, Controller, Listener
from libinput import LibInput
from os import access, R_OK
from binascii import b2a_hex
from sys import stdout, exit
from time import localtime

# mykeyboard = Controller()

INTERVAL = 100
THRESHOLD = 10
step = 1


def do_forward():
    global step
    if step == 2:
        do_down()
        do_left()
        step = 3
    elif step == 4:
        do_up()
        do_left()
        step = 1
    else:
        do_right()
        step += 1


def do_backward():
    global step
    if step == 1:
        do_down()
        do_right()
        step = 4
    elif step == 3:
        do_up()
        do_right()
        step = 2
    else:
        do_left()
        step -= 1


def do_left():
    keys = [Key.ctrl, Key.alt, Key.left]
    for k in keys:
        mykeyboard.press(k)
    for k in keys:
        mykeyboard.release(k)


def do_right():
    keys = [Key.ctrl, Key.alt, Key.right]
    for k in keys:
        mykeyboard.press(k)
    for k in keys:
        mykeyboard.release(k)


def do_up():
    keys = [Key.ctrl, Key.alt, Key.up]
    for k in keys:
        mykeyboard.press(k)
    for k in keys:
        mykeyboard.release(k)


def do_down():
    keys = [Key.ctrl, Key.alt, Key.down]
    for k in keys:
        mykeyboard.press(k)
    for k in keys:
        mykeyboard.release(k)


def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(key.char))
    except AttributeError:
        print('special key {0} pressed'.format(key))


def on_release(key):
    print('[{0}] {1} released'.format(step, key))
    if key == Key.esc:
        # Stop listener
        return False


def scan_device(ev):
    '''
        :TODO: refactor this func to a simpler version.
    '''
    if access("/proc/bus/input/devices", R_OK) is False:
        print("permission denied")
        exit(-1)
    with open("/proc/bus/input/devices", "r") as f:
        x = y = pos = -1
        lines = f.read().split("\n")
        for i in range(lines.count("")):
            lines.remove("")
        for l in lines:
            if l[0] == "H":
                pos = l.find("event")
                if pos != -1:
                    l = l[pos:]
                    l = l.split()
                    l = l[0]
                    l = l[len("event"):]
                    x = int(l)
                    pos = -1
            elif l[0] == "B":
                pos = l.find("EV=")
                if pos != -1:
                    l = l[pos:]
                    l = l.split()
                    l = l[0]
                    l = l[len("EV="):]
                    y = int(l, 16)
                    if y == ev:
                        return x
        print(x, y)
    return -1


def timestamp():
    t = localtime()


def clean_old_events(li, direction):
    pass


def handle_pointer_motion(ev):
    src = ev.get_axis_source()
    axis_value = ev.aixs_value(src)
    last_time = t = 0
    t = timestamp()
    if axis_value > THRESHOLD:
        if t > last_time + INTERVAL:
            do_forward()
            last_time = timestamp()
            # clean_old_events(ev., 1)
    elif axis_value < -THRESHOLD:
        if t > last_time + INTERVAL:
            do_backward()
            last_time = timestamp()
            # clean_old_events()


def do_main():
    dev = scan_device(0x0b)
    if dev == -1:
        exit(-1)
    dev_path = "/dev/input/event{0}".format(dev)
    print(dev_path)
    li = LibInput(debug=True)
    device = li.path_add_device(dev_path)
    print(device)
    if device is None:
        print("Get device failed, please check your permissions")
        exit(-1)
    t = 0
    ev_generator = li.get_event()
    while t < 10:
        with open(dev_path, "rb") as f:
            stdout.buffer.write(f.read(1024))
        for ev in ev_generator:
            assert ev.get_device() == device
            if ev.get_device_notify_event is None:
                print("hit device_notify_event")
            if ev.get_keyboard_event is None:
                print("hit keyboard_event")
            if ev.get_switch_event is None:
                print("hit switch_event")
            if ev.get_gesture_event is None:
                print("hit gesture_event")
            if ev.get_pointer_event() is None:
                print("hit pointer_event")
            if ev.tablet_pad_event() is None:
                print("hit tablet_pad_event")
            if ev.tablet_tool_event() is None:
                print("hit tablet_tool_event")
            if ev.touch_event() is None:
                print("hit toch_event")
        t += 1


if __name__ == "__main__":
    # Collect events until released
    # with Listener(on_press=on_press, on_release=on_release) as listener:
        # listener.start()
    do_main()
