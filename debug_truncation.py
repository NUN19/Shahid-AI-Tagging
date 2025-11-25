import os
import sys
from mind_map_parser import MindMapParser

# Set up paths
base_dir = os.getcwd()
excel_path = os.path.join(base_dir, "List of tags 2025.xlsx")

print(f"Checking file: {excel_path}")
if not os.path.exists(excel_path):
    print("Error: Excel file not found!")
    sys.exit(1)

# Initialize parser
try:
    parser = MindMapParser(excel_file_path=excel_path)
    print(f"Loaded {len(parser.tags)} tags.")
except Exception as e:
    print(f"Error loading parser: {e}")
    sys.exit(1)

# Replicate _prepare_tag_data logic
def prepare_tag_data(parser):
    all_tags = parser.get_all_tags()
    if not all_tags:
        return []
    
    tag_data_list = []
    for tag_key, tag_info in all_tags.items():
        if 'tag_name' in tag_info:
            tag_data_list.append({
                'tag_id': tag_info.get('tag_id', ''),
                'tag_name': tag_info.get('tag_name', ''),
                'tag_logic': tag_info.get('logic', ''),
                'customer_scenarios': tag_info.get('customer_scenarios', ''),
                'sheet': tag_info.get('sheet', '')
            })
    return tag_data_list

tag_data_list = prepare_tag_data(parser)
print(f"Prepared {len(tag_data_list)} tag entries.")

tags_for_comparison = []
for tag_data in tag_data_list:
    tag_entry = f"""
[TAG ID: {tag_data['tag_id']}]
TAG NAME: {tag_data['tag_name']}
TAG LOGIC: {tag_data['tag_logic']}
EXAMPLE CUSTOMER SCENARIOS: {tag_data['customer_scenarios']}
CATEGORY: {tag_data['sheet']}
"""
    tags_for_comparison.append(tag_entry)

tags_text = "\n".join(tags_for_comparison)
print(f"Total tags text length: {len(tags_text)} characters")

if len(tags_text) > 15000:
    print("TRUNCATION DETECTED!")
    truncated_text = tags_text[:15000]
    last_tag_end = truncated_text.rfind('\n[TAG ID:')
    if last_tag_end > 12000:
        print(f"Truncating at index {last_tag_end}")
        final_text = truncated_text[:last_tag_end]
        print(f"Final text length: {len(final_text)}")
        
        # Count how many tags made it
        count = final_text.count("[TAG ID:")
        print(f"Tags included after truncation: {count} / {len(tag_data_list)}")
        
        # Print the last tag that made it
        print("Last included tag:")
        print(final_text.split('\n[TAG ID:')[-1])
else:
    print("No truncation needed.")
