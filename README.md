# dex-machinesim

Simulates a DEX-protocol machine that serves the given DEX content on the given pseduo-tty path.  This project was developed in conjunction with the [dex-reader](https://github.com/mdisibio/dex-reader) library to read DEX data, as access to physical DEX-speaking hardware was limited.

# Running

The following code will wait for a connection on pseudo-tty 3 (ptyp3), and upon connection return the contents of the `test.dex` file in the DEX protocol.

```
import dexmachinesim

content = open('test.dex','r').read().splitlines(True)

sim = dexmachinesim.DexMachineSim('/dev/ptyp3', content, False)
sim.run()
```
