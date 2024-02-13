from copy import deepcopy
from typing import Dict
import sys
import evdev

layout_normal = [list(line) for line in """┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬──────┐
│ ` │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │ 0 │ - │ = │  ⌫   │
├───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬────┤
│ Tab │ Q │ W │ E │ R │ T │ Y │ U │ I │ O │ P │ [ │ ] │ \\  │
├─────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴────┤
│ Caps │ A │ S │ D │ F │ G │ H │ J │ K │ L │ ; │ ' │ Enter │
├──────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴───────┤
│ Shift │ Z │ X │ C │ V │ B │ N │ M │ , │ . │ / │  Shift   │
├─────┬─┴───┼───┴─┬─┴───┴───┴───┴───┴───┴───┴──┬┴────┬─────┤
│ Ctl │ Win │ Alt │            Space           │ Alt │ Ctl │
└─────┴─────┴─────┴────────────────────────────┴─────┴─────┘""".splitlines()]

layout_shifted = [list(line) for line in """┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬──────┐
│ ~ │ ! │ @ │ # │ $ │ % │ ^ │ & │ * │ ( │ ) │ _ │ + │  ⌫   │
├───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬────┤
│ Tab │ Q │ W │ E │ R │ T │ Y │ U │ I │ O │ P │ { │ } │ |  │
├─────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴────┤
│ Caps │ A │ S │ D │ F │ G │ H │ J │ K │ L │ : │ " │ Enter │
├──────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴───────┤
│ Shift │ Z │ X │ C │ V │ B │ N │ M │ < │ > │ ? │  Shift   │
├─────┬─┴───┼───┴─┬─┴───┴───┴───┴───┴───┴───┴──┬┴────┬─────┤
│ Ctl │ Win │ Alt │            Space           │ Alt │ Ctl │
└─────┴─────┴─────┴────────────────────────────┴─────┴─────┘""".splitlines()]

class Key:
    height = 2

    def __init__(self, row: int, left_border_idx: int, width: int):
        right_border_idx = left_border_idx + width - 1
        pixels = []
        for i in range(row * Key.height, row * Key.height + 3):
            for j in range(left_border_idx, right_border_idx + 1):
                pixels += [(i, j)]
        self.pixels = pixels
        self.is_pressed = False

    def press(self):
        self.is_pressed = True

    def unpress(self):
        self.is_pressed = False

keys_dict = {
    "KEY_GRAVE": Key(0, 0, 5),
    "KEY_1": Key(0, 4, 5),
    "KEY_2": Key(0, 8, 5),
    "KEY_3": Key(0, 12, 5), 
    "KEY_4":Key(0, 16, 5), 
    "KEY_5":Key(0, 20, 5), 
    "KEY_6":Key(0, 24, 5), 
    "KEY_7":Key(0, 28, 5), 
    "KEY_8":Key(0, 32, 5), 
    "KEY_9":Key(0, 36, 5), 
    "KEY_0":Key(0, 40, 5), 
    "KEY_MINUS":Key(0, 44, 5), 
    "KEY_EQUAL":Key(0, 48, 5), 
    "KEY_BACKSPACE": Key(0, 52, 8),

    #---------------------------
    "KEY_TAB": Key(1, 0, 7),
    "KEY_Q": Key(1, 6, 5),
    "KEY_W": Key(1, 10, 5),
    "KEY_E": Key(1, 14, 5),
    "KEY_R": Key(1, 18, 5),
    "KEY_T": Key(1, 22, 5),
    "KEY_Y": Key(1, 26, 5),
    "KEY_U": Key(1, 30, 5),
    "KEY_I": Key(1, 34, 5),
    "KEY_O": Key(1, 38, 5),
    "KEY_P": Key(1, 42, 5),
    "KEY_LEFTBRACE": Key(1, 46, 5),
    "KEY_RIGHTBRACE": Key(1, 50, 5),
    "KEY_BACKSLASH": Key(1, 54, 6),

    #---------------------------
    "KEY_CAPSLOCK": Key(2, 0, 8),
    "KEY_A":Key(2, 7, 5),
    "KEY_S":Key(2, 11, 5),
    "KEY_D":Key(2, 15, 5),
    "KEY_F":Key(2, 19, 5),
    "KEY_G":Key(2, 23, 5),
    "KEY_H":Key(2, 27, 5),
    "KEY_J":Key(2, 31, 5),
    "KEY_K":Key(2, 35, 5),
    "KEY_L":Key(2, 39, 5),
    "KEY_SEMICOLON": Key(2, 43, 5),
    "KEY_APOSTROPHE": Key(2, 47, 5),
    "KEY_ENTER": Key(2, 51, 9),

    #---------------------------
    "KEY_LEFTSHIFT": Key(3, 0, 9),
    "KEY_Z": Key(3, 8, 5),
    "KEY_X": Key(3, 12, 5),
    "KEY_C": Key(3, 16, 5),
    "KEY_V": Key(3, 20, 5),
    "KEY_B": Key(3, 24, 5),
    "KEY_N": Key(3, 28, 5),
    "KEY_M": Key(3, 32, 5),
    "KEY_COMMA": Key(3, 36, 5),
    "KEY_DOT": Key(3, 40, 5),
    "KEY_SLASH": Key(3, 44, 5),
    "KEY_RIGHTSHIFT": Key(3, 48, 12),

    #---------------------------
    "KEY_LEFTCTRL": Key(4, 0, 7),
    "KEY_LEFTMETA": Key(4, 6, 7),
    "KEY_LEFTALT": Key(4, 12, 7),
    "KEY_SPACE": Key(4, 18, 30),
    "KEY_RIGHTALT": Key(4, 47, 7),
    "KEY_RIGHTCTRL": Key(4, 53, 7),
}

class Keyboard:
    def __init__(self, keys: Dict[str, Key]):
        self.keys = keys

    def paint_key(self, layout, key: Key):
        INVERT_CLR = "\033[7m"
        RESET_CLR = "\033[0m"
        PAINTED_BLOCK = "\u2588"
        CHARS_TO_BE_COLORED = [" ", "┌", "┐", "└", "┘", "─", "│", "┼", "┬", "┴", "├", "┤"]
        for y, x in key.pixels:
            if layout[y][x] == PAINTED_BLOCK: # char is already colored
                continue
            if any(layout[y][x] == char for char in CHARS_TO_BE_COLORED): # char needs to be colored
                layout[y][x] = PAINTED_BLOCK
            else:
                layout[y][x] = INVERT_CLR + layout[y][x] + RESET_CLR # invert colors for labels

    def draw(self):
        if self.keys["KEY_LEFTSHIFT"].is_pressed or self.keys["KEY_RIGHTSHIFT"].is_pressed:
            result = deepcopy(layout_shifted)
        else:
            result = deepcopy(layout_normal)
        for key in self.keys.values():
            if key.is_pressed:
                self.paint_key(result, key)   
        sys.stdout.write('\033[H')
        print("\n".join("".join(row) for row in result ))

def main():
    device = evdev.InputDevice('/dev/input/event5')
    #print(device)
    kb = Keyboard(keys_dict)
    print('\033c', end='', flush=True)
    kb.draw()
    try:
        for event in device.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                keycode = evdev.ecodes.KEY[event.code]
                if keycode not in kb.keys:
                    continue
                if event.value == 1:
                    kb.keys[keycode].press()
                elif event.value == 0:
                    kb.keys[keycode].unpress()
                kb.draw()
    except KeyboardInterrupt:
        print('\033c', end='', flush=True)

main()

