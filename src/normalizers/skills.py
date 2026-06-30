from typing import Dict

# Configurable canonical dictionary for resolving aliases
CANONICAL_SKILLS: Dict[str, str] = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "llm": "Large Language Model",
    "reactjs": "React",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "c++": "C++",
    "sql": "SQL",
    "aws": "AWS",
    "gcp": "GCP"
}

def normalize_skill(skill_name: str) -> str:
    """
    Normalizes a skill name using a configurable canonical dictionary.
    Falls back to title-casing if the skill is not explicitly mapped.
    """
    if not skill_name:
        return skill_name
        
    normalized_key = str(skill_name).strip().lower()
    
    # Apply canonical mapping if it exists
    if normalized_key in CANONICAL_SKILLS:
        return CANONICAL_SKILLS[normalized_key]
        
    # Safe fallback for unknown skills
    return str(skill_name).strip().title()
