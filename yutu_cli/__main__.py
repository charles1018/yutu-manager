#!/usr/bin/env python3
"""Yutu Manager 入口點 - 支援 python -m yutu_cli 執行"""

import click

from yutu_cli import __version__
from yutu_cli.app import run_interactive


@click.command()
@click.version_option(version=__version__, prog_name="yutu-manager")
@click.option("--non-interactive", "-n", is_flag=True, help="非互動模式（用於腳本）")
def main(non_interactive: bool) -> None:
    """🎬 Yutu Manager - 互動式 YouTube 頻道管理工具
    
    透過友善的選單介面管理您的 YouTube 頻道，包括播放清單、影片、留言等功能。
    """
    if non_interactive:
        click.echo("非互動模式尚未實作")
        return
    
    run_interactive()


if __name__ == "__main__":
    main()
