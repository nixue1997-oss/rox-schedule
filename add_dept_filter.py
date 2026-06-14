#!/usr/bin/env python3
"""Add department filter to ROX schedule board HTML. Fixes: scope + ALL_PEOPLE lookup."""
import sys

def add_dept_filter(html):
    changes = 0

    # 1. Add department filter dropdown in the filter bar
    old_filter = '</div>\n    <div class="filter-group">\n      <label>\u641c\u7d22</label>'
    dept_filter = (
        '</div>\n'
        '    <div class="filter-group">\n'
        '      <label>\u90e8\u95e8</label>\n'
        '      <select id="filterDept" onchange="applyFilters()">\n'
        '        <option value="">\u5168\u90e8</option>\n'
        '      </select>\n'
        '    </div>\n'
        '    <div class="filter-group">\n'
        '      <label>\u641c\u7d22</label>'
    )
    if old_filter in html:
        html = html.replace(old_filter, dept_filter, 1)
        changes += 1
        print("✅ Step 1: filter dropdown added")
    else:
        print("❌ Step 1 failed")

    # 2. Add dept var declaration at top of getFilteredData(), alongside other vars
    # Remove the old bad var dept from inside DATA.filter first (step 3 handles replacement)
    old_bad_var = (
        "    var dept = document.getElementById('filterDept').value;\n"
        "    if (dept) {\n"
        "      if (!r.assignee || !r.assignee.some(function(p) { return p.dept === dept; })) return false;\n"
        "    }"
    )
    # Blank it out
    if old_bad_var in html:
        html = html.replace(old_bad_var, "", 1)
        changes += 1
        print("✅ Step 2: removed bad var dept from DATA.filter")
    else:
        print("❌ Step 2 failed")
        # Debug
        idx = html.find("var dept = document.getElementById")
        if idx >= 0:
            print(f"  Found at {idx}: {html[idx:idx+150]!r}")

    # 3. Insert corrected dept check into DATA.filter 
    # The dept check was blanked out, insert after the person else block
    old_person_else = (
        "    } else {\n"
        "      // When \"\u5168\u90e8\" is selected, show all (default behavior)\n"
        "    }"
    )
    corrected_dept_check = (
        "    } else {\n"
        "      // When \"\u5168\u90e8\" is selected, show all (default behavior)\n"
        "    }\n"
        "    if (dept) {\n"
        "      if (!r.assignee || !r.assignee.some(function(p) {\n"
        "        var pDept = '';\n"
        "        ALL_PEOPLE.some(function(pp) { if (pp.name === p.name) { pDept = pp.dept; return true; } return false; });\n"
        "        return pDept === dept;\n"
        "      })) return false;\n"
        "    }"
    )
    if old_person_else in html:
        html = html.replace(old_person_else, corrected_dept_check, 1)
        changes += 1
        print("✅ Step 3: corrected dept check (via ALL_PEOPLE lookup) added")
    else:
        print("❌ Step 3 failed")

    # 4. Add var dept at top of getFilteredData() alongside other var declarations
    old_vars = (
        "function getFilteredData() {\n"
        "  var region = document.getElementById('filterRegion').value;\n"
        "  var progress = document.getElementById('filterProgress').value;\n"
        "  var person = document.getElementById('filterPerson').value;\n"
        "  var search = document.getElementById('filterSearch').value.trim().toLowerCase();"
    )
    new_vars = (
        "function getFilteredData() {\n"
        "  var region = document.getElementById('filterRegion').value;\n"
        "  var progress = document.getElementById('filterProgress').value;\n"
        "  var person = document.getElementById('filterPerson').value;\n"
        "  var search = document.getElementById('filterSearch').value.trim().toLowerCase();\n"
        "  var dept = document.getElementById('filterDept').value;"
    )
    if old_vars in html:
        html = html.replace(old_vars, new_vars, 1)
        changes += 1
        print("✅ Step 4: var dept added at getFilteredData() top level")
    else:
        print("❌ Step 4 failed")

    # 5. Add dept check to adminTasks.filter
    old_admin_filter = (
        "if (person && t.assigneeName !== person) return false;\n"
        "    if (search && t.title.toLowerCase().indexOf(search) === -1) return false;"
    )
    new_admin_filter = (
        "if (person && t.assigneeName !== person) return false;\n"
        "    if (dept) {\n"
        "      var tDept = '';\n"
        "      ALL_PEOPLE.some(function(p) { if (p.name === t.assigneeName) { tDept = p.dept; return true; } return false; });\n"
        "      if (tDept !== dept) return false;\n"
        "    }\n"
        "    if (search && t.title.toLowerCase().indexOf(search) === -1) return false;"
    )
    if old_admin_filter in html:
        html = html.replace(old_admin_filter, new_admin_filter, 1)
        changes += 1
        print("✅ Step 5: admin filter dept check added")
    else:
        print("❌ Step 5 failed")
    
    # 6. Populate department filter in init()
    old_stats = "document.getElementById('headerInfo').textContent = DATA.length + ' \\u4e2a\\u4efb\\u52a1 | ' + allPeople.length + ' \\u4eba';"
    dept_pop = (
        "// Populate department filter\n"
        "  var selDept = document.getElementById('filterDept');\n"
        "  sortedDepts.forEach(function(dept) {\n"
        "    var opt = document.createElement('option');\n"
        "    opt.value = dept;\n"
        "    opt.textContent = dept;\n"
        "    selDept.appendChild(opt);\n"
        "  });\n"
        "\n"
        "  document.getElementById('headerInfo').textContent = DATA.length + ' \\u4e2a\\u4efb\\u52a1 | ' + allPeople.length + ' \\u4eba';"
    )
    if old_stats in html:
        html = html.replace(old_stats, dept_pop, 1)
        changes += 1
        print("✅ Step 5: init dept population added")
    else:
        print("❌ Step 5 failed")

    # 7. Update renderPersonView to respect dept filter
    idx = html.find("function renderPersonView()")
    if idx >= 0:
        sub = html[idx:]
        sd_idx = sub.find("var sortedDepts = Object.keys(deptMap).sort();")
        if sd_idx >= 0:
            old_line = "var sortedDepts = Object.keys(deptMap).sort();"
            new_block = (
                "  var filterDeptVal = document.getElementById('filterDept').value;\n"
                "  if (filterDeptVal) {\n"
                "    var filteredDeptMap = {};\n"
                "    filteredDeptMap[filterDeptVal] = deptMap[filterDeptVal] || [];\n"
                "    deptMap = filteredDeptMap;\n"
                "  }\n"
                "  var sortedDepts = Object.keys(deptMap).sort();\n"
            )
            actual_idx = idx + sd_idx
            html = html[:actual_idx] + new_block + html[actual_idx + len(old_line):]
            changes += 1
            print("✅ Step 6: renderPersonView dept filter added")
        else:
            print("❌ Step 6b sortedDepts not found")
    else:
        print("❌ Step 6a renderPersonView not found")

    print(f"\nTotal changes: {changes}")
    return html


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 add_dept_filter.py <input.html> [output.html]")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        html = f.read()

    result = add_dept_filter(html)

    output = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
    with open(output, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"Output: {len(result)} bytes -> {output}")