#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def _force_utf8_stdio():
    """Windows consoles default to cp1252 — force UTF-8 so '₹' and friends
    never crash email/report printing (Django console email backend)."""
    if sys.platform == "win32":
        import io

        for name in ("stdout", "stderr"):
            stream = getattr(sys, name)
            if (
                stream is not None
                and hasattr(stream, "buffer")
                and getattr(stream, "encoding", "").lower() not in ("utf-8", "utf8")
            ):
                setattr(
                    sys,
                    name,
                    io.TextIOWrapper(
                        stream.buffer,
                        encoding="utf-8",
                        errors="replace",
                        line_buffering=True,
                    ),
                )


def main():
    """Run administrative tasks."""
    _force_utf8_stdio()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
