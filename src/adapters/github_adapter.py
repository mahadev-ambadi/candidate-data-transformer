import json
import requests
from typing import List, Optional
from pathlib import Path

from src.adapters.base_adapter import BaseAdapter
from src.models.candidate import Candidate, Link, Provenance, Skill

class GitHubAdapter(BaseAdapter):
    """
    Adapter for reading candidate data from GitHub.
    Supports 'dev' mode (reading from local JSON) and 'prod' mode (fetching from REST API).
    """
    
    def __init__(self, mode: str = "dev", token: Optional[str] = None):
        """
        Args:
            mode (str): 'dev' to read local JSON, 'prod' to use GitHub API.
            token (Optional[str]): GitHub Personal Access Token for prod mode to prevent rate limiting.
        """
        self.mode = mode
        self.token = token
        
    def load(self, file_path: Path) -> List[Candidate]:
        """
        In 'dev' mode, reads a JSON file of profiles and maps them directly.
        In 'prod' mode, reads a JSON file containing GitHub usernames and fetches their 
        live profiles from the GitHub REST API.
        """
        candidates = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            for item in data:
                username = item.get("username")
                if not username:
                    continue
                    
                if self.mode == "prod":
                    candidate = self.fetch_profile(username)
                    if candidate:
                        candidates.append(candidate)
                else:
                    candidate = self._map_dev_data(item)
                    candidates.append(candidate)
                    
        except Exception as e:
            # TODO: Replace print with logger
            print(f"Error loading GitHub data from {file_path}: {e}")
            
        return candidates

    def _map_dev_data(self, data: dict) -> Candidate:
        """Maps local JSON structure to the canonical Candidate object."""
        username = data.get("username")
        name = data.get("name")
        bio = data.get("bio")
        skills_raw = data.get("skills", [])
        
        links = Link(github=f"https://github.com/{username}") if username else None
        
        skills = []
        for s in skills_raw:
            skills.append(Skill(name=s, sources=["github_profiles.json"]))
            
        provenance_records = []
        if name:
            provenance_records.append(Provenance(field="full_name", source="github_profiles.json", method="direct_mapping"))
        if bio:
            provenance_records.append(Provenance(field="headline", source="github_profiles.json", method="direct_mapping"))
        if username:
            provenance_records.append(Provenance(field="links", source="github_profiles.json", method="direct_mapping"))
        if skills:
            provenance_records.append(Provenance(field="skills", source="github_profiles.json", method="direct_mapping"))
            
        return Candidate(
            full_name=name,
            headline=bio,
            links=links,
            skills=skills,
            provenance=provenance_records
        )

    def fetch_profile(self, username: str) -> Optional[Candidate]:
        """Fetches data from GitHub REST API using a username and maps to a Candidate object."""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
            
        try:
            # 1. Fetch user profile
            response = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=10)
            if response.status_code != 200:
                # TODO: Replace print with logger
                print(f"Failed to fetch GitHub profile for {username}. Status: {response.status_code}")
                return None
                
            user_data = response.json()
            name = user_data.get("name")
            bio = user_data.get("bio")
            github_url = user_data.get("html_url")
            
            # 2. Fetch repos to derive languages (skills)
            repos_url = user_data.get("repos_url")
            skills = []
            if repos_url:
                repo_resp = requests.get(repos_url, headers=headers, timeout=10)
                if repo_resp.status_code == 200:
                    repos = repo_resp.json()
                    # Extract unique languages
                    languages = set()
                    for repo in repos:
                        lang = repo.get("language")
                        if lang:
                            languages.add(lang)
                    
                    for lang in languages:
                        skills.append(Skill(name=lang, sources=["github_api"]))
            
            # 3. Map to canonical model
            links = Link(github=github_url) if github_url else None
            
            provenance_records = []
            if name:
                provenance_records.append(Provenance(field="full_name", source="github_api", method="rest_api_fetch"))
            if bio:
                provenance_records.append(Provenance(field="headline", source="github_api", method="rest_api_fetch"))
            if github_url:
                provenance_records.append(Provenance(field="links", source="github_api", method="rest_api_fetch"))
            if skills:
                provenance_records.append(Provenance(field="skills", source="github_api", method="rest_api_fetch"))
                
            return Candidate(
                full_name=name,
                headline=bio,
                links=links,
                skills=skills,
                provenance=provenance_records
            )
        except Exception as e:
            # TODO: Replace print with logger
            print(f"Error fetching GitHub data for {username}: {e}")
            return None
