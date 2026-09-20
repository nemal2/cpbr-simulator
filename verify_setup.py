import numpy, scipy, pandas, networkx, matplotlib
print('1/5 numerics + graphs: OK')
import pandapower as pp, pandapower.networks as pn
net = pn.case14(); pp.runpp(net)
print('2/5 pandapower power-flow solve: OK')
import wntr
wn = wntr.network.WaterNetworkModel('Net3')
wntr.sim.EpanetSimulator(wn).run_sim()
print('3/5 wntr hydraulic solve: OK')
import jupyterlab
print('4/5 jupyterlab importable: OK')
print('5/5 all good — you are ready to start coding')
