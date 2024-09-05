import time
from machine import Pin, SoftI2C
import ssd1306

# ESP32 Pin assignment
# first is SCL
# second is SDA
i2c_north = SoftI2C(scl=Pin(32), sda=Pin(33))
i2c_south = SoftI2C(scl=Pin(23), sda=Pin(27))
i2c_east = SoftI2C(scl=Pin(4), sda=Pin(5)) # 5 is sketchy

oled_width = 128
oled_height = 64
oled_tram_north = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c_north)
oled_tram_south = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c_south)
oled_tram_east = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c_east)

pin_button_north_in = Pin(13, mode=Pin.IN, pull=Pin.PULL_DOWN)
pin_button_north_out = Pin(14, mode=Pin.IN, pull=Pin.PULL_DOWN)

pin_button_south_in = Pin(16, mode=Pin.IN, pull=Pin.PULL_DOWN)
pin_button_south_out = Pin(17, mode=Pin.IN, pull=Pin.PULL_DOWN)

pin_button_east_in = Pin(12, mode=Pin.IN, pull=Pin.PULL_DOWN)
pin_button_east_out = Pin(15, mode=Pin.IN, pull=Pin.PULL_DOWN)

pin_led_north_green = Pin(18, mode=Pin.OUT)
pin_led_north_red = Pin(19, mode=Pin.OUT)

pin_led_south_green = Pin(21, mode=Pin.OUT)
pin_led_south_red = Pin(22, mode=Pin.OUT)

pin_led_east_green = Pin(25, mode=Pin.OUT)
pin_led_east_red = Pin(26, mode=Pin.OUT)

phase_time = 20

oled_tram_north.fill(0)
oled_tram_north.text("Hello World!", 0, 0)
oled_tram_north.show()

oled_tram_south.fill(0)
oled_tram_south.text("Hello World!", 0, 0)
oled_tram_south.show()

oled_tram_east.fill(0)
oled_tram_east.text("Hello World!", 0, 0)
oled_tram_east.show()

# oled parameters:
# oled.framebuf.fill_rect(x, y, width, height, color)

north_info = ""
south_info = ""
east_info = ""

def tram_go(time_left_in_phase: int, oled: ssd1306.SSD1306_I2C, information: str, go_in_next: bool = False):
    oled.fill(0)
    oled.framebuf.fill_rect(50, 0, 16, 40, 1)
    if(time_left_in_phase < 10 and not go_in_next):
        oled.text(f"Red in: {time_left_in_phase}", 0, 50)
    else:
        oled.text(information, 0, 50)
    oled.show()

def tram_stop(time_left_in_phase: int, oled: ssd1306.SSD1306_I2C, go_in_next: bool = False):
    oled.fill(0)
    oled.framebuf.fill_rect(14, 10, 100, 16, 1)
    if(time_left_in_phase < 10):
        if go_in_next:
            oled.text(f"Go in: {time_left_in_phase}", 0, 50)
    oled.show()

# 1. north
# 2. south
# 3. east

# green/red - front/left/right/dont
# 0) 1g 2r 3r - 1fl 2x 3x - caution - cars front!
# 1) 1g 2g 3r - 1f 2f 3x - only forwards!
# 2) 1r 2g 3r - 1x 2fr 3x - caution - cars right!
# 3) 1r 2r 3r - 1x 2x 3lr
# 4) 1r 2r 3g - 1x 2x 3lr - caution - cars right!

# programmed sample routes:
# if north_in pressed, go to phase 0 after 10 seconds, freeze time
# if north_out pressed, go to phase 1 after 5 seconds, unfreeze time

# if south_in pressed, go to phase 2 after 10 seconds, freeze time
# if south_out pressed, go to phase 3 after 5 seconds, unfreeze time

# if east_in pressed, go to phase 3 after 10 seconds, freeze time
# if east_out pressed, go to phase 2 after 0 seconds, unfreeze time

def phase_0(time_left_in_phase: int):
    pin_led_north_green.on()
    pin_led_north_red.off()
    north_tram_green = True

    pin_led_south_green.off()
    pin_led_south_red.on()
    south_tram_green = False

    pin_led_east_green.off()
    pin_led_east_red.on()
    east_tram_green = False
    tram_go(time_left_in_phase, oled_tram_north, "Cars front!", go_in_next=True)
    tram_stop(time_left_in_phase, oled_tram_south, go_in_next=True)
    tram_stop(time_left_in_phase, oled_tram_east, go_in_next=False)

