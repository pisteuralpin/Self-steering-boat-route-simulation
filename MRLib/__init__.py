# ---------------------------------------------------------------------------- #
#                                     MRLib                                    #
#                               Mathurin Roulier                               #
# ---------------------------------------------------------------------------- #

"""
MRLib by Mathurin Roulier
=====
A library of useful functions for myself.
Feel free to use it, edit it, and share it. If you publish something using this library, please credit me.

Modules
-------
control_engineering
    Contains functions related to control engineering: Transfer function, Bode diagram, Corrector, etc.
prompt
    Contains functions used to prompt the user via the terminal: Choice Menu.
export
    Contains functions used to export data: Dict -> CSV.
list
    Contains functions used to manipulate lists: Remove duplicates.
operations
    Contains functions used to perform operations: Direction, Distance, Nearest point.
route
    Contains functions used to compute routes: Route cost.
"""

import MRLib.control_engineering as control_engineering
import MRLib.prompt as prompt
import MRLib.export as export
import MRLib.list as list
import MRLib.geometry as geometry
import MRLib.route as route