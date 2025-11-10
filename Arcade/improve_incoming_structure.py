#!/usr/bin/env python3
"""
Improve Incoming Directory Structure for Accuracy

Reorganizes the incoming directory with precise categorization
and improved file handling for real use case scenarios.
"""

import json
import time
import shutil
from pathlib import Path
from typing import Dict, List, Any


class IncomingDirectoryImprover:
    """Improves incoming directory structure for better accuracy."""
    
    def __init__(self, arcade_root: Path):
        """
        Initialize directory improver.
        
        Args:
            arcade_root: Root directory of Arcade system
        """
        self.arcade_root = Path(arcade_root)
        self.incoming_dir = self.arcade_root / "incoming"
        self.backup_dir = self.arcade_root / "incoming_backup"
        
        # Create new organized structure
        self.new_incoming = self.arcade_root / "incoming_v2"
        
        # Subdirectories by category
        self.categories = {
            "core_network": self.new_incoming / "core_network",
            "controlled_scenarios": self.new_incoming / "controlled_scenarios", 
            "habitat_specific": self.new_incoming / "habitat_specific",
            "specialized_analysis": self.new_incoming / "specialized_analysis",
            "instrumentation": self.new_incoming / "instrumentation",
            "batch_processing": self.new_incoming / "batch_processing",
            "testing": self.new_incoming / "testing",
            "monitoring": self.new_incoming / "monitoring",
            "legacy": self.new_incoming / "legacy",
            "fallback": self.new_incoming / "fallback"
        }
        
    def backup_existing_incoming(self):
        """Backup existing incoming directory."""
        if self.incoming_dir.exists():
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            shutil.copytree(self.incoming_dir, self.backup_dir)
            print(f"📦 Backed up existing incoming to: {self.backup_dir}")
    
    def create_new_structure(self):
        """Create the new organized directory structure."""
        # Remove old new_incoming if exists
        if self.new_incoming.exists():
            shutil.rmtree(self.new_incoming)
        
        # Create main directory
        self.new_incoming.mkdir(exist_ok=True)
        
        # Create category directories
        for category_name, category_path in self.categories.items():
            category_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created category: {category_name}")
        
        # Create metadata directory
        metadata_dir = self.new_incoming / "metadata"
        metadata_dir.mkdir(exist_ok=True)
        
        # Create index files
        self._create_category_index(metadata_dir)
        self._create_routing_rules(metadata_dir)
        
        print(f"✅ New structure created: {self.new_incoming}")
    
    def _create_category_index(self, metadata_dir: Path):
        """Create category index file."""
        index = {
            "version": "2.0",
            "created": time.time(),
            "categories": {
                "core_network": {
                    "description": "Core network visualization and analysis",
                    "tools": ["network_visualizer_main", "network_core_analysis", "network_topology"],
                    "priority": "high"
                },
                "controlled_scenarios": {
                    "description": "Controlled test scenarios and use cases",
                    "tools": ["small_team_network", "integration_points", "dynamic_movement", "high_traffic"],
                    "priority": "medium"
                },
                "habitat_specific": {
                    "description": "Habitat-based node processing",
                    "tools": ["core_nexus_analysis", "hub_zone_analysis", "bridge_territory_analysis", "peripheral_analysis"],
                    "priority": "medium"
                },
                "specialized_analysis": {
                    "description": "Specialized network analysis tools",
                    "tools": ["centrality_analysis", "movement_patterns", "integration_detection"],
                    "priority": "medium"
                },
                "instrumentation": {
                    "description": "Compass and geometric instrumentation",
                    "tools": ["compass_instrumentation", "geometric_analysis", "spatial_navigation"],
                    "priority": "low"
                },
                "batch_processing": {
                    "description": "Batch and historical analysis",
                    "tools": ["historical_analysis", "report_generation", "automated_reports"],
                    "priority": "low"
                },
                "testing": {
                    "description": "Testing and validation payloads",
                    "tools": ["controlled_test", "performance_test", "integration_test"],
                    "priority": "low"
                },
                "monitoring": {
                    "description": "System health and monitoring",
                    "tools": ["health_monitoring", "system_status", "performance_health"],
                    "priority": "high"
                },
                "legacy": {
                    "description": "Legacy compatibility tools",
                    "tools": ["audio_tool", "visual_tool", "games_tool"],
                    "priority": "low"
                },
                "fallback": {
                    "description": "Default and unmapped tool routing",
                    "tools": ["default_tool", "unknown_tool", "fallback_processing"],
                    "priority": "low"
                }
            }
        }
        
        with open(metadata_dir / "categories.json", 'w') as f:
            json.dump(index, f, indent=2)
    
    def _create_routing_rules(self, metadata_dir: Path):
        """Create routing rules file."""
        rules = {
            "version": "2.0",
            "routing_strategy": "category_based",
            "default_zone": "visual",
            "fallback_zone": "visual",
            "rules": {
                "pattern_matching": {
                    "network_visualizer.*": "core_network",
                    "small_team.*": "controlled_scenarios",
                    "integration_points": "controlled_scenarios",
                    "dynamic_movement.*": "controlled_scenarios",
                    "high_traffic.*": "controlled_scenarios",
                    "core_nexus.*": "habitat_specific",
                    "hub_zone.*": "habitat_specific",
                    "bridge_territory.*": "habitat_specific",
                    "peripheral.*": "habitat_specific",
                    "centrality.*": "specialized_analysis",
                    "movement.*": "specialized_analysis",
                    "compass.*": "instrumentation",
                    "geometric.*": "instrumentation",
                    "test.*": "testing",
                    "monitoring.*": "monitoring",
                    "audio_.*": "legacy",
                    "visual_.*": "legacy",
                    "games_.*": "legacy"
                },
                "exact_matching": {
                    "network_visualizer": "core_network",
                    "arcade_routing_demo": "testing",
                    "network_node_processor": "specialized_analysis"
                }
            }
        }
        
        with open(metadata_dir / "routing_rules.json", 'w') as f:
            json.dump(rules, f, indent=2)
    
    def migrate_existing_files(self):
        """Migrate existing files to new structure."""
        if not self.incoming_dir.exists():
            print("📭 No existing incoming directory to migrate")
            return
        
        migrated_count = 0
        
        for file_path in self.incoming_dir.glob("*.json"):
            # Determine category based on filename
            category = self._categorize_file(file_path.name)
            
            # Copy to appropriate category
            dest_path = self.categories[category] / file_path.name
            shutil.copy2(file_path, dest_path)
            
            # Add metadata
            self._add_file_metadata(dest_path, category)
            
            migrated_count += 1
            print(f"📄 Migrated: {file_path.name} → {category}/")
        
        print(f"✅ Migrated {migrated_count} files to new structure")
    
    def _categorize_file(self, filename: str) -> str:
        """Categorize file based on filename patterns."""
        filename_lower = filename.lower()
        
        # Pattern matching for categorization
        if "network_visualizer" in filename_lower:
            return "core_network"
        elif any(pattern in filename_lower for pattern in ["small_team", "integration_points", "dynamic_movement", "high_traffic"]):
            return "controlled_scenarios"
        elif any(pattern in filename_lower for pattern in ["core_nexus", "hub_zone", "bridge_territory", "peripheral"]):
            return "habitat_specific"
        elif any(pattern in filename_lower for pattern in ["centrality", "movement", "integration_detection"]):
            return "specialized_analysis"
        elif any(pattern in filename_lower for pattern in ["compass", "geometric", "spatial"]):
            return "instrumentation"
        elif any(pattern in filename_lower for pattern in ["historical", "report", "batch"]):
            return "batch_processing"
        elif any(pattern in filename_lower for pattern in ["test", "scenario", "validation"]):
            return "testing"
        elif any(pattern in filename_lower for pattern in ["monitoring", "health", "status"]):
            return "monitoring"
        elif any(pattern in filename_lower for pattern in ["audio", "visual", "games"]):
            return "legacy"
        else:
            return "fallback"
    
    def _add_file_metadata(self, file_path: Path, category: str):
        """Add metadata to migrated file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Add migration metadata
            data['_migration_metadata'] = {
                'migrated_at': time.time(),
                'category': category,
                'original_path': str(file_path.relative_to(self.new_incoming)),
                'migration_version': '2.0'
            }
            
            # Write back with metadata
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Could not add metadata to {file_path}: {e}")
    
    def create_sample_payloads(self):
        """Create sample payloads for testing new structure."""
        samples = {
            "core_network/sample_network_visualizer.json": {
                "tool": "network_visualizer_main",
                "zone": "visual",
                "sample": True,
                "description": "Sample core network visualization payload"
            },
            "controlled_scenarios/sample_small_team.json": {
                "tool": "small_team_network",
                "zone": "visual", 
                "sample": True,
                "description": "Sample small team network scenario"
            },
            "habitat_specific/sample_core_nexus.json": {
                "tool": "core_nexus_analysis",
                "zone": "visual",
                "sample": True,
                "description": "Sample core nexus habitat analysis"
            },
            "instrumentation/sample_compass.json": {
                "tool": "compass_instrumentation",
                "zone": "visual",
                "sample": True,
                "description": "Sample compass instrumentation payload"
            }
        }
        
        for relative_path, sample_data in samples.items():
            file_path = self.new_incoming / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add timestamp and basic structure
            sample_data.update({
                "timestamp": time.time(),
                "node_count": 0,
                "event_count": 0,
                "node_states": {},
                "movement_events": []
            })
            
            with open(file_path, 'w') as f:
                json.dump(sample_data, f, indent=2)
            
            print(f"📝 Created sample: {relative_path}")
    
    def generate_summary_report(self):
        """Generate summary report of the improvement."""
        report = {
            "improvement_summary": {
                "version": "2.0",
                "timestamp": time.time(),
                "old_incoming": str(self.incoming_dir),
                "new_incoming": str(self.new_incoming),
                "backup_location": str(self.backup_dir)
            },
            "categories_created": list(self.categories.keys()),
            "files_migrated": len(list(self.backup_dir.glob("*.json"))) if self.backup_dir.exists() else 0,
            "sample_files_created": 4,
            "next_steps": [
                "Update dispatcher.py to use new structure",
                "Test routing with new categories",
                "Monitor file processing in new structure",
                "Update documentation to reflect new organization"
            ]
        }
        
        report_path = self.new_incoming / "improvement_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Summary report: {report_path}")
        return report
    
    def run_improvement(self):
        """Run the complete improvement process."""
        print("🔧 Starting Incoming Directory Improvement")
        print("=" * 60)
        
        # Step 1: Backup existing
        print("\n1️⃣  Backing up existing directory...")
        self.backup_existing_incoming()
        
        # Step 2: Create new structure
        print("\n2️⃣  Creating new organized structure...")
        self.create_new_structure()
        
        # Step 3: Migrate existing files
        print("\n3️⃣  Migrating existing files...")
        self.migrate_existing_files()
        
        # Step 4: Create sample payloads
        print("\n4️⃣  Creating sample payloads...")
        self.create_sample_payloads()
        
        # Step 5: Generate report
        print("\n5️⃣  Generating summary report...")
        report = self.generate_summary_report()
        
        print("\n" + "=" * 60)
        print("✅ INCOMING DIRECTORY IMPROVEMENT COMPLETE")
        print("=" * 60)
        print(f"📁 New structure: {self.new_incoming}")
        print(f"📦 Backup: {self.backup_dir}")
        print(f"📊 Categories: {len(self.categories)}")
        print(f"📄 Files migrated: {report['files_migrated']}")
        print(f"📝 Samples created: {report['sample_files_created']}")
        
        print(f"\n🎯 Next steps:")
        for step in report['next_steps']:
            print(f"  • {step}")


def main():
    """Main improvement runner."""
    arcade_root = Path("e:/Projects/Atmosphere/Arcade")
    
    if not arcade_root.exists():
        print(f"❌ Arcade directory not found: {arcade_root}")
        return
    
    improver = IncomingDirectoryImprover(arcade_root)
    improver.run_improvement()


if __name__ == "__main__":
    main()