def phase_1(time_left_in_phase: int):
    pin_led_north_green.on()
    pin_led_north_red.off()
    north_tram_green = True

    pin_led_south_green.on()
    pin_led_south_red.off()
    south_tram_green = True

    pin_led_east_green.off()
    pin_led_east_red.on()
    east_tram_green = False
    tram_go(time_left_in_phase, oled_tram_north, "Only forwards!", go_in_next=False)
    tram_go(time_left_in_phase, oled_tram_south, "Only forwards!", go_in_next=True)
    tram_stop(time_left_in_phase, oled_tram_east, go_in_next=False)

def phase_2(time_left_in_phase: int):
    pin_led_north_green.off()
    pin_led_north_red.on()
    north_tram_green = False

    pin_led_south_green.on()
    pin_led_south_red.off()
    south_tram_green = True

    pin_led_east_green.off()
    pin_led_east_red.on()
    east_tram_green = False
    tram_stop(time_left_in_phase, oled_tram_north, go_in_next=False)
    tram_go(time_left_in_phase, oled_tram_south, "Cars right!", go_in_next=False)
    tram_stop(time_left_in_phase, oled_tram_east, go_in_next=True)

def phase_3(time_left_in_phase: int):
    pin_led_north_green.off()
    pin_led_north_red.on()
    north_tram_green = False

    pin_led_south_green.off()
    pin_led_south_red.on()
    south_tram_green = False

    pin_led_east_green.off()
    pin_led_east_red.on()
    east_tram_green = True
    tram_stop(time_left_in_phase, oled_tram_north, go_in_next=False)
    tram_stop(time_left_in_phase, oled_tram_south, go_in_next=False)
    tram_go(time_left_in_phase, oled_tram_east, "", go_in_next=True)

def phase_4(time_left_in_phase: int):
    pin_led_north_green.off()
    pin_led_north_red.on()
    north_tram_green = False

    pin_led_south_green.off()
    pin_led_south_red.on()
    south_tram_green = False

    pin_led_east_green.off()
    pin_led_east_red.on()
    east_tram_green = True
    tram_stop(time_left_in_phase, oled_tram_north, go_in_next=True)
    tram_stop(time_left_in_phase, oled_tram_south, go_in_next=False)
    tram_go(time_left_in_phase, oled_tram_east, "Cars right!", go_in_next=False)


def any_button_out_pressed():
    if pin_button_north_out.value() == 1:
        return True
    if pin_button_south_out.value() == 1:
        return True
    if pin_button_east_out.value() == 1:
        return True

#setup
pin_led_north_green.off()
pin_led_north_red.off()
pin_led_south_green.off()
pin_led_south_red.off()
pin_led_east_green.off()
pin_led_east_red.off()
current_phase = 0
phase_start_time = time.time()
freeze_state = False

north_tram_green = False
south_tram_green = False
east_tram_green = False

number_of_phases = 5
phase_functions = {0: phase_0, 1: phase_1, 2: phase_2, 3: phase_3, 4: phase_4}

button_states = {
    'north_in': {'pressed': False, 'press_time': 0},
    'north_out': {'pressed': False, 'press_time': 0},
    'south_in': {'pressed': False, 'press_time': 0},
    'south_out': {'pressed': False, 'press_time': 0},
    'east_in': {'pressed': False, 'press_time': 0},
    'east_out': {'pressed': False, 'press_time': 0},
}

detected_north_in = False
detected_south_in = False
detected_east_in = False

