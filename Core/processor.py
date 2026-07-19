from Modules.enhancements import Enhancements
from Modules.noise_addition import Noise
from Modules.filtering import Filtering
from Modules.edge_detection import EdgeDetection
from Modules.segmentation import Segmentation
from Modules.frequency_domain import FrequencyDomain
from Modules.morphological import Morphology
from Modules.compression import Compression
from Modules.transformation import Transformation


class Processor:

    def __init__(self):

        self.enhancement = Enhancements()
        self.noise = Noise()
        self.filtering = Filtering()
        self.edge = EdgeDetection()
        self.segmentation = Segmentation()
        self.frequency = FrequencyDomain()
        self.morphology = Morphology()
        self.compression = Compression()
        self.transformation = Transformation()