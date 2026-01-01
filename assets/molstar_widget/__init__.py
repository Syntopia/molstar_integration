"""AnyWidget wrapper for Mol* MolViewSpec loading."""

from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path
import zipfile
from typing import Any, Mapping

import anywidget
import traitlets


def _read_structure_bytes(value: Any) -> bytes:
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, (str, Path)):
        return Path(value).read_bytes()
    raise TypeError("Structure values must be bytes or paths.")


def _build_mvsx_base64(builder: Any, data: Mapping[str, Any]) -> str:
    if not hasattr(builder, "get_state"):
        raise TypeError("builder must expose get_state().")
    state = builder.get_state()
    if not hasattr(state, "model_dump_json"):
        raise TypeError("builder state must expose model_dump_json().")
    mvsj = state.model_dump_json(exclude_none=True, indent=2)
    if not isinstance(mvsj, str):
        raise TypeError("builder state did not return JSON string.")
    index_mvsj_bytes = mvsj.encode("utf-8")
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("index.mvsj", index_mvsj_bytes)
        for name, value in data.items():
            archive.writestr(name, _read_structure_bytes(value))
    return base64.b64encode(buffer.getvalue()).decode("ascii")


class MolStarWidget(anywidget.AnyWidget):
    """Mol* viewer that loads data via MolViewSpec."""

    _esm = Path(__file__).parent / "static" / "molstar_widget.js"
    _css = Path(__file__).parent / "static" / "molstar_widget.css"

    mvsx_base64 = traitlets.Unicode("").tag(sync=True)
    layout_show_controls = traitlets.Bool(False).tag(sync=True)
    layout_show_remote_state = traitlets.Bool(False).tag(sync=True)
    layout_show_log = traitlets.Bool(True).tag(sync=True)
    layout_is_expanded = traitlets.Bool(False).tag(sync=True)
    show_welcome_message = traitlets.Bool(False).tag(sync=True)
    viewport_show_expand = traitlets.Bool(True).tag(sync=True)
    viewport_show_controls = traitlets.Bool(True).tag(sync=True)
    collapse_left_panel = traitlets.Bool(True).tag(sync=True)
    frame_index = traitlets.Int(0).tag(sync=True)

    def __init__(
        self,
        *args: Any,
        builder: Any | None = None,
        data: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        if builder is not None:
            if data is None:
                data = {}
            if "mvsx_base64" in kwargs:
                raise ValueError("mvsx_base64 cannot be set when using builder input.")
            kwargs["mvsx_base64"] = _build_mvsx_base64(builder, data)
        super().__init__(*args, **kwargs)


__all__ = ["MolStarWidget"]
