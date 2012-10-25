import sublime, sublime_plugin
import re
import os
import os.path
import time

rails_root_cache = {}

def rails_root(directory):
    global rails_root_cache

    retval = False
    leaf_dir = directory

    if leaf_dir in rails_root_cache and rails_root_cache[leaf_dir]['expires'] > time.time():
        return rails_root_cache[leaf_dir]['retval']

    while directory:
        if os.path.exists(os.path.join(directory, '.idea')):
            retval = directory
            break
        parent = os.path.realpath(os.path.join(directory, os.path.pardir))
        if parent == directory:
            # /.. == /
            retval = False
            break
        directory = parent

    rails_root_cache[leaf_dir] = {
        'retval': retval,
        'expires': time.time() + 5
    }

    return retval

# for readability code
def rails_root_exist(directory):
    return rails_root(directory)

def get_idea(directory):
  root = rails_root(directory)
  return os.path.join(root, '.idea')


class QuickRailsWindowCommand(sublime_plugin.WindowCommand):
  def active_view(self):
    return self.window.active_view()

  def _active_file_name(self):
    view = self.active_view()
    if view and view.file_name() and len(view.file_name()) > 0:
      return view.file_name()

  # If there is a file in the active view use that file's directory to
  # search for the Rails root.  Otherwise, use the only folder that is
  # open.
  def get_working_dir(self):
    file_name = self._active_file_name()
    if file_name:
      return os.path.realpath(os.path.dirname(file_name))
    else:
      try:  # handle case with no open folder
        return self.window.folders()[0]
      except IndexError:
        return ''

  # If there's no active view or the active view is not a file on the
  # filesystem (e.g. a search results view)
  def is_enabled(self):
    if self._active_file_name() or len(self.window.folders()) == 1:
      return rails_root(self.get_working_dir())

  def run_shell_command(self, command, working_dir):
    if not command:
      return False
    self.window.run_command("exec", {
      "cmd": [command],
      "shell": True,
      "working_dir": working_dir,
      "file_regex": r"([^ ]*\.rb):?(\d*)"
    })
    self.display_results()
    return True
