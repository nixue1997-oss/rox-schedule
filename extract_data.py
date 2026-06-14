#!/usr/bin/env python3
"""Fetch records from Feishu using view, then merge parent/JIRA fields from full table."""
import json, os, subprocess, sys

BASE_TOKEN = os.environ.get('BASE_TOKEN', 'ByUibD4rxaBmHlswtT5cz3PsnNf')
TABLE_ID = 'tblCQ1JwLliZON3a'
VIEW_ID = 'vewpI8lyYw'

def fetch_page(table_id, offset, limit=200, view_id=None):
    cmd = [
        'lark-cli', 'base', '+record-list',
        '--base-token', BASE_TOKEN,
        '--table-id', table_id,
        '--offset', str(offset), '--limit', str(limit),
        '--as', 'user', '--format', 'json'
    ]
    if view_id:
        cmd.extend(['--view-id', view_id])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'  Error at offset {offset}: {result.stderr[:200]}', file=sys.stderr)
        return None
    return json.loads(result.stdout)

def fetch_all(table_id, view_id=None):
    all_rows, all_record_ids = [], []
    fields, field_ids = None, None
    offset, page = 0, 1
    while True:
        print(f'  Page {page} (offset={offset})...')
        data = fetch_page(table_id, offset, 200, view_id)
        if data is None: break
        rows = data['data']['data']
        rids = data['data']['record_id_list']
        if page == 1:
            fields = data['data']['fields']
            field_ids = data['data']['field_id_list']
        all_rows.extend(rows)
        all_record_ids.extend(rids)
        has_more = data['data'].get('has_more', False)
        print(f'    Got {len(rows)} recs (total={len(all_rows)}, has_more={has_more})')
        if not has_more: break
        offset += len(rows)
        page += 1
    return {'fields': fields, 'field_ids': field_ids, 'rows': all_rows, 'record_ids': all_record_ids}

# ========== Phase 1: Fetch from view (279 records, 37 fields) ==========
print('Phase 1: Fetching from view vewpI8lyYw...')
view_data = fetch_all(TABLE_ID, VIEW_ID)
print(f'  Total: {len(view_data["rows"])} records, {len(view_data["fields"])} fields')

# ========== Phase 2: Fetch full table extra fields ==========
print('\nPhase 2: Fetching full table for extra fields (parent, JIRA)...')
full_data = fetch_all(TABLE_ID)
print(f'  Total: {len(full_data["rows"])} full records, {len(full_data["fields"])} fields')

# Build extra field map by record_id
extra_fields = {}
full_fidx = {name: i for i, name in enumerate(full_data['fields'])}

# Only keep records that are in our view (by record_id)
view_rid_set = set(view_data['record_ids'])
print(f'  View record IDs: {len(view_rid_set)}')

for ri, row in enumerate(full_data['rows']):
    rid = full_data['record_ids'][ri]
    if rid not in view_rid_set:
        continue
    def gf(name):
        idx = full_fidx.get(name)
        if idx is None or idx >= len(row): return None
        return row[idx]
    
    parent_raw = gf('\u672c\u8868--\u7236\u8bb0\u5f55')
    parent_task = parent_raw[0]['id'] if isinstance(parent_raw, list) and len(parent_raw) > 0 else ''
    
    jira_url_raw = gf('JIRA\u5355')
    jira_url = jira_url_raw if isinstance(jira_url_raw, str) else ''
    
    jira_key_raw = gf('Jira Key')
    jira_key = jira_key_raw if isinstance(jira_key_raw, str) else (jira_key_raw[0] if isinstance(jira_key_raw, list) and len(jira_key_raw) > 0 else '')
    
    ext_ver_raw = gf('\u5bf9\u5916\u7248\u672c')
    ext_version = ext_ver_raw[0]['id'] if isinstance(ext_ver_raw, list) and len(ext_ver_raw) > 0 else ''
    
    extra_fields[rid] = {
        'parentTask': parent_task,
        'jiraUrl': jira_url,
        'jiraKey': jira_key,
        'extVersion': ext_version,
    }

print(f'  Merged extra fields for {len(extra_fields)} records')

