def _import_apt() -> None:
    try:
        import apt  # pyright: ignore[reportMissingImports]
    except ImportError:
        import sys
        if sys.platform == "linux" and '/usr/lib/python3/dist-packages' not in sys.path:
            sys.path.append('/usr/lib/python3/dist-packages')
