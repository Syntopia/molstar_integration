# MolStar Webapp

Simple FastAPI app for selecting trajectories from `testdata/` and viewing them in Mol*.

## Run

Use the `pdblifter` environment:

```
python -m uvicorn webapp.app:app --reload --port 8000
```

Then open `http://localhost:8000`.
