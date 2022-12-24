import subprocess
import ctypes

class disable_file_system_redirection:
    _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
    _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection
    def __enter__(self):
        self.old_value = ctypes.c_long()
        self.success = self._disable(ctypes.byref(self.old_value))
    def __exit__(self, type, value, traceback):
        if self.success:
            self._revert(self.old_value)


src_filename = 'input_file.oga'
dest_filename = 'output.wav'
with disable_file_system_redirection():
    process = subprocess.run(['ffmpeg', '-i', 'input_file.oga', 'output_file.wav'])