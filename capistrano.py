import os
import re

import sublime
from QuickRails import QuickRailsWindowCommand, get_idea
from QuickExec import ProcessListener


class QuickRailsCapistranoTasksCommand(QuickRailsWindowCommand, ProcessListener):

    def run(self):
        self.capistranoTasks = self.get_available_capistrano_tasks()
        self.window.show_quick_panel(self.capistranoTasks, self.on_selected)

    def on_selected(self, selected):
        if selected == 0:
            self.run_quick_command("cap -vT", self.window.folders()[0], self)
        elif selected > 0:
            self.capistrano(self.capistranoTasks[selected][0])

    def on_data(self, proc, data):
        pass

    def on_finished(self, proc, alldata):
        print ":: on_finished"
        print str(alldata)
        if alldata:
            tasks = self.parse_capistrano_tasks(alldata)
            self.write_tasks_to_file(tasks)
            #self.window.show_quick_panel(tasks, self.on_selected)

    def capistrano(self, argument):
        self.window.show_input_panel("cap ", argument + " ", lambda s: self.run_capistrano_task(s), None, None)

    def run_capistrano_task(self, argument):
        command = 'cap {thing}'.format(thing=argument)
        self.run_shell_command(command, self.window.folders()[0])

    def parse_capistrano_tasks(self, capistrano_tasks_result):
        ctsk = re.findall("cap ([\w:]+\s.*)", capistrano_tasks_result)
        ctsk = [re.sub("([\w:]+)[\s#]+(.*)", "\\1 \\2", i) for i in ctsk]
        return ctsk

    def write_tasks_to_file(self, ctsk):
        ctsk.sort()
        data = "\n".join(ctsk)
        f = open(os.path.join(get_idea(self.get_working_dir()), '.capistranoTasks'), 'w')
        f.write(data)
        f.close()

    def get_available_capistrano_tasks(self):
        try:
            f = open(os.path.join(get_idea(self.get_working_dir()), '.capistranoTasks'), 'r')
            data = f.read()
            f.close()
            ctsk = [i.split(" ", 1) for i in data.split("\n")]
            print ctsk
        except IOError:
            ctsk = []
        ctsk.insert(0, ["Update...", "Rebuild list of available capistrano tasks"])
        return ctsk