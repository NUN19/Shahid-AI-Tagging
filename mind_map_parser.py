"""
Mind Map Parser
Reads Excel mind map and extracts tag logic
Supports both file-based and in-memory data
"""

import pandas as pd
import os

class MindMapParser:
    def __init__(self, excel_file_path=None, data_dict=None):
        """
        Initialize parser with Excel file or in-memory data
        
        Args:
            excel_file_path: Path to Excel file (for file-based loading)
            data_dict: Dictionary of {sheet_name: DataFrame} (for in-memory data)
        """
        self.excel_file_path = excel_file_path
        self.data = None
        self.tags = {}
        
        if data_dict is not None:
            # Initialize from in-memory data (client-side processed)
            self.data = data_dict
            self._extract_tags()
        elif excel_file_path:
            # Initialize from file (backward compatibility)
            if not os.path.exists(excel_file_path):
                raise FileNotFoundError(f"Mind map file not found: {excel_file_path}")
            self.load_mind_map()
        else:
            raise ValueError("Either excel_file_path or data_dict must be provided")
    
    def load_mind_map(self):
        """Load and parse the Excel mind map from file"""
        try:
            # Read all sheets
            excel_data = pd.read_excel(self.excel_file_path, sheet_name=None)
            
            # Store all data
            self.data = excel_data
            
            # Extract tags and their logic from all sheets
            self._extract_tags()
            
        except Exception as e:
            raise Exception(f"Error loading mind map: {str(e)}")
    
    def load_from_dict(self, data_dict):
        """Load mind map from dictionary (for client-side processed data)"""
        self.data = data_dict
        self._extract_tags()
    
    def _extract_tags(self):
        """Extract tags and their logic from Excel sheets"""
        self.tags = {}
        
        for sheet_name, df in self.data.items():
            # Store the full sheet data for context (this is what AI will analyze)
            self.tags[f'_sheet_{sheet_name}'] = {
                'type': 'sheet',
                'data': df.to_dict('records'),
                'columns': list(df.columns)
            }
            
            # Try to identify tag columns (common patterns)
            # Look for columns that might contain tags
            tag_columns = []
            for col in df.columns:
                col_str = str(col).lower()
                if any(keyword in col_str for keyword in ['tag', 'category', 'type', 'label', 'classification']):
                    tag_columns.append(col)
            
            # If no obvious tag column found, use first column as potential tag column
            if not tag_columns and len(df.columns) > 0:
                tag_columns = [df.columns[0]]
            
            # Extract tags from identified columns
            for col in tag_columns:
                for idx, row in df.iterrows():
                    tag_value = str(row[col]).strip()
                    if tag_value and tag_value.lower() not in ['nan', 'none', '', 'none', 'n/a']:
                        # Create unique key for tag
                        tag_key = f"{tag_value}_{sheet_name}_{idx}"
                        if tag_key not in self.tags:
                            self.tags[tag_key] = {
                                'tag_name': tag_value,
                                'sheet': sheet_name,
                                'row': idx,
                                'logic': self._extract_row_logic(row, df.columns),
                                'full_row': row.to_dict()
                            }
    
    def _extract_row_logic(self, row, columns):
        """Extract logic/criteria from a row"""
        logic_parts = []
        for col in columns:
            value = str(row[col]).strip()
            if value and value.lower() not in ['nan', 'none', '']:
                logic_parts.append(f"{col}: {value}")
        return " | ".join(logic_parts)
    
    def get_all_tags(self):
        """Get all available tags"""
        # Filter out sheet entries and return unique tag names
        unique_tags = {}
        for k, v in self.tags.items():
            if not k.startswith('_sheet_'):
                tag_name = v.get('tag_name', k)
                if tag_name not in unique_tags:
                    unique_tags[tag_name] = v
        return unique_tags
    
    def get_mind_map_summary(self):
        """Get a summary of the mind map for AI context"""
        summary = []
        summary.append("Mind Map Structure:")
        summary.append(f"Total Sheets: {len(self.data)}")
        
        for sheet_name, df in self.data.items():
            summary.append(f"\nSheet: {sheet_name}")
            summary.append(f"  Rows: {len(df)}, Columns: {len(df.columns)}")
            summary.append(f"  Columns: {', '.join(df.columns)}")
            
            # Add sample data
            if len(df) > 0:
                summary.append(f"  Sample rows (first 3):")
                for idx in range(min(3, len(df))):
                    row_summary = []
                    for col in df.columns:
                        val = str(df.iloc[idx][col]).strip()
                        if val and val.lower() not in ['nan', 'none', '']:
                            row_summary.append(f"{col}={val}")
                    if row_summary:
                        summary.append(f"    Row {idx}: {' | '.join(row_summary)}")
        
        return "\n".join(summary)
    
    def get_full_mind_map_text(self):
        """Get full mind map as formatted text for AI"""
        text_parts = []
        
        for sheet_name, df in self.data.items():
            text_parts.append(f"\n{'='*60}")
            text_parts.append(f"SHEET: {sheet_name}")
            text_parts.append(f"{'='*60}")
            
            # Add column headers
            text_parts.append("COLUMNS: " + " | ".join(df.columns))
            text_parts.append("")
            
            # Add all rows
            for idx, row in df.iterrows():
                row_data = []
                for col in df.columns:
                    val = str(row[col]).strip()
                    if val and val.lower() not in ['nan', 'none', '']:
                        row_data.append(f"{col}: {val}")
                if row_data:
                    text_parts.append(f"Row {idx}: {' | '.join(row_data)}")
        
        return "\n".join(text_parts)

