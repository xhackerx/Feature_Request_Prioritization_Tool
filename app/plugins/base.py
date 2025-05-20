from abc import ABC, abstractmethod

class PluginBase(ABC):
    """Base class for all plugins"""
    
    @abstractmethod
    def initialize(self):
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    def execute(self, context):
        """Execute the plugin's main functionality"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Cleanup plugin resources"""
        pass

class PluginManager:
    """Manages plugin lifecycle and execution"""
    
    def __init__(self):
        self.plugins = {}
        self.active_plugins = set()
    
    def register_plugin(self, plugin_id, plugin_class):
        """Register a new plugin"""
        if plugin_id in self.plugins:
            raise ValueError(f"Plugin {plugin_id} already registered")
        self.plugins[plugin_id] = plugin_class()
    
    def activate_plugin(self, plugin_id):
        """Activate a registered plugin"""
        if plugin_id not in self.plugins:
            raise ValueError(f"Plugin {plugin_id} not found")
        plugin = self.plugins[plugin_id]
        plugin.initialize()
        self.active_plugins.add(plugin_id)
    
    def execute_plugin(self, plugin_id, context):
        """Execute a specific plugin"""
        if plugin_id not in self.active_plugins:
            raise ValueError(f"Plugin {plugin_id} not active")
        return self.plugins[plugin_id].execute(context)