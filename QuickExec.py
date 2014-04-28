import sublime, sublime_plugin
import os, sys
import threading
from threading import Thread
import subprocess
import functools
import time
import gc


def objects_by_id(id_):
  for obj in gc.get_objects():
    if id(obj) == id_:
      return obj
  raise Exception("No found")

class ProcessListener(object):
  def on_data(self, proc, data):
    pass

  def on_finished(self, proc, alldata):
    pass


# Encapsulates subprocess.Popen, forwarding stdout to a supplied
# ProcessListener (on a separate thread)
class AsyncProcess(object):
  # "path" is an option in build systems
  # "shell" is an options in build systems
  def __init__(self, arg_list, env, listener, path="", shell=False):
    self.listener = listener
    self.killed = False

    self.start_time = time.time()
    self.alldata = ''
    self.stdout_thread = None
    self.stderr_thread = None

    # Hide the console window on Windows
    startupinfo = None
    if os.name == "nt":
      startupinfo = subprocess.STARTUPINFO()
      startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    # Set temporary PATH to locate executable in arg_list
    if path:
      old_path = os.environ["PATH"]
      # The user decides in the build system whether he wants to append $PATH
      # or tuck it at the front: "$PATH;C:\\new\\path", "C:\\new\\path;$PATH"
      os.environ["PATH"] = os.path.expandvars(path).encode(sys.getfilesystemencoding())

    proc_env = os.environ.copy()
    proc_env.update(env)
    # for k, v in proc_env.iteritems():
    for k, v in tuple(proc_env.items()):
      proc_env[k] = os.path.expandvars(v).encode(sys.getfilesystemencoding())

    self.proc = subprocess.Popen(arg_list, stdout=subprocess.PIPE,
      stderr=subprocess.PIPE, startupinfo=startupinfo, env=proc_env, shell=shell)

    if path:
      os.environ["PATH"] = old_path

    if self.proc.stdout:
      self.stdout_thread = Thread(target=self.read_stdout, args=())
      self.stdout_thread.start()

    if self.proc.stderr:
      self.stderr_thread = Thread(target=self.read_stderr, args=())
      self.stderr_thread.start()

  def kill(self):
    if not self.killed:
      self.killed = True
      self.proc.terminate()
      self.listener = None

  def poll(self):
    return self.proc.poll() == None

  def exit_code(self):
    return self.proc.poll()

  def read_stdout(self):
    for row in self.proc.stdout.readlines():
      self.alldata += str(row)

    self.listener.on_data(self, self.alldata)
    self.proc.stdout.close()
    # self.stdout_thread = None
    # self.stderr_thread = None
    self.proc.terminate()
    sublime.set_timeout(lambda: self.listener.on_finished(self, self.alldata), 0)

  def read_stderr(self):
    data = ''
    for row in self.proc.stderr.readlines():
      data += str(row)
    if data != "":
      if self.listener:
        self.listener.on_data(self, data)
    else:
      self.proc.stderr.close()
      self.proc.terminate()
      break

class QuickExecCommand(sublime_plugin.WindowCommand, ProcessListener):
  def run(self, cmd = [], file_regex = "", line_regex = "", working_dir = "",
            encoding = "utf-8", env = {}, kill = False, listenerid = "",
            # Catches "path" and "shell"
            **kwargs):

    listener = objects_by_id(listenerid)

    # TODO: arguments can only be in JSON format, so i need to convert
    # function pointer 'listener' to string and then back to function pointer.

    if kill:
      if self.proc:
        self.proc.kill()
        self.proc = None
      return

    # Default the to the current files directory if no working directory was given
    if (working_dir == "" and self.window.active_view()
                    and self.window.active_view().file_name()):
        working_dir = os.path.dirname(self.window.active_view().file_name())

    self.encoding = encoding

    self.proc = None
    sublime.status_message("BUILDING")

    merged_env = env.copy()
    if self.window.active_view():
      user_env = self.window.active_view().settings().get('build_env')
      if user_env:
        merged_env.update(user_env)

    # Change to the working dir, rather than spawning the process with it,
    # so that emitted working dir relative path names make sense
    if working_dir != "":
      os.chdir(working_dir)

    err_type = OSError
    if os.name == "nt":
      err_type = WindowsError

    if not listener:
      print("Oh shit...")
      listener = self

    try:
      # Forward kwargs to AsyncProcess
      self.proc = AsyncProcess(cmd, merged_env, listener, **kwargs)
    except err_type as e:
      pass

  def is_enabled(self, kill = False):
    if kill:
      return hasattr(self, 'proc') and self.proc and self.proc.poll()
    else:
      return True

  def finish(self, proc, alldata):
    if proc != self.proc:
      return

  def on_data(self, proc, data):
    pass
    #sublime.set_timeout(functools.partial(self.append_data, proc, data), 0)

  def on_finished(self, proc, alldata):
    sublime.set_timeout(functools.partial(self.finish, proc, alldata), 0)
