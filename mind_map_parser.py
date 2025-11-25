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
            # Skip empty DataFrames
            if df is None or df.empty or len(df) == 0:
                continue
            
            # Skip if no columns
            if len(df.columns) == 0:
                continue
            
            try:
                # Store the full sheet data for context (this is what AI will analyze)
                self.tags[f'_sheet_{sheet_name}'] = {
                    'type': 'sheet',
                    'data': df.to_dict('records'),
                    'columns': list(df.columns)
                }
                
                # Check if this is the new organized format (has Full_Tag_Name, Tag_Logic, Customer_Scenarios)
                is_organized_format = any(col in df.columns for col in ['Full_Tag_Name', 'Tag_Logic', 'Customer_Scenarios'])
                
                if is_organized_format:
                    # New organized format - use Full_Tag_Name as primary tag identifier
                    tag_name_col = 'Full_Tag_Name' if 'Full_Tag_Name' in df.columns else None
                    tag_id_col = 'Tag_ID' if 'Tag_ID' in df.columns else None
                    tag_logic_col = 'Tag_Logic' if 'Tag_Logic' in df.columns else None
                    customer_scenarios_col = 'Customer_Scenarios' if 'Customer_Scenarios' in df.columns else None
                    sheet_name_col = 'Sheet_Name' if 'Sheet_Name' in df.columns else None
                    
                    for idx, row in df.iterrows():
                        try:
                            # Get tag name from Full_Tag_Name column
                            if tag_name_col:
                                tag_value = str(row[tag_name_col]).strip()
                            else:
                                continue
                            
                            if tag_value and tag_value.lower() not in ['nan', 'none', '', 'n/a']:
                                # Get tag ID if available
                                tag_id = str(row[tag_id_col]).strip() if tag_id_col and pd.notna(row.get(tag_id_col)) else f"T{idx:04d}"
                                
                                # Get sheet name from column or use sheet name
                                tag_sheet = str(row[sheet_name_col]).strip() if sheet_name_col and pd.notna(row.get(sheet_name_col)) else sheet_name
                                
                                # Get tag logic
                                tag_logic = str(row[tag_logic_col]).strip() if tag_logic_col and pd.notna(row.get(tag_logic_col)) else ""
                                
                                # Get customer scenarios
                                customer_scenarios = str(row[customer_scenarios_col]).strip() if customer_scenarios_col and pd.notna(row.get(customer_scenarios_col)) else ""
                                
                                # Create unique key for tag (use Tag_ID if available, otherwise use tag name + index)
                                tag_key = f"{tag_id}_{tag_value}_{idx}" if tag_id_col else f"{tag_value}_{sheet_name}_{idx}"
                                
                                if tag_key not in self.tags:
                                    self.tags[tag_key] = {
                                        'tag_id': tag_id,
                                        'tag_name': tag_value,
                                        'sheet': tag_sheet,
                                        'row': idx,
                                        'logic': tag_logic,
                                        'customer_scenarios': customer_scenarios,
                                        'full_row': row.to_dict()
                                    }
                        except Exception as row_error:
                            # Skip problematic rows instead of crashing
                            print(f"Warning: Error processing row {idx} in sheet '{sheet_name}': {row_error}")
                            continue
                else:
                    # Legacy format - use old extraction method
                # Try to identify tag columns (common patterns)
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
                        try:
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
                        except Exception as row_error:
                            # Skip problematic rows instead of crashing
                            continue
            except Exception as sheet_error:
                # Skip problematic sheets instead of crashing
                print(f"Warning: Error processing sheet '{sheet_name}': {sheet_error}, skipping...")
                continue
    
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
        """Get a detailed summary of the mind map with full tag logic for AI context"""
        summary = []
        summary.append("=" * 80)
        summary.append("TAG CLASSIFICATION MIND MAP - COMPLETE LOGIC REFERENCE")
        summary.append("=" * 80)
        summary.append(f"\nTotal Sheets: {len(self.data)}")
        summary.append("\n" + "=" * 80)
        
        for sheet_name, df in self.data.items():
            # Skip empty or invalid DataFrames
            if df is None or df.empty or len(df) == 0:
                continue
            
            try:
                summary.append(f"\n{'='*80}")
                summary.append(f"SHEET: {sheet_name}")
                summary.append(f"{'='*80}")
                summary.append(f"Total Rows: {len(df)}, Columns: {len(df.columns)}")
                
                if len(df.columns) > 0:
                    # Check if this is the new organized format
                    is_organized_format = any(col in df.columns for col in ['Full_Tag_Name', 'Tag_Logic', 'Customer_Scenarios'])
                    
                    if is_organized_format:
                        # New organized format - present in a cleaner, more structured way
                        summary.append(f"\nColumn Structure: {', '.join(str(col) for col in df.columns)}")
                        summary.append("\n" + "-" * 80)
                        summary.append("COMPLETE TAG LOGIC (Organized Format - All Tags with Full Details):")
                        summary.append("-" * 80)
                        
                        for idx, row in df.iterrows():
                            try:
                                tag_id = str(row.get('Tag_ID', '')).strip() if 'Tag_ID' in df.columns and pd.notna(row.get('Tag_ID')) else f"T{idx:04d}"
                                tag_name = str(row.get('Full_Tag_Name', '')).strip() if 'Full_Tag_Name' in df.columns and pd.notna(row.get('Full_Tag_Name')) else ""
                                tag_sheet = str(row.get('Sheet_Name', '')).strip() if 'Sheet_Name' in df.columns and pd.notna(row.get('Sheet_Name')) else sheet_name
                                tag_logic = str(row.get('Tag_Logic', '')).strip() if 'Tag_Logic' in df.columns and pd.notna(row.get('Tag_Logic')) else ""
                                customer_scenarios = str(row.get('Customer_Scenarios', '')).strip() if 'Customer_Scenarios' in df.columns and pd.notna(row.get('Customer_Scenarios')) else ""
                                
                                if tag_name and tag_name.lower() not in ['nan', 'none', '']:
                                    summary.append(f"\n[TAG ID: {tag_id}]")
                                    summary.append(f"TAG NAME: {tag_name}")
                                    summary.append(f"CATEGORY/SHEET: {tag_sheet}")
                                    if tag_logic:
                                        summary.append(f"TAG LOGIC: {tag_logic}")
                                    if customer_scenarios:
                                        summary.append(f"EXAMPLE CUSTOMER SCENARIOS: {customer_scenarios}")
                                    summary.append("-" * 80)
                            except Exception as row_error:
                                continue
                    else:
                        # Legacy format - use old method
                    summary.append(f"\nColumn Structure: {', '.join(str(col) for col in df.columns)}")
                    summary.append("\n" + "-" * 80)
                    summary.append("COMPLETE TAG LOGIC (All Rows with Full Details):")
                    summary.append("-" * 80)
                    
                    # Include ALL rows with complete logic, not just samples
                    for idx, row in df.iterrows():
                        try:
                            row_details = []
                            tag_name = None
                            
                            # Extract all column values for this row
                            for col in df.columns:
                                try:
                                    val = str(row[col]).strip()
                                    if val and val.lower() not in ['nan', 'none', '']:
                                        # Identify potential tag name column
                                        col_lower = str(col).lower()
                                        if any(keyword in col_lower for keyword in ['tag', 'category', 'type', 'label', 'name', 'classification']):
                                            if not tag_name:
                                                tag_name = val
                                        row_details.append(f"{col}: {val}")
                                except:
                                    continue
                            
                            if row_details:
                                # Format: Tag Name (if found) | All Logic Details
                                tag_prefix = f"TAG: {tag_name} | " if tag_name else ""
                                summary.append(f"\nRow {idx}: {tag_prefix}{' | '.join(row_details)}")
                        except Exception as row_error:
                            continue
                    
                    summary.append("\n" + "-" * 80)
            except Exception as e:
                # Skip problematic sheets
                continue
        
        summary.append("\n" + "=" * 80)
        summary.append("END OF MIND MAP")
        summary.append("=" * 80)
        
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

