#!/usr/bin/env python3
"""Fetch records from Feishu view (all 37 fields) + full table extra fields (parent, Jira Key)."""
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

# ========== Phase 1: Fetch from view (37 fields) ==========
print('Phase 1: Fetching from view vewpI8lyYw...')
view_data = fetch_all(TABLE_ID, VIEW_ID)
print(f'  Total: {len(view_data["rows"])} records, {len(view_data["fields"])} fields')

# ========== Phase 2: Fetch full table for extra fields (parent, Jira Key) ==========
print('\nPhase 2: Fetching full table for extra fields (parent, Jira Key)...')
full_data = fetch_all(TABLE_ID)
print(f'  Total: {len(full_data["rows"])} full records, {len(full_data["fields"])} fields')

# Build extra field map by record_id
full_fidx = {name: i for i, name in enumerate(full_data['fields'])}
view_rid_set = set(view_data['record_ids'])

extra_fields = {}
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
    
    jira_key_raw = gf('Jira Key')
    jira_key = jira_key_raw if isinstance(jira_key_raw, str) else (jira_key_raw[0] if isinstance(jira_key_raw, list) and len(jira_key_raw) > 0 else '')
    
    extra_fields[rid] = {
        'parentTask': parent_task,
        'jiraKey': jira_key,
    }

print(f'  Merged extra fields for {len(extra_fields)} records')

# ========== Phase 3: Map view records with all fields ==========
view_fidx = {name: i for i, name in enumerate(view_data['fields'])}

def get_val(row, name, fidx):
    """Get value from row by field name, with proper type handling."""
    idx = fidx.get(name)
    if idx is None or idx >= len(row):
        return None
    return row[idx]

def safe_select(val):
    """Extract select value: returns list of strings or empty list."""
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        return [val]
    return []

def safe_user(val):
    """Extract user value: returns list of {id, name} or empty list."""
    if isinstance(val, list):
        return val
    return []

def safe_link(val):
    """Extract link value: returns first id string or empty string."""
    if isinstance(val, list) and len(val) > 0:
        return val[0].get('id', '') if isinstance(val[0], dict) else ''
    return ''

def safe_str(val):
    """Extract string value."""
    if val is None:
        return ''
    if isinstance(val, str):
        return val
    return str(val)

def safe_date(val):
    """Extract date value."""
    if val is None:
        return ''
    if isinstance(val, str):
        return val
    return str(val)

