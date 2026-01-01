from __future__ import annotations

from dataclasses import dataclass
import io
import logging
from pathlib import Path
import zipfile

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import molviewspec as mvs
from starlette.requests import Request

LOGGER = logging.getLogger("molstar_webapp")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

ROOT = Path(__file__).resolve().parents[1]
TESTDATA_DIR = ROOT / "testdata"

app = FastAPI()
app.mount("/static", StaticFiles(directory=ROOT / "webapp" / "static"), name="static")
templates = Jinja2Templates(directory=ROOT / "webapp" / "templates")


@dataclass(frozen=True)
class TrajectoryEntry:
    traj_id: str
    label: str
    pdb_path: Path
    xtc_path: Path


def find_trajectory_pairs(testdata_dir: Path) -> list[TrajectoryEntry]:
    if not testdata_dir.exists():
        raise FileNotFoundError(f"Testdata directory not found: {testdata_dir}")
    pdb_suffix = ".trajectory_system.pdb"
    xtc_suffix = ".trajectory.xtc"
    pdb_map: dict[str, Path] = {}
    xtc_map: dict[str, Path] = {}
    for path in testdata_dir.iterdir():
        if path.name.endswith(pdb_suffix):
            traj_id = path.name[: -len(pdb_suffix)]
            pdb_map[traj_id] = path
        elif path.name.endswith(xtc_suffix):
            traj_id = path.name[: -len(xtc_suffix)]
            xtc_map[traj_id] = path
    entries: list[TrajectoryEntry] = []
    for traj_id in sorted(set(pdb_map) & set(xtc_map)):
        label = traj_id.replace("_", " ")
        entries.append(
            TrajectoryEntry(
                traj_id=traj_id,
                label=label,
                pdb_path=pdb_map[traj_id],
                xtc_path=xtc_map[traj_id],
            )
        )
    return entries


def build_mvsx_bytes(pdb_path: Path, xtc_path: Path) -> bytes:
    LOGGER.info("Building MVSX for %s", pdb_path.name)
    builder = mvs.create_builder()
    builder.download(url="trajectory.xtc").parse(format="xtc").coordinates(ref="traj")
    structure = (
        builder.download(url="trajectory.pdb")
        .parse(format="pdb")
        .model_structure(coordinates_ref="traj")
    )
    (
        structure.component(selector={"label_comp_id": "UNK"})
        .representation(type="ball_and_stick", size_factor=0.7, ignore_hydrogens=True)
        .color(color="blue")
    )
    structure.component(selector="all").representation().color(color="white")
    mvsj = builder.get_state().model_dump_json(exclude_none=True, indent=2)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("index.mvsj", mvsj)
        archive.writestr("trajectory.pdb", pdb_path.read_bytes())
        archive.writestr("trajectory.xtc", xtc_path.read_bytes())
    return buffer.getvalue()


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/trajectories")
def list_trajectories() -> list[dict[str, str]]:
    LOGGER.info("Scanning trajectories in %s", TESTDATA_DIR)
    try:
        entries = find_trajectory_pairs(TESTDATA_DIR)
    except FileNotFoundError as exc:
        LOGGER.error("Testdata folder missing: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return [{"id": entry.traj_id, "label": entry.label} for entry in entries]


@app.get("/api/mvsx/{traj_id}")
def get_mvsx(traj_id: str) -> Response:
    try:
        entries = find_trajectory_pairs(TESTDATA_DIR)
    except FileNotFoundError as exc:
        LOGGER.error("Testdata folder missing: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    entry = next((item for item in entries if item.traj_id == traj_id), None)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Trajectory not found: {traj_id}")
    try:
        payload = build_mvsx_bytes(entry.pdb_path, entry.xtc_path)
    except Exception as exc:
        LOGGER.error("Failed to build MVSX for %s: %s", traj_id, exc)
        raise HTTPException(status_code=500, detail="Failed to build MVSX") from exc
    return Response(payload, media_type="application/octet-stream")
