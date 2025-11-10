"""
VS Code integration for Mental Load Balancer.
This module provides VS Code-specific monitoring and interaction capabilities.
"""
import os
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import json

# VS Code API types for type hints
class TextDocument:
    language_id: str
    file_name: str

class Diagnostic:
    severity: int
    message: str
    range: Any

class TextEditor:
    document: TextDocument

class Window:
    active_text_editor: Optional[TextEditor]
    on_did_change_active_text_editor: Any
    on_did_change_text_document: Any
    on_did_save_text_document: Any

class Workspace:
    on_did_open_text_document: Any
    on_did_close_text_document: Any
    on_did_save_text_document: Any
    on_did_change_text_document: Any

class VSCodeAPI:
    window: Window
    workspace: Workspace
    DiagnosticSeverity: Any

# Try to import vscode module
try:
    import vscode
    VSCODE_AVAILABLE = True
except ImportError:
    VSCODE_AVAILABLE = False
    print("VS Code extension API not available. Running in standalone mode.")

@dataclass
class VSCodeMetrics:
    """Metrics specific to VS Code environment."""
    active_document: Optional[str] = None
    document_language: Optional[str] = None
    open_documents: int = 0
    diagnostics: List[Diagnostic] = None
    last_save_time: float = 0
    last_activity_time: float = 0

class VSCodeMonitor:
    """Monitors VS Code specific events and metrics."""
    
    def __init__(self, vscode_api: Optional[VSCodeAPI] = None):
        self.vscode = vscode if VSCODE_AVAILABLE and vscode_api is None else vscode_api
        self.metrics = VSCodeMetrics()
        self._callbacks = {
            'on_metrics_update': [],
            'on_intervention': []
        }
        
        if self.vscode and VSCODE_AVAILABLE:
            self._setup_event_listeners()
    
    def _setup_event_listeners(self):
        """Set up VS Code event listeners."""
        self.vscode.window.on_did_change_active_text_editor(self._on_editor_changed)
        self.vscode.workspace.on_did_open_text_document(self._on_document_opened)
        self.vscode.workspace.on_did_save_text_document(self._on_document_saved)
        self.vscode.workspace.on_did_change_text_document(self._on_document_changed)
        
        # Initial metrics update
        self._update_metrics()
    
    def _on_editor_changed(self, editor: Optional[TextEditor]):
        """Handle editor change events."""
        if editor:
            self.metrics.active_document = editor.document.file_name
            self.metrics.document_language = editor.document.language_id
        self._update_metrics()
    
    def _on_document_opened(self, document: TextDocument):
        """Handle document open events."""
        self.metrics.open_documents += 1
        self._update_metrics()
    
    def _on_document_saved(self, document: TextDocument):
        """Handle document save events."""
        self.metrics.last_save_time = time.time()
        self._update_metrics()
    
    def _on_document_changed(self, event):
        """Handle document change events."""
        self.metrics.last_activity_time = time.time()
        self._update_metrics()
    
    def _update_metrics(self):
        """Update metrics and notify listeners."""
        # Update diagnostics if available
        if self.vscode and hasattr(self.vscode.window, 'activeTextEditor'):
            editor = self.vscode.window.activeTextEditor
            if editor:
                self.metrics.diagnostics = self.vscode.languages.getDiagnostics(editor.document.uri)
        
        # Notify listeners
        for callback in self._callbacks['on_metrics_update']:
            callback(self.metrics)
    
    def on_metrics_update(self, callback: Callable[[VSCodeMetrics], None]):
        """Register a callback for metrics updates."""
        self._callbacks['on_metrics_update'].append(callback)
    
    def on_intervention(self, callback: Callable[[str, str], None]):
        """Register a callback for intervention requests."""
        self._callbacks['on_intervention'].append(callback)
    
    def show_notification(self, title: str, message: str, severity: str = 'info'):
        """Show a notification in VS Code."""
        if not self.vscode or not VSCODE_AVAILABLE:
            print(f"[{severity.upper()}] {title}: {message}")
            return
            
        if severity == 'error':
            self.vscode.window.show_error_message(f"{title}: {message}")
        elif severity == 'warning':
            self.vscode.window.show_warning_message(f"{title}: {message}")
        else:
            self.vscode.window.show_information_message(f"{title}: {message}")

# Example usage
if __name__ == "__main__":
    # This will only work when run within VS Code's extension host
    if VSCODE_AVAILABLE:
        vscode_monitor = VSCodeMonitor()
        
        def on_metrics_update(metrics: VSCodeMetrics):
            print(f"Active document: {metrics.active_document}")
            print(f"Language: {metrics.document_language}")
            print(f"Open documents: {metrics.open_documents}")
            
        vscode_monitor.on_metrics_update(on_metrics_update)
    else:
        print("VS Code integration is not available in standalone mode.")
