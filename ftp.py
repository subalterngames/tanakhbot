from ftplib import FTP
import re
from pathlib import Path

"""
Upload mishnabot scripts to the server via FTP.
"""

ftp_files = ["run.py", "setup.py", "bot_secrets.txt", "tanakhbot/data/tanakh.json", "tanakhbot/bot.py"]
secrets = Path("secrets.txt").read_text()
ftp_uri = re.search(r"ftp=(.*)", secrets).group(1)
ftp = FTP(ftp_uri)
ftp_username = re.search(r"ftp_username=(.*)", secrets).group(1)
ftp_password = re.search(r"ftp_password=(.*)", secrets).group(1)
hostname = re.search(r"hostname=(.*)", secrets).group(1)
ftp.login(user=ftp_username, passwd=ftp_password)
ftp.cwd(hostname)
ftp.storbinary('STOR .htaccess', open('.htaccess', 'rb'))
ftp.cwd("public")
for f in ftp_files:
    ftp.storbinary('STOR ' + f, open(f, "rb"))
ftp.quit()
