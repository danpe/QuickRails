import os
import re

import sublime
from QuickRails import QuickRailsWindowCommand, get_idea
import add

class QuickRailsGeneratorsCommand(QuickRailsWindowCommand):
  def run(self):
    self.generators = self.get_available_generators()
    self.window.show_quick_panel(self.generators, self.on_selected)

  def on_selected(self, selected):
     self.generate(self.generators[selected])

  def generate(self, argument):
    self.window.show_input_panel("rails generate", argument + " ", lambda s: self.run_generator(s), None, None)

  def run_generator(self, argument):
    command = 'rails generate {thing}'.format(thing=argument)
    self.run_shell_command(command, self.window.folders()[0])

  def get_available_generators(self):
    f = open(os.path.join(get_idea(self.get_working_dir()), '.generators'), 'r')
    data = f.read()
    f.close()
    return re.findall('Generator name="(.*?)"', data)
