# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Thomas Amland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import shutil
import traceback
import xbmc
import utils
from xbmcgui import Dialog
from editor import Editor


default = xbmc.translatePath('special://xbmc/system/keymaps/%s.xml' % utils.setting('deviceTag'))
userdata = xbmc.translatePath('special://userdata/keymaps/')
kmName = utils.setting('deviceTag') + '_gen.xml'
gen_file = os.path.join(userdata, kmName)


def setup_keymap_folder():
    if not os.path.exists(userdata):
        os.makedirs(userdata)
    else:
        #check if 'gen.xml' (from older versions) exists, and if it does copy and rename it to the new format
        if os.path.exists(os.path.join(userdata, 'gen.xml')):
            shutil.copyfile(os.path.join(userdata, 'gen.xml'), os.path.join(userdata, kmName))
        #make sure there are no user defined keymaps
        for name in os.listdir(userdata):
            if name.endswith('.xml') and not name.endswith('_gen.xml'):# and name != os.path.basename(gen_file):
                src = os.path.join(userdata, name)
                for i in xrange(100):
                    dst = os.path.join(userdata, "%s.bak.%d" % (name, i))
                    if os.path.exists(dst):
                        continue
                    shutil.move(src, dst)
                    #successfully renamed
                    break


def main():
    ## load mappings ##
    try:
        setup_keymap_folder()
    except Exception:
        traceback.print_exc()
        utils.rpc('GUI.ShowNotification', title="Keymap Editor",
            message="Failed to remove old keymap file", image='error')
        return

    defaultkeymap = utils.read_keymap(default)
    userkeymap = []
    if os.path.exists(gen_file):
        try:
            userkeymap = utils.read_keymap(gen_file)
        except Exception:
            traceback.print_exc()
            utils.rpc('GUI.ShowNotification', title="Keymap Editor",
                      message="Failed to load keymap file", image='error')
            return

    ## main loop ##
    confirm_discard = False
    while True:
        idx = Dialog().select(utils.tr(30000), [utils.tr(30003), utils.tr(30004), utils.tr(30005)])
        if idx == 0:
            # edit
            editor = Editor(defaultkeymap, userkeymap)
            editor.start()
            confirm_discard = editor.dirty
        elif idx == 1:
            # reset
            confirm_discard = bool(userkeymap)
            userkeymap = []
        elif idx == 2:
            # save
            if os.path.exists(gen_file):
                shutil.copyfile(gen_file, gen_file + ".old")
            utils.write_keymap(userkeymap, gen_file)
            xbmc.executebuiltin("Action(reloadkeymaps)")
            break
        elif idx == -1 and confirm_discard:
            if Dialog().yesno(utils.tr(30000), utils.tr(30006)) == 1:
                break
        else:
            break

    sys.modules.clear()

if __name__ == "__main__":
    main()
