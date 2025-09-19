#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess


APKTOOL = r"path\apktool.jar"
UBER_SIGNER = r"path\uber-apk-signer.jar"
REFLUTTER = "reflutter"  # Must be installed in PATH


def run_cmd(cmd, check=True):
    """Run a shell command and stream output."""
    print(f"[CMD] {' '.join(cmd)}")
    subprocess.run(cmd, check=check)


def main(apk_path):
    if not os.path.isfile(apk_path):
        print(f"[ERROR] APK not found: {apk_path}")
        sys.exit(1)

    apk_name = os.path.splitext(os.path.basename(apk_path))[0]
    src_dir = f"{apk_name}_src"
    patched_apk = f"{apk_name}_patched.apk"

    # Step 1: Decompile APK
    print(f"[+] Decompiling APK: {apk_path}")
    run_cmd(["java", "-jar", APKTOOL, "d", "-f", apk_path, "-o", src_dir])

    # Step 2: Copy libflutter.so
    arm_lib = os.path.join(src_dir, "lib", "armeabi-v7a", "libflutter.so")
    x86_dir = os.path.join(src_dir, "lib", "x86")

    if not os.path.isfile(arm_lib):
        print("[ERROR] libflutter.so not found in armeabi-v7a folder!")
        sys.exit(1)

    os.makedirs(x86_dir, exist_ok=True)
    shutil.copy2(arm_lib, os.path.join(x86_dir, "libflutter.so"))
    print("[+] Copied libflutter.so to x86 folder")


    # Step 3: Build APK
    print("[+] Rebuilding APK...")
    run_cmd(["java", "-jar", APKTOOL, "b", src_dir, "-o", patched_apk])

    # Step 4: Reflutter
    print("[+] Refluttering APK...")
    run_cmd([REFLUTTER, patched_apk])

    if os.path.exists(patched_apk):
        os.remove(patched_apk)

    if os.path.exists("release.RE.apk"):
        os.rename("release.RE.apk", patched_apk)
    else:
        print("[ERROR] reflutter did not produce release.RE.apk")
        sys.exit(1)
    print("[+] Cleaning up decompile folder...")
    shutil.rmtree(src_dir, ignore_errors=True)
    # Step 5: Sign APK
    print("[+] Signing APK with uber-apk-signer...")
    run_cmd(["java", "-jar", UBER_SIGNER, "-a", patched_apk, "--overwrite"])

    final_apk = f"{apk_name}_patched-aligned-signed.apk"
    print("\n[SUCCESS] Final signed APK:", final_apk)
    print("======================================================================")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[ERROR] Please provide APK file path.")
        print("Example: python3 fix.py /home/user/myapp.apk")
        sys.exit(1)

    main(sys.argv[1])
