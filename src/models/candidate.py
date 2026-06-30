from typing import List, Optional
from pydantic import BaseModel, Field

class Location(BaseModel):
    """Represents a geographical location for a candidate or organization."""
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

class Skill(BaseModel):
    """Represents a professional skill possessed by the candidate."""
    name: str
    confidence: float = 0.0
    sources: List[str] = Field(default_factory=list)

class Experience(BaseModel):
    """Represents a work experience entry for the candidate."""
    company: Optional[str] = None
    title: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[Location] = None

class Education(BaseModel):
    """Represents an educational degree or certification."""
    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None

class Link(BaseModel):
    """Represents URLs related to the candidate, grouped by type."""
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    other: List[str] = Field(default_factory=list)

class Provenance(BaseModel):
    """Tracks the source systems and methods of data collected for individual fields."""
    field: str
    source: str
    method: str

class Candidate(BaseModel):
    """The canonical representation of a candidate within the data transformer pipeline."""
    candidate_id: Optional[str] = None
    full_name: Optional[str] = None
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    location: Optional[Location] = None
    links: Optional[Link] = None
    headline: Optional[str] = None
    years_experience: Optional[float] = None
    skills: List[Skill] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    provenance: List[Provenance] = Field(default_factory=list)
    overall_confidence: Optional[float] = None
