import os
import sys
import subprocess
import shutil
import glob
import urllib.request

# ---------------------------------------------------------
#  Flutter x86 Patch & Rebuild Script (Python3)
#  Usage: python fix.py path\to\your.apk
# ---------------------------------------------------------

APKTOOL_URL = "https://github.com/iBotPeaches/Apktool/releases/download/v2.12.1/apktool_2.12.1.jar"
UBER_SIGNER_URL = "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar"


def download_if_missing(url, filename):
    """Download file if not present"""
    if not os.path.exists(filename):
        print(f"[+] Downloading {filename} ...")
        urllib.request.urlretrieve(url, filename)
        print(f"[+] Downloaded {filename}")
    return filename


def find_tool(pattern, url=None, default_name=None):
    """Find a tool jar in current directory, or download"""
    matches = glob.glob(pattern)
    if matches:
        return matches[0]
    if url and default_name:
        return download_if_missing(url, default_name)
    print(f"[ERROR] Could not find {pattern} and no download URL provided!")
    sys.exit(1)


def run_cmd(cmd, error_msg):
    """Run a shell command with error handling"""
    print(f"[+] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"[ERROR] {error_msg}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout


def main():
    if len(sys.argv) < 2:
        print("[ERROR] Please provide APK file path.")
        print("Example: python fix.py C:\\apps\\myapp.apk")
        sys.exit(1)

    apk_path = sys.argv[1]
    apk_name = os.path.splitext(os.path.basename(apk_path))[0]

    # Detect or download tools
    apktool = find_tool("apktool*.jar", APKTOOL_URL, "apktool.jar")
    uber_signer = find_tool("uber-apk-signer*.jar", UBER_SIGNER_URL, "uber-apk-signer.jar")

    # Step 1: Decompile
    src_dir = f"{apk_name}_src"
    print(f"[+] Decompiling APK: {apk_path}")
    run_cmd(["java", "-jar", apktool, "d", "-f", apk_path, "-o", src_dir],
            "Failed to decompile APK")

    # Step 2: Copy libflutter.so
    arm_lib = os.path.join(src_dir, "lib", "armeabi-v7a", "libflutter.so")
    x86_dir = os.path.join(src_dir, "lib", "x86")

    if not os.path.exists(arm_lib):
        print("[ERROR] libflutter.so not found in armeabi-v7a folder!")
        sys.exit(1)

    os.makedirs(x86_dir, exist_ok=True)
    shutil.copy2(arm_lib, os.path.join(x86_dir, "libflutter.so"))
    print("[+] Copied libflutter.so to x86")

    # Step 3: Build APK
    patched_apk = f"{apk_name}_patched.apk"
    print("[+] Rebuilding APK...")
    run_cmd(["java", "-jar", apktool, "b", src_dir, "-o", patched_apk],
            "Failed to rebuild APK")

    # Step 4: Reflutter
    print("[+] Refluttering APK...")
    try:
        run_cmd(["reflutter", patched_apk], "Reflutter failed")
        if os.path.exists(patched_apk):
            os.remove(patched_apk)
        os.rename("release.RE.apk", patched_apk)
    except FileNotFoundError:
        print("[WARNING] Reflutter not installed. Skipping this step.")

    # Step 5: Sign APK
    print("[+] Signing APK with Uber APK Signer...")
    run_cmd(["java", "-jar", uber_signer, "-a", patched_apk, "--overwrite"],
            "Failed to sign APK")

    # Step 6: Cleanup
    shutil.rmtree(src_dir, ignore_errors=True)

    print(f"\n[SUCCESS] Final signed APK: {apk_name}_patched-aligned-signed.apk")


if __name__ == "__main__":
    main()
