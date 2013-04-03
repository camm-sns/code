PBS job submission sassena.pbs shows how to submit a sassena job on Chadwick cluster. In particular:
- sassenaInc.xml will calculate incoherent structure factor Inc(Q,t) with:
  - Q in between 0.1 and 1.0 every 0.01
  - use trajectory production_single.dcd (not included in this directory because of size)
- sassenaCoh.xml will calculate coherent structure factor Coh(Q,t) with:
  - Q in between 0.1 and 1.0 every 0.01
  - use trajectory production_single.dcd (not included in this directory because of size)
