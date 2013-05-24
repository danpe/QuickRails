import os
import re

import sublime
from QuickRails import QuickRailsWindowCommand, get_idea
from QuickExec import ProcessListener
#import add

class QuickRailsGeneratorsCommand(QuickRailsWindowCommand, ProcessListener):
  def run(self):
    self.generators = self.get_available_generators()
    self.window.show_quick_panel(self.generators, self.on_selected)

  def on_selected(self, selected):
    if selected == 0:
      self.run_quick_command("rails g", self.window.folders()[0], self)
    elif selected > 0:
      self.generate(self.generators[selected])

  def on_data(self, proc, data):
    pass

  def on_finished(self, proc, alldata):
    if alldata:
      gens = self.parse_generators(alldata)
      self.write_gens_to_file(gens)
      #self.window.show_quick_panel(gens, self.on_selected)

  def generate(self, argument):
    self.window.show_input_panel("rails generate", argument + " ", lambda s: self.run_generator(s), None, None)

  def run_generator(self, argument):
    command = 'rails generate {thing}'.format(thing=argument)
    self.run_shell_command(command, self.window.folders()[0])

  def parse_generators(self, generators_result):
    gens = re.findall("  ([\w:]+)", generators_result)
    #print gens
    return gens

  def write_gens_to_file(self, gens):
    gens.sort()
    data = "\n".join(gens)
    f = open(os.path.join(get_idea(self.get_working_dir()), '.generators'), 'w+')
    f.write(data)
    f.close()

  def get_available_generators(self):
    try:
      f = open(os.path.join(get_idea(self.get_working_dir()), '.generators'), 'r')
      data = f.read()
      f.close()
      gens = data.split()
      gens.insert(0, "Update...")
    except IOError:
      gens = "".split()
      gens.insert(0, "Update...")
    return gens
