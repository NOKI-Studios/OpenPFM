import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import sys
import json

from bambu_ftp import make_ftp, done

ip          = sys.argv[1]
access_code = sys.argv[2]
path        = sys.argv[3] if len(sys.argv) > 3 else '/'

try:
    ftp = make_ftp(ip, access_code)

    if path and path != '/':
        ftp.cwd(path)

    lines = []
    ftp.retrlines('LIST', lines.append)
    ftp.quit_safe()
    done()

    files = []
    for line in lines:
        parts = line.split(None, 8)
        if len(parts) < 9:
            continue
        perms        = parts[0]
        size         = int(parts[4]) if parts[4].isdigit() else 0
        month        = parts[5]
        day          = parts[6]
        year_or_time = parts[7]
        name         = parts[8]
        if name in ('.', '..'):
            continue
        files.append({
            'name': name,
            'type': 'dir' if perms.startswith('d') else 'file',
            'size': size,
            'date': f"{month} {day} {year_or_time}"
        })

    print(json.dumps({'files': files, 'path': path}))

except Exception as e:
    done()
    print(json.dumps({'error': str(e), 'files': []}))
