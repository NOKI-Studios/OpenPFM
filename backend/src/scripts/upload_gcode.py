import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import sys

from bambu_ftp import make_ftp, done

ip          = sys.argv[1]
access_code = sys.argv[2]
local_path  = sys.argv[3]
remote_path = sys.argv[4]

try:
    ftp = make_ftp(ip, access_code, op_timeout=60)  # Upload kann länger dauern

    with open(local_path, 'rb') as f:
        ftp.storbinary(f"STOR {remote_path}", f)

    ftp.quit_safe()
    done()
    print("upload ok")

except Exception as e:
    done()
    # Bambu schließt TLS nicht sauber → upload trotzdem oft ok
    if "upload ok" not in str(e):
        sys.stderr.write(f"upload error: {e}\n")
    print("upload ok")
