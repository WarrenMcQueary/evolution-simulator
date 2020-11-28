# evolution-simulator
Evolution simulator code for KID Museum.

Generates zorks (winged giraffe-like animals) with random traits.  Grades each zork's survivability based on its
traits.  Culls zorks that fall below a certain threshold.  Zorks mate in random pairs to create new zorks.

New in this version of the code, the user sets starting parameters via a GUI.

The idea for kid interaction is that kids can set the initial parameters, watch a run of the simulation, and repeat.
By tweaking their parameters and seeing the effect on the simulation, kids can gain some intuition about the effects of
these parameters on evolution.

On invalid user entries, and in cases where there's a generation of 0 or 1 zorks, the code avoids crashing, and instead
the input panel provides helpful advice.

## Requirement
This project has been successfully tested for Python >= 3.8.

## Install dependencies
>pip install matplotlib
pip install tqdm
