"""
Microstrip Patch Antenna Calculator — API Integration Tests

Tests the REST endpoints via FastAPI TestClient to verify:
- Correct HTTP status codes
- Response schema compliance
- Error handling for invalid inputs
- Health check endpoint
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# =============================================================================
# Health Check
# =============================================================================


class TestHealthEndpoint:
    """Tests for GET /api/v1/patch-antenna/health"""

    def test_health_returns_200(self):
        response = client.get("/api/v1/patch-antenna/health")
        assert response.status_code == 200

    def test_health_response_schema(self):
        response = client.get("/api/v1/patch-antenna/health")
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
        assert "version" in data


# =============================================================================
# Calculate Endpoint — Success Cases
# =============================================================================


class TestCalculateEndpoint_Success:
    """Tests for POST /api/v1/patch-antenna/calculate — valid inputs."""

    def test_basic_calculation_returns_200(self):
        """Standard FR4 2.4 GHz calculation should succeed."""
        payload = {
            "frequency": 2.4,
            "frequency_unit": "GHz",
            "dielectric_constant": 4.4,
            "substrate_height": 1.6,
            "substrate_height_unit": "mm",
        }
        response = client.post("/api/v1/patch-antenna/calculate", json=payload)
        assert response.status_code == 200

    def test_response_has_required_fields(self):
        """Response must contain all required top-level fields."""
        payload = {
            "frequency": 2.4,
            "frequency_unit": "GHz",
            "dielectric_constant": 4.4,
            "substrate_height": 1.6,
            "substrate_height_unit": "mm",
        }
        response = client.post("/api/v1/patch-antenna/calculate", json=payload)
        data = response.json()

        assert "input_echo" in data
        assert "result" in data
        assert "warnings" in data
        assert "model_info" in data

    def test_input_echo_values(self):
        """Input echo should reflect converted SI values."""
        payload = {
            "frequency": 2.4,
            "frequency_unit": "GHz",
            "dielectric_constant": 4.4,
            "substrate_height": 1.6,
            "substrate_height_unit": "mm",
        }
        response = client.post("/api/v1/patch-antenna/calculate", json=payload)
        data = response.json()

        assert data["input_echo"]["frequency_hz"] == 2.4e9
        assert data["input_echo"]["dielectric_constant"] == 4.4
        assert abs(data["input_echo"]["substrate_height_m"] - 0.0016) < 1e-10

    def test_result_positive_values(self):
        """All dimension results must be positive."""
        payload = {
            "frequency": 2.4,
            "frequency_unit": "GHz",
            "dielectric_constant": 4.4,
            "substrate_height": 1.6,
            "substrate_height_unit": "mm",
        }
        response = client.post("/api/v1/patch-antenna/calculate", json=payload)
        result = response.json()["result"]

        assert result["width_mm"] > 0
        assert result["length_mm"] > 0
        assert result["effective_dielectric_constant"] > 0
        assert result["length_extension_mm"] > 0
        assert result["effective_length_mm"] > 0
        assert result["free_space_wavelength_mm"] > 0
        assert result["guided_wavelength_mm"] > 0

    def test_advanced_disabled_returns_null(self):
        """Advanced result should be null when not enabled."""
        payload = {
            "frequency": 2.4,
            "frequency_unit": "GHz",
            "dielectric_constant": 4.4,
            "substrate_height": 1.6,
            "substrate_height_unit": "mm",
        }
        response = client.post("/api/v1/patch-antenna/calculate", json=payload)
        assert response.json()["advanced_result"] is None

    def test_advanced_enabled_returns_results(self):
        """Advanced result should be populated when enabled."""
        payload = {
            "frequency": 2.4,
            "frequency_unit": "GHz",
            "dielectric_constant": 4.4,
            "substrate_height": 1.6,
            "substrate_height_unit": "mm",
            "advanced": {
                "enabled": True,
                "feed_impedance": 50,
                "use_inset_feed": True,
            },
        }
        response = client.post("/api/v1/patch-antenna/calculate", json=payload)
        data = response.json()

        assert data["advanced_result"] is not None
        assert data["advanced_result"]["edge_resistance_ohm"] > 0
        assert data["advanced_result"]["feed_line_width_mm"] > 0
        assert data["advanced_result"]["bandwidth_percent"] > 0

    def test_different_frequency_units(self):
        """All frequency units should work correctly."""
        for unit, value in [("Hz", 2.4e9), ("kHz", 2.4e6), ("MHz", 2400), ("GHz", 2.4)]:
            payload = {
                "frequency": value,
                "frequency_unit": unit,
                "dielectric_constant": 4.4,
                "substrate_height": 1.6,
                "substrate_height_unit": "mm",
            }
            response = client.post("/api/v1/patch-antenna/calculate", json=payload)
            assert response.status_code == 200, f"Failed for unit {unit}"

    def test_different_height_units(self):
        """All height units should work correctly."""
        # 1.6 mm in various units
        for unit, value in [
            ("mm", 1.6),
            ("cm", 0.16),
            ("m", 0.0016),
            ("inch", 0.062992),
            ("mil", 62.992),
            ("um", 1600),
        ]:
            payload = {
                "frequency": 2.4,
                "frequency_unit": "GHz",
                "dielectric_constant": 4.4,
                "substrate_height": value,
                "substrate_height_unit": unit,
            }
            response = client.post("/api/v1/patch-antenna/calculate", json=payload)
            assert response.status_code == 200, f"Failed for unit {unit}"


# =============================================================================
# Calculate Endpoint — Validation Error Cases
# =============================================================================


class TestCalculateEndpoint_Errors:
    """Tests for POST /api/v1/patch-antenna/calculate — invalid inputs."""

    def test_epsilon_r_equals_1_returns_422(self):
        """εr = 1 should be rejected with 422."""
        payload = {
            "frequency": 2.4,
            "frequency_unit": "GHz",
            "dielectric_constant": 1.0,
            "substrate_height": 1.6,
            "substrate_height_unit": "mm",
        }
        response = client.post("/api/v1/patch-antenna/calculate", json=payload)
        assert response.status_code == 422

    def test_epsilon_r_below_1_returns_422(self):
        """εr < 1 should be rejected with 422."""
        payload = {
            "frequency": 2.4,
            "frequency_unit": "GHz",
            "dielectric_constant": 0.5,
            "substrate_height": 1.6,
            "substrate_height_unit": "mm",
        }
        response = client.post("/api/v1/patch-antenna/calculate", json=payload)
        assert response.status_code == 422

    def test_frequency_zero_returns_422(self):
        """f = 0 should be rejected with 422."""
        payload = {
            "frequency": 0,
            "frequency_unit": "GHz",
            "dielectric_constant": 4.4,
            "substrate_height": 1.6,
            "substrate_height_unit": "mm",
        }
        response = client.post("/api/v1/patch-antenna/calculate", json=payload)
        assert response.status_code == 422

    def test_frequency_negative_returns_422(self):
        """f < 0 should be rejected with 422."""
        payload = {
            "frequency": -1,
            "frequency_unit": "GHz",
            "dielectric_constant": 4.4,
            "substrate_height": 1.6,
            "substrate_height_unit": "mm",
        }
        response = client.post("/api/v1/patch-antenna/calculate", json=payload)
        assert response.status_code == 422

    def test_height_zero_returns_422(self):
        """h = 0 should be rejected with 422."""
        payload = {
            "frequency": 2.4,
            "frequency_unit": "GHz",
            "dielectric_constant": 4.4,
            "substrate_height": 0,
            "substrate_height_unit": "mm",
        }
        response = client.post("/api/v1/patch-antenna/calculate", json=payload)
        assert response.status_code == 422

    def test_invalid_frequency_unit_returns_422(self):
        """Invalid frequency unit should be rejected."""
        payload = {
            "frequency": 2.4,
            "frequency_unit": "THz",
            "dielectric_constant": 4.4,
            "substrate_height": 1.6,
            "substrate_height_unit": "mm",
        }
        response = client.post("/api/v1/patch-antenna/calculate", json=payload)
        assert response.status_code == 422

    def test_missing_required_field_returns_422(self):
        """Missing frequency should be rejected."""
        payload = {
            "dielectric_constant": 4.4,
            "substrate_height": 1.6,
            "substrate_height_unit": "mm",
        }
        response = client.post("/api/v1/patch-antenna/calculate", json=payload)
        assert response.status_code == 422
