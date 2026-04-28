import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import sys

from bambu_ftp import make_ftp, done

ip          = sys.argv[1]
access_code = sys.argv[2]
remote_path = sys.argv[3]

try:
    ftp = make_ftp(ip, access_code)
    ftp.delete(remote_path)
    ftp.quit_safe()
    done()
    print("deleted ok")

except Exception as e:
    done()
    print(f"error: {e}")
