#!/usr/bin/env python3
"""Extract records from Feishu raw JSON and save as clean_data.json format."""
import json, subprocess, requests
from datetime import datetime

BASE_TOKEN = 'ByUibD4rxaBmHlswtT5cz3PsnNf'
TABLE_ID = 'tblCQ1JwLliZON3a'
VIEW_ID = 'vewpI8lyYw'

def fetch_records_json():
    cmd = [
        'lark-cli', 'base', '+record-list',
        '--base-token', BASE_TOKEN,
        '--table-id', TABLE_ID,
        '--view-id', VIEW_ID,
        '--offset', '0',
        '--limit', '200',
        '--as', 'user',
        '--format', 'json'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'Error fetching: {result.stderr}')
        return None
    return json.loads(result.stdout)

def map_records(data):
    """Map raw API response to clean_data format."""
    fields = data['data']['fields']
    record_ids = data['data']['record_id_list']
    rows = data['data']['data']
    
    # Create field index mapping
    # Find key field indices
    field_to_idx = {}
    for i, name in enumerate(fields):
        field_to_idx[name] = i
    
    print(f'Field mapping:')
    for i, name in enumerate(fields):
        print(f'  [{i:2d}] {name}')
    
    # Also get field_id_list for lookup
    field_ids = data['data']['field_id_list']
    
    records = []
    for ri, row in enumerate(rows):
        rec = {}
        rec_id = record_ids[ri] if ri < len(record_ids) else f'rec_auto_{ri}'
        
        # Helper to get field value by name
        def gf(name):
            idx = field_to_idx.get(name)
            if idx is None or idx >= len(row):
                return None
            return row[idx]
        
        # title = 工作内容 (index 0 likely)
        title = gf('工作内容') or ''
        
        # progress = 进展 (array like ["进行中"])
        progress_raw = gf('进展')
        progress = progress_raw[0] if isinstance(progress_raw, list) and progress_raw else ''
        
        # dates
        test_date = gf('最晚转测时间') or ''
        freeze_date = gf('封板时间') or ''
        version_date = gf('版更时间') or ''
        online_date = gf('上线时间（功能owner维护）') or ''
        start_date = gf('启动日期') or ''
        end_date = gf('任务结束') or ''
        
        # assignee
        assignee_raw = gf('执行人')
        assignee = assignee_raw if isinstance(assignee_raw, list) else []
        
        # region - try different field names
        region = gf('地区')
        if region is None:
            region = gf('对外版本')
        if not isinstance(region, list):
            region = []
        
        records.append({
            '工作内容': title,
            '进展': [progress],
            '最晚转测时间': test_date,
            '封板时间': freeze_date,
            '版更时间': version_date,
            '上线时间（功能owner维护）': online_date,
            '启动日期': start_date,
            '任务结束': end_date,
            '执行人': assignee,
            '地区': region,
            '_id': rec_id
        })
    
    return records

# Main
data = fetch_records_json()
if not data:
    print('Failed to fetch data')
    exit(1)

records = map_records(data)
print(f'\nTotal records: {len(records)}')

# Save as clean_data.json format
output = {'records': records}
with open('/tmp/clean_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f'Saved to /tmp/clean_data.json')

# Summary
assignee_task_count = {}
for r in records:
    for a in r['执行人']:
        name = a.get('name', '?')
        assignee_task_count[name] = assignee_task_count.get(name, 0) + 1
print(f'Unique assignees: {len(assignee_task_count)}')
print(f'\nTasks per assignee:')
for name, count in sorted(assignee_task_count.items(), key=lambda x: -x[1]):
    print(f'  {name}: {count} tasks')