while True:

    current_time = time.time()
    elapsed_time = current_time - phase_start_time


    # Check if any buttons have been pressed
    if pin_button_north_in.value() == 1 and not button_states['north_in']['pressed']:
        button_states['north_in']['pressed'] = True
        button_states['north_in']['press_time'] = current_time
        detected_north_in = True
        freeze_state = True
    if any_button_out_pressed() and detected_north_in and not button_states['north_out']['pressed']:
        button_states['north_out']['pressed'] = True
        button_states['north_in']['pressed'] = False
        button_states['north_out']['press_time'] = current_time
        detected_north_in = False
        freeze_state = True
        print("north out pressed")

    if pin_button_south_in.value() == 1 and not button_states['south_in']['pressed']:
        button_states['south_in']['pressed'] = True
        button_states['south_in']['press_time'] = current_time
        detected_south_in = True
        freeze_state = True
    if any_button_out_pressed() and detected_south_in and not button_states['south_out']['pressed']:
        button_states['south_out']['pressed'] = True
        button_states['south_in']['pressed'] = False
        button_states['south_out']['press_time'] = current_time
        detected_south_in = False
        freeze_state = True

    if pin_button_east_in.value() == 1 and not button_states['east_in']['pressed']:
        button_states['east_in']['pressed'] = True
        button_states['east_in']['press_time'] = current_time
        detected_east_in = True
        freeze_state = True
    if any_button_out_pressed() and detected_east_in and not button_states['east_out']['pressed']:
        button_states['east_out']['pressed'] = True
        button_states['east_in']['pressed'] = False
        button_states['east_out']['press_time'] = current_time
        detected_east_in = False
        freeze_state = True

    # Check if it's time to change phases based on button presses
    if button_states['north_in']['pressed']:
        oled_tram_north.framebuf.fill_rect(0, 0, 200, 10, 0)
        oled_tram_north.text(f"Opt depart: {10 - (current_time - button_states['north_in']['press_time'])}", 0, 0)
        oled_tram_north.show()
        if current_time - button_states['north_in']['press_time'] >= 10:
            current_phase = 0
            phase_start_time = current_time
            button_states['north_in']['pressed'] = False
            freeze_state = False
    if button_states['north_out']['pressed']:
        oled_tram_north.framebuf.fill_rect(0, 0, 200, 10, 0)
        oled_tram_north.text(f"Ret traff: {3 - (current_time - button_states['north_out']['press_time'])}", 0, 0)
        oled_tram_north.show()
        if current_time - button_states['north_out']['press_time'] >= 3:
            current_phase = 1
            phase_start_time = current_time
            button_states['north_out']['pressed'] = False
            freeze_state = False

    if button_states['south_in']['pressed']:
        oled_tram_south.framebuf.fill_rect(0, 0, 200, 10, 0)
        oled_tram_south.text(f"Opt depart: {10 - (current_time - button_states['south_in']['press_time'])}", 0, 0)
        oled_tram_south.show()
        if current_time - button_states['south_in']['press_time'] >= 10:
            current_phase = 2
            phase_start_time = current_time
            button_states['south_in']['pressed'] = False
            freeze_state = False
    if button_states['south_out']['pressed']:
        oled_tram_south.framebuf.fill_rect(0, 0, 200, 10, 0)
        oled_tram_south.text(f"Ret traff: {3 - (current_time - button_states['south_out']['press_time'])}", 0, 0)
        oled_tram_south.show()
        if current_time - button_states['south_out']['press_time'] >= 3:
            current_phase = 3
            phase_start_time = current_time
            button_states['south_out']['pressed'] = False
            freeze_state = False

    if button_states['east_in']['pressed']:
        oled_tram_east.framebuf.fill_rect(0, 0, 200, 10, 0)
        oled_tram_east.text(f"Opt depart: {10 - (current_time - button_states['east_in']['press_time'])}", 0, 0)
        oled_tram_east.show()
        if current_time - button_states['east_in']['press_time'] >= 10:
            current_phase = 3
            phase_start_time = current_time
            button_states['east_in']['pressed'] = False
            freeze_state = False
    if button_states['east_out']['pressed']:
        current_phase = 2
        phase_start_time = current_time
        button_states['east_out']['pressed'] = False
        freeze_state = False

    elapsed_time = current_time - phase_start_time

    if not freeze_state:
        # Move to the next phase if the phase time has elapsed
        if elapsed_time >= phase_time:
            current_phase = (current_phase + 1) % number_of_phases
            phase_start_time = current_time

        time_left_in_phase = phase_time - elapsed_time
        phase_functions[current_phase](int(time_left_in_phase))
