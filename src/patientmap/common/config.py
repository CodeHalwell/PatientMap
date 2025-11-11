import yaml
from patientmap.common.models import AgentSettings


class AgentConfig:
    def __init__(self, profile_path):
        self.profile = yaml.safe_load(open(profile_path))

    def get_agent(self):
        return AgentSettings(
            agent_id=self.profile.get("agent_id", "default_agent"),
            agent_name=self.profile.get("agent_name", "Default Agent"),
            model=self.profile.get("model", "gemini-2.5-flash"),
            instruction=self.profile.get("instruction", ""),
            description=self.profile.get("description", ""),
            tools=self.profile.get("tools", []),
        )
    
    def list_profiles(self):
        return self.profile.keys()
    
    def update_profile(self, key, value):
        return self.profile.update({key: value})