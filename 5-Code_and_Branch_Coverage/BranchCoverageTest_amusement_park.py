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


def test_invalid_groups_or_pass_fee():
    with pytest.raises(ValueError):
        process_ride_admissions("not_a_list", 5.0)
    with pytest.raises(ValueError):
        process_ride_admissions([], -2.0)


def test_closed_ride_and_empty_groups():
    result_empty = process_ride_admissions([], 5.0)
    assert result_empty["total_revenue"] == 0.0
    assert result_empty["status"] == "ZERO_ADMISSIONS"

    groups = [
        {
            "is_open": False,
            "ride_type": "family",
            "patrons": [{"height_cm": 150}]
        }
    ]
    result_closed = process_ride_admissions(groups, 5.0)
    assert result_closed["total_revenue"] == 0.0
    assert result_closed["status"] == "ZERO_ADMISSIONS"


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
    # Roller coaster health warning aborts ride and zeroes out group revenue
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

    # Other ride types reject the individual patron but continue for others
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


def test_patron_height_rejections_and_safety_audit():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [
                {"height_cm": 0},
                {"height_cm": -10},
                {"height_cm": 105},
                {"height_cm": 110},
                {"height_cm": 115},
                {"height_cm": 150}
            ]
        }
    ]
    result = process_ride_admissions(groups, 0.0)
    assert result["status"] == "SAFETY_AUDIT"
    assert result["total_revenue"] == 10.0


def test_inspect_safety_restraints():
    # Consecutive unlatched sensors trigger emergency lock
    assert inspect_safety_restraints([[1, 0, 0, 1]]) == "EMERGENCY_LOCK"
    # Latched sensors result in safe state
    assert inspect_safety_restraints([[1, 1, 1]]) == "SAFE"