records = []
for ri, row in enumerate(view_data['rows']):
    rid = view_data['record_ids'][ri]
    v = lambda name: get_val(row, name, view_fidx)
    extra = extra_fields.get(rid, {})
    
    records.append({
        # Core fields
        '\u5de5\u4f5c\u5185\u5bb9': safe_str(v('\u5de5\u4f5c\u5185\u5bb9')),
        '\u4efb\u52a1\u540d\u79f0': safe_str(v('\u4efb\u52a1\u540d\u79f0')),
        '\u4efb\u52a1\u63cf\u8ff0': safe_str(v('\u4efb\u52a1\u63cf\u8ff0')),
        '\u8fdb\u5c55': safe_select(v('\u8fdb\u5c55')),
        '\u5f00\u53d1\u7c7b\u522b': safe_select(v('\u5f00\u53d1\u7c7b\u522b')),
        '\u4f18\u5148\u7ea7': safe_select(v('\u4f18\u5148\u7ea7')),
        '\u6708\u4efd': safe_select(v('\u6708\u4efd')),
        '\u5730\u533a': safe_select(v('\u5730\u533a')),
        '\u7248\u672c\u670d': safe_str(v('\u7248\u672c\u670d')),
        
        # People
        '\u6267\u884c\u4eba': safe_user(v('\u6267\u884c\u4eba')),
        'owner': safe_str(v('owner')),
        'QA': safe_user(v('QA')),
        '\u6700\u540e\u66f4\u65b0\u4eba': safe_user(v('\u6700\u540e\u66f4\u65b0\u4eba')),
        
        # Dates
        '\u542f\u52a8\u65e5\u671f': safe_date(v('\u542f\u52a8\u65e5\u671f')),
        '\u4efb\u52a1\u7ed3\u675f': safe_date(v('\u4efb\u52a1\u7ed3\u675f')),
        '\u6700\u665a\u8f6c\u6d4b\u65f6\u95f4': safe_date(v('\u6700\u665a\u8f6c\u6d4b\u65f6\u95f4')),
        '\u5c01\u677f\u65f6\u95f4': safe_date(v('\u5c01\u677f\u65f6\u95f4')),
        '\u5c01\u5305\u65f6\u95f4': safe_date(v('\u5c01\u5305\u65f6\u95f4')),
        '\u7248\u66f4\u65f6\u95f4': safe_date(v('\u7248\u66f4\u65f6\u95f4')),
        '\u4e0a\u7ebf\u65f6\u95f4\uff08\u529f\u80fdowner\u7ef4\u62a4\uff09': safe_date(v('\u4e0a\u7ebf\u65f6\u95f4\uff08\u529f\u80fdowner\u7ef4\u62a4\uff09')),
        '\u4e09\u65b9\u65f6\u95f4': safe_date(v('\u4e09\u65b9\u65f6\u95f4')),
        '\u672c\u5730\u5316\u5f00\u59cb': safe_date(v('\u672c\u5730\u5316\u5f00\u59cb')),
        '\u7ffb\u8bd1\u5bfc\u5165': safe_date(v('\u7ffb\u8bd1\u5bfc\u5165')),
        '\u672c\u5730\u5316\u8fd4\u56de': safe_date(v('\u672c\u5730\u5316\u8fd4\u56de')),
        '\u7f8e\u672f\u5b57\u5165\u7248': safe_date(v('\u7f8e\u672f\u5b57\u5165\u7248')),
        '\u7f8e\u672f\u5b57\u6700\u665a\u63d0\u9700\u65f6\u95f4': safe_date(v('\u7f8e\u672f\u5b57\u6700\u665a\u63d0\u9700\u65f6\u95f4')),
        '\u6700\u540e\u66f4\u65b0\u65f6\u95f4': safe_date(v('\u6700\u540e\u66f4\u65b0\u65f6\u95f4')),
        
        # Art & Localization
        '\u7f8e\u672f\u5b57': safe_select(v('\u7f8e\u672f\u5b57')),
        '\u8fd4\u56de\u72b6\u6001': safe_select(v('\u8fd4\u56de\u72b6\u6001')),
        '\u5bfc\u5165\u72b6\u6001': safe_select(v('\u5bfc\u5165\u72b6\u6001')),
        
        # Jira
        'JIRA\u5355': safe_str(v('JIRA\u5355')),
        'Jira \u72b6\u6001': safe_select(v('Jira \u72b6\u6001')),
        'Jira \u9879\u76ee Key': safe_select(v('Jira \u9879\u76ee Key')),
        'Jira \u4efb\u52a1\u7c7b\u578b': safe_str(v('Jira \u4efb\u52a1\u7c7b\u578b')),
        'Jira Key': extra.get('jiraKey', ''),
        '\u5b50\u4efb\u52a1\u521b\u5efa\u7ed3\u679c': safe_str(v('\u5b50\u4efb\u52a1\u521b\u5efa\u7ed3\u679c')),
        
        # Relations
        '\u5bf9\u5916\u7248\u672c': safe_link(v('\u5bf9\u5916\u7248\u672c')),
        '\u672c\u8868--\u7236\u8bb0\u5f55': extra.get('parentTask', ''),
        
        # Attachments
        '\u76f8\u5173\u9644\u4ef6': v('\u76f8\u5173\u9644\u4ef6') if v('\u76f8\u5173\u9644\u4ef6') else [],
        
        # ID
        '_id': rid,
    })

print(f'\nMapped {len(records)} records total')

# Stats
stats = {}
for r in records:
    for k, v in r.items():
        if k.startswith('_') or v == '' or v == []:
            continue
        stats[k] = stats.get(k, 0) + 1

print('\nField coverage:')
for k in sorted(stats.keys()):
    print(f'  {k}: {stats[k]}/{len(records)}')

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