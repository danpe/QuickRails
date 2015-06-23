import os
import re

import sublime
from QuickRails.QuickRails import QuickRailsWindowCommand, rails_root
#import add

class QuickRailsBundleInstallCommand(QuickRailsWindowCommand):
  def run(self):
    self.run_bundle_install()

  def run_bundle_install(self):
    command = 'bundle install'
    self.run_shell_command(command, rails_root(self.get_working_dir()))

  def is_enabled(args):
    return True
