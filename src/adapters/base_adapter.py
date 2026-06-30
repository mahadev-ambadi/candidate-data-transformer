from abc import ABC, abstractmethod
from typing import List
from pathlib import Path

from src.models.candidate import Candidate

class BaseAdapter(ABC):
    """
    Abstract base class for all data source adapters.
    
    Adapters are strictly responsible for reading raw source data and mapping
    it into the canonical Candidate model. They must not perform data validation,
    normalization, or merging.
    """
    
    @abstractmethod
    def load(self, file_path: Path) -> List[Candidate]:
        """
        Reads the data source and maps records to a list of Candidate objects.
        
        Args:
            file_path (Path): Path to the source file.
            
        Returns:
            List[Candidate]: A list of mapped canonical Candidate objects.
        """
        pass
