

import dexmachinesim

path = '/dev/ptyp3'
content = "line1\nline2\n"

f = open('test.dex','r')
content = f.read()

sim = dexmachinesim.DexMachineSim(path, content.splitlines(True), False)
sim.run()