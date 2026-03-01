"""
Data Manager Module
Handles data storage, export, and management
"""

import json
import csv
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging


class DataManager:
    """Manages data storage and export operations"""
    
    def __init__(self):
        self.data_dir = Path.cwd() / "moodle_data"
        self.data_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def save_data(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Path]:
        """Save data to files with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = {}
        
        try:
            # Save individual data types
            data_mappings = {
                'courses': 'courses',
                'events': 'events',
                'notifications': 'notifications',
                'recent_courses': 'recent_courses',
                'calendar': 'calendar'
            }
            
            for key, filename in data_mappings.items():
                if key in data and data[key]:
                    file_path = self.data_dir / f"{prefix}{filename}_{timestamp}.json"
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data[key], f, indent=2, ensure_ascii=False)
                    saved_files[key] = file_path
                    self.logger.info(f"Saved {key} to {file_path}")
            
            # Save combined data
            combined_path = self.data_dir / f"{prefix}all_data_{timestamp}.json"
            with open(combined_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            saved_files['combined'] = combined_path
            
            return saved_files
            
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
            raise
    
    def export_to_csv(self, data: Dict[str, Any], data_type: str) -> Optional[Path]:
        """Export specific data type to CSV"""
        try:
            if data_type not in data or not data[data_type]:
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.data_dir / f"{data_type}_{timestamp}.csv"
            
            # Convert to DataFrame and save
            df = pd.json_normalize(data[data_type])
            df.to_csv(file_path, index=False, encoding='utf-8')
            
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            return None
    
    def export_to_excel(self, data: Dict[str, Any]) -> Optional[Path]:
        """Export all data to Excel with multiple sheets"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.data_dir / f"moodle_data_{timestamp}.xlsx"
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for key, values in data.items():
                    if values and isinstance(values, list):
                        df = pd.json_normalize(values)
                        df.to_excel(writer, sheet_name=key.capitalize(), index=False)
            
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {e}")
            return None
    
    def load_history(self) -> List[Dict[str, Any]]:
        """Load historical data files"""
        history = []
        
        try:
            for file_path in sorted(self.data_dir.glob("all_data_*.json"), reverse=True):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    history.append({
                        'file': file_path.name,
                        'path': file_path,
                        'timestamp': file_path.stem.replace('all_data_', ''),
                        'size': file_path.stat().st_size,
                        'data_summary': {
                            'courses': len(data.get('courses', [])),
                            'events': len(data.get('events', [])),
                            'notifications': len(data.get('notifications', [])),
                            'recent_courses': len(data.get('recent_courses', [])),
                            'calendar': len(data.get('calendar', []))
                        }
                    })
                except Exception as e:
                    self.logger.error(f"Error loading {file_path}: {e}")
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error loading history: {e}")
            return []
    
    def get_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate statistics from data"""
        stats = {}
        
        try:
            # Course statistics
            if data.get('courses'):
                courses = data['courses']
                stats['courses'] = {
                    'total': len(courses),
                    'in_progress': sum(1 for c in courses if c.get('progress') != 100),
                    'completed': sum(1 for c in courses if c.get('progress') == 100)
                }
            
            # Event statistics
            if data.get('events'):
                events = data['events']
                stats['events'] = {
                    'total': len(events),
                    'upcoming': sum(1 for e in events if not e.get('is_past')),
                    'past': sum(1 for e in events if e.get('is_past'))
                }
            
            # Notification statistics
            if data.get('notifications'):
                notifications = data['notifications']
                stats['notifications'] = {
                    'total': len(notifications),
                    'unread': sum(1 for n in notifications if not n.get('is_read'))
                }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error generating statistics: {e}")
            return {}