import pytest
from amusement_park_ride_access import process_ride_admissions, inspect_safety_restraints

# Example test case:
def test_single_adult_family_ride():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "has_fast_lane": False,
            "patrons": [{"height_cm": 150, "health_warning": False, "is_child": False}]
        }
    ]
    result = process_ride_admissions(groups, 5.0)
    assert result["total_revenue"] == 10.0
    assert result["status"] == "COMPLETED"


def test_invalid_arguments():
    with pytest.raises(ValueError):
        process_ride_admissions("invalid_groups", 5.0)


def test_closed_ride():
    groups = [
        {
            "is_open": False,
            "ride_type": "family",
            "patrons": [{"height_cm": 150}]
        }
    ]
    result = process_ride_admissions(groups, 5.0)
    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_ADMISSIONS"


def test_water_ride_child_and_fast_lane():
    groups = [
        {
            "is_open": True,
            "ride_type": "water_ride",
            "has_fast_lane": True,
            "patrons": [{"height_cm": 130, "is_child": True}]
        }
    ]
    result = process_ride_admissions(groups, 7.5)
    # 18.0 * 0.60 + 7.5 = 10.8 + 7.5 = 18.3
    assert result["total_revenue"] == 18.3
    assert result["status"] == "COMPLETED"


def test_health_warnings_roller_coaster_and_water_ride():
    # Roller coaster health warning resets group_total and breaks loop
    rc_group = [
        {
            "is_open": True,
            "ride_type": "roller_coaster",
            "patrons": [
                {"height_cm": 160, "health_warning": False},
                {"height_cm": 160, "health_warning": True},
                {"height_cm": 160, "health_warning": False}
            ]
        }
    ]
    res_rc = process_ride_admissions(rc_group, 5.0)
    assert res_rc["total_revenue"] == 0.0
    assert res_rc["status"] == "ZERO_ADMISSIONS"

    # Non-roller coaster health warning adds 0.0 and continues
    water_group = [
        {
            "is_open": True,
            "ride_type": "water_ride",
            "patrons": [
                {"height_cm": 160, "health_warning": True},
                {"height_cm": 160, "health_warning": False}
            ]
        }
    ]
    res_water = process_ride_admissions(water_group, 5.0)
    assert res_water["total_revenue"] == 18.0
    assert res_water["status"] == "COMPLETED"


def test_height_checks_and_safety_audit():
    # Patrons with height <= 0 and height < 120
    # Also trigger rejected_patrons > 4 for SAFETY_AUDIT
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [
                {"height_cm": 0},
                {"height_cm": 100},
                {"height_cm": 110},
                {"height_cm": 115},
                {"height_cm": 119},
                {"height_cm": 150}
            ]
        }
    ]
    result = process_ride_admissions(groups, 0.0)
    assert result["status"] == "SAFETY_AUDIT"
    assert result["total_revenue"] == 10.0


def test_inspect_safety_restraints():
    # 2 consecutive unlatched (0, 0) -> EMERGENCY_LOCK
    assert inspect_safety_restraints([[0, 0]]) == "EMERGENCY_LOCK"
    # All latched (1) -> SAFE
    assert inspect_safety_restraints([[1, 1, 1]]) == "SAFE"
