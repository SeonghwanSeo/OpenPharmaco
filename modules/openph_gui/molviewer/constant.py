import random
import string

characters = string.digits + string.ascii_lowercase
RAND_KEY = "".join(random.choice(characters) for _ in range(4))

CHAIN_KEY = RAND_KEY + "_CHAIN_"
PROTEIN_KEY = RAND_KEY + "_PROTEIN_"
POCKET_KEY = RAND_KEY + "_POCKET_"

NCI_KEY = RAND_KEY + "_NCITYPE_"
HOTSPOT_KEY = RAND_KEY + "_hotspot"
RESIDUE_KEY = RAND_KEY + "_resi"
PHARMACOPHORE_POINT_KEY = RAND_KEY + "_point"
INTERACTION_KEY = RAND_KEY + "_nci"
