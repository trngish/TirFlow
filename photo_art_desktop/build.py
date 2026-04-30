#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PhotoArt Desktop 一键打包脚本
"""
import os
import sys
import shutil
import subprocess


def main():
    print("=" * 50)
    print("  PhotoArt Desktop 打包脚本")
    print("=" * 50)
    print()

    # 切换到脚本所在目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("[1/3] 清理旧构建文件...")
    if os.path.exists("dist/PhotoArtDesktop"):
        shutil.rmtree("dist/PhotoArtDesktop")
    if os.path.exists("build/PhotoArtDesktop"):
        shutil.rmtree("build/PhotoArtDesktop")
    print("    完成")

    print("\n[2/3] 执行 PyInstaller 打包...")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "PhotoArtDesktop.spec", "-y"],
        capture_output=False
    )

    if result.returncode != 0:
        print("\n    打包失败！")
        sys.exit(1)

    print("\n[3/3] 完成！")
    print()
    print(f"打包完成！输出目录: {os.path.abspath('dist/PhotoArtDesktop')}")
    print()


if __name__ == "__main__":
    main()