# ========== Phase 3: Map view records with merged fields ==========
view_fidx = {name: i for i, name in enumerate(view_data['fields'])}

records = []
for ri, row in enumerate(view_data['rows']):
    rid = view_data['record_ids'][ri]
    def gf(name):
        idx = view_fidx.get(name)
        if idx is None or idx >= len(row): return None
        return row[idx]
    
    title = gf('\u5de5\u4f5c\u5185\u5bb9') or ''
    
    progress_raw = gf('\u8fdb\u5c55')
    progress = progress_raw[0] if isinstance(progress_raw, list) and progress_raw else ''
    
    test_date = gf('\u6700\u665a\u8f6c\u6d4b\u65f6\u95f4') or ''
    freeze_date = gf('\u5c01\u677f\u65f6\u95f4') or ''
    version_date = gf('\u7248\u66f4\u65f6\u95f4') or ''
    online_date = gf('\u4e0a\u7ebf\u65f6\u95f4\uff08\u529f\u80fdowner\u7ef4\u62a4\uff09') or ''
    start_date = gf('\u542f\u52a8\u65e5\u671f') or ''
    end_date = gf('\u4efb\u52a1\u7ed3\u675f') or ''
    
    assignee_raw = gf('\u6267\u884c\u4eba')
    assignee = assignee_raw if isinstance(assignee_raw, list) else []
    
    region = gf('\u5730\u533a')
    if region is None:
        region = gf('\u5bf9\u5916\u7248\u672c')
    if not isinstance(region, list):
        region = []
    
    extra = extra_fields.get(rid, {})
    
    records.append({
        '\u5de5\u4f5c\u5185\u5bb9': title,
        '\u8fdb\u5c55': [progress],
        '\u6700\u665a\u8f6c\u6d4b\u65f6\u95f4': test_date,
        '\u5c01\u677f\u65f6\u95f4': freeze_date,
        '\u7248\u66f4\u65f6\u95f4': version_date,
        '\u4e0a\u7ebf\u65f6\u95f4\uff08\u529f\u80fdowner\u7ef4\u62a4\uff09': online_date,
        '\u542f\u52a8\u65e5\u671f': start_date,
        '\u4efb\u52a1\u7ed3\u675f': end_date,
        '\u6267\u884c\u4eba': assignee,
        '\u5730\u533a': region,
        '\u672c\u8868--\u7236\u8bb0\u5f55': extra.get('parentTask', ''),
        'JIRA\u5355': extra.get('jiraUrl', ''),
        'Jira Key': extra.get('jiraKey', ''),
        '\u5bf9\u5916\u7248\u672c': extra.get('extVersion', ''),
        '_id': rid,
    })

print(f'\nMapped {len(records)} records total')

parent_count = sum(1 for r in records if r.get('\u672c\u8868--\u7236\u8bb0\u5f55'))
jira_count = sum(1 for r in records if r.get('JIRA\u5355'))
print(f'Records with parent: {parent_count}')
print(f'Records with JIRA: {jira_count}')
ext_cnt = sum(1 for r in records if r.get('\u5bf9\u5916\u7248\u672c'))
print(f'Records with extVersion: {ext_cnt}')

output = {'records': records}
with open('/tmp/clean_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f'\nSaved to /tmp/clean_data.json ({len(json.dumps(output, ensure_ascii=False))} bytes)')

# ========== Fetch People Table ==========
print('\nFetching people table...')
ppl_data = fetch_all('tblZ7AiIKPFRZuiR')
prows = ppl_data['rows']
people = []
for row in prows:
    name = ''
    if len(row) > 2 and isinstance(row[2], list) and len(row[2]) > 0:
        name = row[2][0].get('name', '') or ''
        pid = row[2][0].get('id', '') or ''
    else:
        pid = ''
    dept = ''
    if len(row) > 1 and isinstance(row[1], list) and len(row[1]) > 0:
        dept = row[1][0] or ''
    if name:
        people.append({'name': name, 'id': pid or '', 'dept': dept or ''})
with open('/tmp/all_people.json', 'w', encoding='utf-8') as f:
    json.dump(people, f, ensure_ascii=False, indent=2)
print(f'Fetched {len(people)} people -> /tmp/all_people.json')
