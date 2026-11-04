"""Load the AI models once (downloading them the first time, about 2.3 GB) and check that they use the graphics card.

Exit code 0: the cutouts run on the graphics card. 3: they run on the processor (slow), so the setup can try another
build of the cutout runtime. Used by the Kaggle notebook and the PC setup.
"""

import sys

import split_layers

models = split_layers.Models()
if models.cutouts_on_gpu:
    print("OK: the cutout models run on the graphics card.")
    sys.exit(0)
print("The cutout models run on the processor (slow).")
sys.exit(3)
