import math

def validate_height_and_fastpass(rider_spec):
    try:
        if not rider_spec or not isinstance(rider_spec, str):
            return "Invalid specification"
        parts = rider_spec.strip().split(':')
        if len(parts) != 2:
            return "Invalid specification"
        height_str, pass_str = parts
        height = int(height_str.strip())
        pass_map = {"YES": True, "NO": False}
        pass_clean = pass_str.strip().upper()
        if pass_clean not in pass_map:
            return "Invalid specification"
        has_fastpass = pass_map[pass_clean]
        eligible = height >= 120
        status = "FastPass Priority" if has_fastpass else "Standard Entry"
        return f"Height {height}cm: {'Approved' if eligible else 'Denied'} ({status})"
    except Exception:
        return "Invalid specification"

def compute_dispatch_throughput(ride_metric_str):
    try:
        if not ride_metric_str or not isinstance(ride_metric_str, str):
            return None
        parts = ride_metric_str.strip().split('/')
        if len(parts) != 2:
            return None
        riders = float(parts[0].strip())
        cycle_mins = float(parts[1].strip())
        if math.isnan(riders) or math.isnan(cycle_mins) or math.isinf(riders) or math.isinf(cycle_mins):
            return None
        if cycle_mins <= 0 or riders < 0:
            return None
        rate = riders / cycle_mins
        return round(rate, 2)
    except Exception:
        return None

def resolve_safety_restraint_code(zone_code):
    try:
        if not zone_code or not isinstance(zone_code, str):
            return "Unknown Restraint"
        prefix = zone_code.strip().upper()[:3]
        restraint_types = {
            "CST": "Over-the-Shoulder Harness",
            "WTR": "Lap Bar and Seatbelt",
            "DRP": "Hydraulic Shoulder Vest",
            "WHL": "Manual Safety Bar"
        }
        return restraint_types.get(prefix, "Unknown Restraint")
    except Exception:
        return "Unknown Restraint"

def main():
    print("==== Running validate_height_and_fastpass ====")
    r_input = input("Enter rider spec (Height:FastPass, e.g. 140:YES): ")
    print(validate_height_and_fastpass(r_input))

    print("\n==== Running compute_dispatch_throughput ====")
    t_input = input("Enter riders/mins (e.g. 48/2.5): ")
    print("Throughput (riders/min):", compute_dispatch_throughput(t_input))

    print("\n==== Running resolve_safety_restraint_code ====")
    z_input = input("Enter ride zone code (e.g. CST_01, WTR_A): ")
    print("Restraint:", resolve_safety_restraint_code(z_input))

if __name__ == "__main__":
    main()
