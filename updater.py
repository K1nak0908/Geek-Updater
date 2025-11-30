import requests
import os
import shutil
import sys
from bs4 import BeautifulSoup
import subprocess

current_dir = os.getcwd()
geek_exe = os.path.join(current_dir, "geek.exe")
zip_path = os.path.join(current_dir, "geek.zip")
extract_dir = os.path.join(current_dir, "geek")
version_file = os.path.join(current_dir, "CurrentVersion.txt")


def get_latest_version():
    try:
        res = requests.get("https://geekuninstaller.com/download", timeout=30)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        version_tags = soup.find_all("b")
        versions = [v.text.strip() for v in version_tags if v.text.strip()]
        return versions[0] if versions else None
    except Exception as e:
        print(f"[-] Failed to fetch version info: {e}")
        sys.exit(1)


def download_geek():
    try:
        if os.path.isfile(geek_exe):
            os.remove(geek_exe)

        print("[+] Downloading...")
        with requests.get("https://geekuninstaller.com/geek.zip", timeout=30, stream=True) as geek:
            geek.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in geek.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("[+] Downloaded!")

        print("[+] Extracting...")
        shutil.unpack_archive(zip_path, extract_dir)
        print("[+] Extracted!")

        print("[+] Copying geek.exe...")
        shutil.copy2(os.path.join(extract_dir, "geek.exe"), geek_exe)
        print("[+] Copied geek.exe!")

    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)
    finally:
        if os.path.isfile(zip_path):
            os.remove(zip_path)
        if os.path.isdir(extract_dir):
            shutil.rmtree(extract_dir)


def main():
    latest = get_latest_version()
    if not latest:
        print("[-] No version info found")
        sys.exit(1)

    current_ver = None
    if os.path.isfile(version_file):
        with open(version_file) as f:
            current_ver = f.read().strip()

    if current_ver != latest or not os.path.isfile(geek_exe):
        download_geek()
        with open(version_file, "w") as f:
            f.write(latest)
        print(f"[+] Updated to version {latest}")
    else:
        print(f"[+] Already up-to-date ({latest})")

    print("[+] Launching geek.exe...")
    subprocess.Popen([geek_exe], shell=True)

    sys.exit(0)


if __name__ == "__main__":
    main()
