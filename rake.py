import os
import re

import sublime
from QuickRails import QuickRailsWindowCommand, get_idea
from QuickExec import ProcessListener
#import add

class QuickRailsRakeTasksCommand(QuickRailsWindowCommand, ProcessListener):
  def run(self):
    self.rakeTasks = self.get_available_rake_tasks()
    self.window.show_quick_panel(self.rakeTasks, self.on_selected)

  def on_selected(self, selected):
    if selected == 0:
      self.run_quick_command("rake -sT", self.window.folders()[0], self)
    elif selected > 0:
      self.rake(self.rakeTasks[selected])

  def on_data(self, proc, data):
    pass

  def on_finished(self, proc, alldata):
    if alldata:
      tasks = self.parse_rake_tasks(alldata)
      self.write_tasks_to_file(tasks)
      #self.window.show_quick_panel(tasks, self.on_selected)

  def rake(self, argument):
    self.window.show_input_panel("rake ", argument + " ", lambda s: self.run_rake_task(s), None, None)

  def run_rake_task(self, argument):
    command = 'rake {thing}'.format(thing=argument)
    self.run_shell_command(command, self.window.folders()[0])

  def parse_rake_tasks(self, rake_tasks_result):
    rtsk = re.findall("rake ([\w:]+)", rake_tasks_result)
    print rtsk
    return rtsk

  def write_tasks_to_file(self, rtsk):
    rtsk.sort()
    data = "\n".join(rtsk)
    f = open(os.path.join(get_idea(self.get_working_dir()), '.rakeTasks'), 'w')
    f.write(data)
    f.close()

  def get_available_rake_tasks(self):
    try:
      f = open(os.path.join(get_idea(self.get_working_dir()), '.rakeTasks'), 'r')
      data = f.read()
      f.close()
      rtsk = data.split()
      rtsk.insert(0, "Update...")
    except IOError:
      rtsk = "".split()
      rtsk.insert(0, "Update...")
    return rtsk
