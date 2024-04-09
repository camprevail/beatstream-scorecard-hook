import ctypes

# Define the necessary constants and types
WM_SETTEXT = 0x000C
WM_APP = 0x8000
LPARAM = ctypes.c_void_p

class tOSD:
    def __init__(self):
        self.hwGame = None

    def find_window(self):
        self.hwGame = ctypes.windll.user32.FindWindowW("DX9OSDMessageWindow", None)
        return self.hwGame != 0

    def send_message(self, msg, interval):
        if not self.hwGame:
            return False
        msg_ptr = ctypes.c_wchar_p(msg)
        ctypes.windll.user32.SendMessageW(self.hwGame, WM_SETTEXT, 0, ctypes.cast(msg_ptr, LPARAM))
        ctypes.windll.user32.SendNotifyMessageW(self.hwGame, WM_APP + 1, interval, 0)
        return True

# Example usage
if __name__ == "__main__":
    osd = tOSD()

    # Find the game window
    found = osd.find_game()
    if found:
        print("OSD window found!")
    else:
        print("OSD window not found!")

    # Send message to game window
    message = "Hello from Python"
    interval = 120  # Interval in milliseconds
    sent = osd.send_message(message, interval)
    if sent:
        print("Message sent successfully!")
    else:
        print("Failed to send message.")
