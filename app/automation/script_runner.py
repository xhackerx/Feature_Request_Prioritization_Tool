import yaml
import json
from pathlib import Path
from jinja2 import Template

class AutomationScript:
    """Handles automation script execution"""
    
    def __init__(self, script_path):
        self.script_path = Path(script_path)
        self.load_script()
    
    def load_script(self):
        """Load automation script from YAML file"""
        with open(self.script_path) as f:
            self.script = yaml.safe_load(f)
    
    def validate_script(self):
        """Validate script structure and requirements"""
        required_fields = ['name', 'version', 'steps']
        for field in required_fields:
            if field not in self.script:
                raise ValueError(f"Missing required field: {field}")
    
    def execute(self, context=None):
        """Execute automation script"""
        self.validate_script()
        results = []
        
        for step in self.script['steps']:
            step_result = self._execute_step(step, context)
            results.append(step_result)
            
            if step.get('stop_on_error') and not step_result['success']:
                break
        
        return results
    
    def _execute_step(self, step, context):
        """Execute a single automation step"""
        step_type = step.get('type')
        if not step_type:
            return {'success': False, 'error': 'Missing step type'}
        
        handlers = {
            'api_call': self._handle_api_call,
            'webhook': self._handle_webhook,
            'plugin': self._handle_plugin,
            'condition': self._handle_condition
        }
        
        handler = handlers.get(step_type)
        if not handler:
            return {'success': False, 'error': f'Unknown step type: {step_type}'}
        
        try:
            return handler(step, context)
        except Exception as e:
            return {'success': False, 'error': str(e)}