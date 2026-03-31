import board
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.extensions.display import Display, TextDisplay
from kmk.modules.encoder import EncoderHandler

keyboard = KMKKeyboard()

# 1. Matrix Configuration (4 rows by 3 columns)
# Update these pins to match your actual wiring
keyboard.col_pins = (board.D0, board.D1, board.D2)
keyboard.row_pins = (board.D3, board.D6, board.D7, board.D8)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

# 2. Encoder Configuration
encoder_handler = EncoderHandler()
keyboard.modules.append(encoder_handler)
encoder_handler.pins = ((board.D9, board.D10, None, False),) # No push button

# 3. Display Setup (The "Spinning" Text)
# We use a custom subclass to handle the movement logic
class BouncingText(TextDisplay):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.x_dir = 1
        self.current_x = 0

    def before_matrix_scan(self, keyboard):
        # Update text position every cycle
        # Width of 128 minus roughly the text length
        if self.current_x >= 40 or self.current_x < 0:
            self.x_dir *= -1
        
        self.current_x += self.x_dir
        # Simple 'spinning' effect simulated by moving X and updating title
        self.entries[0] = f"{' ' * (self.current_x // 4)}Antons Hackpad v2"
        super().before_matrix_scan(keyboard)

display_driver = Display(
    displayer=BouncingText(title="Initializing..."),
    width=128,
    height=32,
    flip=False,
)
keyboard.extensions.append(display_driver)

# 4. Keymap & Encoder Map
keyboard.keymap = [
    [
        KC.N1, KC.N2, KC.N3,
        KC.N4, KC.N5, KC.N6,
        KC.N7, KC.N8, KC.N9,
        KC.N0, KC.ENT, KC.SPC,
    ]
]

encoder_handler.map = [((KC.VOLD, KC.VOLU),)] # Layer 0: CCW, CW

if __name__ == '__main__':
    keyboard.go()