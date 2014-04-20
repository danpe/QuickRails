import os
import re

import sublime
from QuickRails.QuickRails import QuickRailsWindowCommand, get_idea
from QuickRails.QuickExec import ProcessListener

class QuickRailsGotoviewCommand(QuickRailsWindowCommand, ProcessListener):

  def is_haml_available(self):
    return os.path.isfile('haml') and os.access('haml', os.X_OK)

  def run(self):
    if self.is_rails_controler(self.active_view().file_name()):
      method = self.get_method(self.active_view)
      file_path = self.get_path_for_controller(method)
      sublime.active_window().open_file(str(file_path))
    else:
      sublime.status_message("NOT VALID RAILS CONTROLLER!")

  def is_rails_controler(self, path):
    if (path.find('controllers') > 0):
      return True
    else:
      return False

  def get_method(self, view):
    text_on_cursor = None
    for region in self.active_view().sel():
      if region.begin() == region.end():
        line = self.active_view().line(region)
        if not line.empty():
          return self.extract_method_from_line(self.active_view().substr(line))
      else:
        pass

  def extract_method_from_line(self, line):
    m = re.search('def (.*)', line)
    if m:
      return m.group(1)
    else:
      sublime.status_message("NOT VALID METHOD!");

  def get_path_for_controller(self, method):
    m = re.search('app/controllers/(.*)_controller.rb', self.active_view().file_name())
    if m:
      view_path = self.window.folders()[0] + '/app/views/' + m.group(1) + '/' + method + '.html.haml'
      try:
        f = open(view_path, 'r')
        f.read()
        f.close()
      except IOError:
        f = open(view_path, 'w')
        f.write('// Generated ' + method + ' view:')
        f.close()
      return view_path

  def is_enabled(args):
    return True
