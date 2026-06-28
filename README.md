# PatchCalc — Microstrip Patch Antenna Calculator

A full-stack web application for calculating the physical dimensions (Width & Length) of rectangular microstrip patch antennas using the **Transmission Line Model** (Balanis, 4th Ed., Chapter 14).

## Features

### Core (MVP)
- **Patch Width (W) & Length (L)** calculation from frequency, εr, and substrate height
- **Intermediate values**: ε_eff, ΔL, L_eff, λ₀, λg
- **Ground plane recommendation** (L + 6h, W + 6h)
- **Model validity warnings** (εr range, h/λ₀ ratio)
- **Interactive SVG** patch antenna visualization with dimension lines
- **Material presets** (FR4, RT/duroid, Rogers, Alumina, Air/Foam) + custom εr
- **Unit support**: Hz/kHz/MHz/GHz for frequency; mm/cm/m/inch/mil/μm for length
- **Export**: Copy text, download CSV, shareable URL

### Advanced Mode
- Edge resistance (Rin) — cavity model approximation
- Inset feed depth (y₀) for impedance matching
- 50Ω microstrip feed line width (Hammerstad-Jensen synthesis)
- Bandwidth estimation (%) — industry rule of thumb
- Directivity estimation (dBi) — cavity model
- All clearly labeled as **"Approximate"**

## Tech Stack

| Layer    | Technology                              |
|----------|-----------------------------------------|
| Backend  | Python 3.11+ / FastAPI / Pydantic       |
| Frontend | React / Vite / TypeScript               |
| Testing  | pytest (backend) / TypeScript (frontend)|
| API Docs | Swagger UI (auto-generated at `/docs`)  |

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend API will be available at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Run Tests

```bash
cd backend
python -m pytest app/tests/ -v
```

## API Endpoint

### `POST /api/v1/patch-antenna/calculate`

**Request:**
```json
{
  "frequency": 2.4,
  "frequency_unit": "GHz",
  "dielectric_constant": 4.4,
  "substrate_height": 1.6,
  "substrate_height_unit": "mm",
  "advanced": {
    "enabled": false,
    "feed_impedance": 50,
    "use_inset_feed": false
  }
}
```

**Response:** Width, Length, ε_eff, ΔL, L_eff, λ₀, λg, ground plane dimensions, warnings, and model info.

### `GET /api/v1/patch-antenna/health`

Health check endpoint returning service status.

## Formulas Reference

All formulas follow the Transmission Line Model from:
- C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th Edition, Ch. 14
- E. O. Hammerstad, "Equations for Microstrip Circuit Design," 1975
- E. Hammerstad & Ø. Jensen, IEEE MTT-S, 1980

## Project Structure

```
antenna/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST endpoints
│   │   ├── core/            # Constants & unit conversions
│   │   ├── schemas/         # Pydantic request/response models
│   │   ├── services/        # Pure calculation functions
│   │   └── tests/           # pytest test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── api.ts           # API client
│   │   ├── types.ts         # TypeScript types (mirror Pydantic)
│   │   └── App.tsx          # Main application
│   └── package.json
└── README.md
```

## License

MIT
