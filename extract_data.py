#!/usr/bin/env python3
"""Extract ALL records from Feishu (with pagination) and save as clean_data.json format."""
import json, os, subprocess, sys

BASE_TOKEN = os.environ.get('BASE_TOKEN', 'ByUibD4rxaBmHlswtT5cz3PsnNf')
TABLE_ID = 'tblCQ1JwLliZON3a'
VIEW_ID = 'vewpI8lyYw'

def fetch_page(offset, limit=200):
    cmd = [
        'lark-cli', 'base', '+record-list',
        '--base-token', BASE_TOKEN,
        '--table-id', TABLE_ID,
        '--view-id', VIEW_ID,
        '--offset', str(offset),
        '--limit', str(limit),
        '--as', 'user',
        '--format', 'json'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'  Error at offset {offset}: {result.stderr[:200]}', file=sys.stderr)
        return None
    return json.loads(result.stdout)

def fetch_all_records():
    """Fetch all records across multiple pages."""
    all_rows = []
    all_record_ids = []
    fields = None
    field_ids = None
    offset = 0
    page = 1
    
    while True:
        print(f'  Fetching page {page} (offset={offset})...')
        data = fetch_page(offset)
        if data is None:
            break
        
        rows = data['data']['data']
        record_ids = data['data']['record_id_list']
        
        if page == 1:
            fields = data['data']['fields']
            field_ids = data['data']['field_id_list']
            print(f'  Fields ({len(fields)}):')
            for i, name in enumerate(fields):
                print(f'    [{i:2d}] {name}')
        
        all_rows.extend(rows)
        all_record_ids.extend(record_ids)
        
        has_more = data['data'].get('has_more', False)
        print(f'  Page {page}: {len(rows)} records (total: {len(all_rows)}, has_more={has_more})')
        
        if not has_more:
            break
        
        offset += len(rows)
        page += 1
    
    return {
        'fields': fields,
        'field_ids': field_ids,
        'rows': all_rows,
        'record_ids': all_record_ids
    }

def map_records(data):
    """Map raw API response rows to clean_data format."""
    fields = data['fields']
    rows = data['rows']
    record_ids = data['record_ids']
    
    field_to_idx = {name: i for i, name in enumerate(fields)}
    
    records = []
    for ri, row in enumerate(rows):
        def gf(name):
            idx = field_to_idx.get(name)
            if idx is None or idx >= len(row):
                return None
            return row[idx]
        
        title = gf('工作内容') or ''
        
        progress_raw = gf('进展')
        progress = progress_raw[0] if isinstance(progress_raw, list) and progress_raw else ''
        
        test_date = gf('最晚转测时间') or ''
        freeze_date = gf('封板时间') or ''
        version_date = gf('版更时间') or ''
        online_date = gf('上线时间（功能owner维护）') or ''
        start_date = gf('启动日期') or ''
        end_date = gf('任务结束') or ''
        
        assignee_raw = gf('执行人')
        assignee = assignee_raw if isinstance(assignee_raw, list) else []
        
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
            '_id': record_ids[ri]
        })
    
    return records

# Main
print('Fetching all records from Feishu (new view: vewpI8lyYw)...')
all_data = fetch_all_records()
print(f'\nTotal rows fetched: {len(all_data["rows"])}')

records = map_records(all_data)
print(f'Total records mapped: {len(records)}')

# Region summary
region_counts = {}
for r in records:
    for x in r['地区']:
        region_counts[x] = region_counts.get(x, 0) + 1
print(f'\nRegion distribution:')
for k, v in sorted(region_counts.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')

# Assignee summary
assignee_counts = {}
for r in records:
    for a in r['执行人']:
        name = a.get('name', '?')
        assignee_counts[name] = assignee_counts.get(name, 0) + 1
print(f'\nUnique assignees: {len(assignee_counts)}')
print(f'Tasks per assignee:')
for name, count in sorted(assignee_counts.items(), key=lambda x: -x[1])[:10]:
    print(f'  {name}: {count}')
print(f'  ...')

# Save tasks
output = {'records': records}
with open('/tmp/clean_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f'\nSaved to /tmp/clean_data.json ({len(json.dumps(output, ensure_ascii=False))} bytes)')

# ========== Fetch People Table ==========
print('\nFetching people table...')
people_table_id = 'tblZ7AiIKPFRZuiR'
cmd = [
    'lark-cli', 'base', '+record-list',
    '--base-token', BASE_TOKEN,
    '--table-id', people_table_id,
    '--offset', '0', '--limit', '200',
    '--as', 'user', '--format', 'json'
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    pdata = json.loads(result.stdout)
    prows = pdata['data']['data']
    pfields = pdata['data']['fields']
    pfield_to_idx = {name: i for i, name in enumerate(pfields)}
    name_idx = pfield_to_idx.get('name', pfield_to_idx.get('\u59d3\u540d', 0))
    dept_idx = pfield_to_idx.get('dept', pfield_to_idx.get('\u90e8\u95e8', 1))
    id_idx = pfield_to_idx.get('id', pfield_to_idx.get('\u4eba\u5458ID', 2))
    people = []
    for row in prows:
        # name is at index 2, inside objects array
        name = ''
        if id_idx < len(row) and isinstance(row[id_idx], list) and len(row[id_idx]) > 0:
            name = row[id_idx][0].get('name', '') or ''
            pid = row[id_idx][0].get('id', '') or ''
        else:
            pid = ''
        # dept is at index 1, inside array
        dept = ''
        if dept_idx < len(row) and isinstance(row[dept_idx], list) and len(row[dept_idx]) > 0:
            dept = row[dept_idx][0] or ''
        if name:
            people.append({'name': name, 'id': pid or '', 'dept': dept or ''})
    with open('/tmp/all_people.json', 'w', encoding='utf-8') as f:
        json.dump(people, f, ensure_ascii=False, indent=2)
    print(f'Fetched {len(people)} people -> /tmp/all_people.json')
else:
    print(f'  Error fetching people: {result.stderr[:200]}')
