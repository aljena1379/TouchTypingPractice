import random
import os
import winsound
import msvcrt
import json
import threading

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

PRESET_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Presets")
os.makedirs(PRESET_FOLDER, exist_ok=True)

CORRECT_SOUND = os.path.join(os.path.dirname(__file__), "Sounds/TRUE_KeyboardKey.wav")
WRONG_SOUND = os.path.join(os.path.dirname(__file__), "Sounds/FALSE_Beep.wav")

sound_lock = threading.Lock()

CHAR_SETS = {
    "Lowercase Home Row (asdf...)": 'asdfghjkl;',
    "Lowercase Top Row (qwerty...)": 'qwertyuiop',
    "Lowercase Bottom Row (zxcvbn...)": 'zxcvbnm,./',
    "Uppercase Home Row (ASDF...)": 'ASDFGHJKL:',
    "Uppercase Top Row (QWERTY...)": 'QWERTYUIOP',
    "Uppercase Bottom Row (ZXCVB...)": 'ZXCVBNM<>?',
    "Numbers (0-9)": '0123456789',
    "Special Characters (!@#$...)": '!@#$%^&*()_+-=[]{}|;:\'"',
}

CHARACTERS = ''

CHUNK_SIZE = 200
GROUP_SIZE = 5

def get_char():
    return msvcrt.getch().decode('utf-8', errors='ignore')

def play_sound(correct=True):
    def _play():
        with sound_lock:
            winsound.PlaySound(None, winsound.SND_PURGE)  
            winsound.PlaySound(
                CORRECT_SOUND if correct else WRONG_SOUND,
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )
    threading.Thread(target=_play, daemon=True).start()

def generate_characters():
    raw = ''.join(random.choice(CHARACTERS) for _ in range(CHUNK_SIZE))
    with_spaces = ' '.join([raw[i:i+GROUP_SIZE] for i in range(0, CHUNK_SIZE, GROUP_SIZE)])
    return with_spaces

def save_preset(name, characters):
    filename = os.path.join(PRESET_FOLDER, f"{name}.preset")
    with open(filename, 'w') as f:
        f.write(characters)

def load_presets():
    presets = []
    for file in os.listdir(PRESET_FOLDER):
        if file.endswith('.preset'):
            with open(os.path.join(PRESET_FOLDER, file), 'r') as f:
                presets.append((file.replace('.preset', ''), f.read()))
    return presets

def define_preset():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Enter characters you want to include in the test:")
    user_chars = input("> ")
    print("Enter a name for this preset:")
    name = input("> ")
    save_preset(name, user_chars)
    print(f"Preset '{name}' saved.")
    input("Press Enter to continue...")

def choose_preset():
    global CHARACTERS
    presets = load_presets()
    if not presets:
        print("No presets found.")
        input("Press Enter to return...")
        return

    print("Available Presets:")
    for i, (name, _) in enumerate(presets):
        print(f"{i + 1}. {name}")
    
    while True:
        print("Choose preset number: ")
        choice = get_char()
        if choice.isdigit() and 1 <= int(choice) <= len(presets):
            CHARACTERS = presets[int(choice) - 1][1]
            break
        print("Invalid choice. Try again.")

def ask_charsets():
    global CHARACTERS
    print("Select which character sets to include:")
    print("Press [f] for Fine (include), [j] for Junk (skip)\n")

    for name, chars in CHAR_SETS.items():
        print(f"{name}? [f/j]: ", end='', flush=True)
        while True:
            key = get_char().lower()
            if key == 'f':
                CHARACTERS += chars
                print("Fine")
                break
            elif key == 'j':
                print("Junk")
                break
            else:
                print("\nInvalid key. Use 'f' or 'j': ", end='', flush=True)

    if not CHARACTERS:
        print("\nNo character sets selected. Exiting...")
        exit()

def typing_trainer():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Touch Typing Trainer (press ESC to quit)\n")
    sequence = generate_characters()
    print(sequence)
    print("\nStart typing:\n")

    input_index = 0
    while input_index < len(sequence):
        expected_char = sequence[input_index]
        typed_char = get_char()

        if typed_char.lower() == '\x1b':  # ESC key
            print("\nExiting...")
            break

        if typed_char == expected_char:
            print(GREEN + expected_char + RESET, end='', flush=True)
            play_sound(True)
            input_index += 1
        else:
            print(RED + typed_char + RESET, end='', flush=True)
            play_sound(False)

    print("\n\nWell done!")

def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("==== Touch Typing Trainer ====\n")
        print("1. Create new custom character set")
        print("2. Use existing preset")
        print("3. Choose character sets manually (Fine/Junk style)")
        print("0. Exit\n")

        print("Choose an option: ")
        
        choice = get_char()
        if choice == '1':
            define_preset()
        elif choice == '2':
            choose_preset()
            typing_trainer()
        elif choice == '3':
            ask_charsets()
            typing_trainer()
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            input("Invalid option. Press Enter to try again...")

if __name__ == "__main__":
    main_menu()

