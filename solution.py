import json
import math
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

EPS = 1e-7


def dist(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def point_in_circle(p: Tuple[float, float], c: Tuple[float, float], r: float) -> bool:
    return dist(p, c) <= r + EPS


def point_in_rect(p: Tuple[float, float], rect: Tuple[float, float, float, float]) -> bool:
    x, y = p
    x1, y1, x2, y2 = rect
    return x1 - EPS <= x <= x2 + EPS and y1 - EPS <= y <= y2 + EPS


def inside_interval_circle(a: Tuple[float, float], b: Tuple[float, float], center: Tuple[float, float], radius: float) -> Optional[Tuple[float, float]]:
    ax, ay = a
    bx, by = b
    cx, cy = center
    dx, dy = bx - ax, by - ay
    fx, fy = ax - cx, ay - cy
    A = dx * dx + dy * dy
    if A <= EPS:
        return (0.0, 1.0) if point_in_circle(a, center, radius) else None

    B = 2.0 * (fx * dx + fy * dy)
    C = fx * fx + fy * fy - radius * radius
    D = B * B - 4.0 * A * C

    if D < -EPS:
        return (0.0, 1.0) if point_in_circle(a, center, radius) else None

    if abs(D) <= EPS:
        u = -B / (2.0 * A)
        if -EPS <= u <= 1.0 + EPS:
            u = min(1.0, max(0.0, u))
            return (u, u)
        return (0.0, 1.0) if point_in_circle(a, center, radius) else None

    sqrt_d = math.sqrt(max(0.0, D))
    u1 = (-B - sqrt_d) / (2.0 * A)
    u2 = (-B + sqrt_d) / (2.0 * A)
    lo, hi = min(u1, u2), max(u1, u2)

    start = max(0.0, lo)
    end = min(1.0, hi)
    if start <= end + EPS:
        start = min(1.0, max(0.0, start))
        end = min(1.0, max(0.0, end))
        return (start, end)

    return (0.0, 1.0) if point_in_circle(a, center, radius) else None


def inside_interval_rect(a: Tuple[float, float], b: Tuple[float, float], rect: Tuple[float, float, float, float]) -> Optional[Tuple[float, float]]:
    x1, y1 = a
    x2, y2 = b
    xmin, ymin, xmax, ymax = rect

    dx = x2 - x1
    dy = y2 - y1

    p = [-dx, dx, -dy, dy]
    q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]

    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if abs(pi) <= EPS:
            if qi < -EPS:
                return None
            continue
        t = qi / pi
        if pi < 0:
            u1 = max(u1, t)
        else:
            u2 = min(u2, t)
        if u1 - u2 > EPS:
            return None

    if u1 <= u2 + EPS:
        return (max(0.0, u1), min(1.0, u2))

    if point_in_rect(a, rect):
        return (0.0, 1.0)
    return None


def parse_nfzs(no_fly_zones: List[Dict]) -> List[Dict]:
    zones = []
    for z in no_fly_zones:
        shape = z.get("shape")
        item = {
            "shape": shape,
            "T_start": float(z.get("T_start", 0.0)),
            "T_end": float(z.get("T_end", 0.0)),
        }
        if shape == "circle":
            item["center"] = (float(z["center"][0]), float(z["center"][1]))
            item["radius"] = float(z["radius"])
        elif shape == "rectangle":
            c1, c2 = z["corners"]
            xmin, xmax = sorted([float(c1[0]), float(c2[0])])
            ymin, ymax = sorted([float(c1[1]), float(c2[1])])
            item["rect"] = (xmin, ymin, xmax, ymax)
        else:
            continue
        zones.append(item)
    return zones


def segment_intervals(a: Tuple[float, float], b: Tuple[float, float], zones: List[Dict]) -> List[Tuple[float, float, float, float]]:
    d = dist(a, b)
    if d <= EPS:
        return []

    out = []
    for z in zones:
        uv = None
        if z["shape"] == "circle":
            uv = inside_interval_circle(a, b, z["center"], z["radius"])
        elif z["shape"] == "rectangle":
            uv = inside_interval_rect(a, b, z["rect"])

        if uv is None:
            continue
        u0, u1 = uv
        s0 = max(0.0, min(1.0, u0)) * d
        s1 = max(0.0, min(1.0, u1)) * d
        if s0 > s1:
            s0, s1 = s1, s0
        out.append((s0, s1, z["T_start"], z["T_end"]))
    return out


def required_wait(a: Tuple[float, float], b: Tuple[float, float], t0: float, zones: List[Dict]) -> float:
    intervals = segment_intervals(a, b, zones)
    if not intervals:
        return 0.0

    w = 0.0
    for _ in range(64):
        changed = False
        for s0, s1, ts, te in intervals:
            enter = t0 + w + s0
            leave = t0 + w + s1
            if enter <= te + EPS and leave >= ts - EPS:
                needed = te - (t0 + s0) + EPS
                if needed > w + EPS:
                    w = needed
                    changed = True
        if not changed:
            break
    return max(0.0, w)


@dataclass
class DroneState:
    drone_id: str
    max_payload: float
    available_time: float = 0.0
    path: List[Dict] = field(default_factory=list)


def add_action(path: List[Dict], x: float, y: float, t: float, action: str, extra: Optional[Dict] = None) -> None:
    item = {
        "x": float(round(x, 6)),
        "y": float(round(y, 6)),
        "t": float(round(t, 6)),
        "action": action,
    }
    if extra:
        item.update(extra)
    path.append(item)


def simulate_single_delivery_trip(start_time: float, wh: Tuple[float, float], delivery: Dict, zones: List[Dict]) -> Optional[Dict]:
    target = (float(delivery["x"]), float(delivery["y"]))
    weight = float(delivery["weight"])

    t = start_time
    actions: List[Tuple[str, float]] = []

    wait1 = required_wait(wh, target, t, zones)
    if wait1 > EPS:
        t += wait1
        actions.append(("WAIT_WH", t))

    d1 = dist(wh, target)
    t_deliver = t + d1

    wait2 = required_wait(target, wh, t_deliver, zones)
    t_after_wait = t_deliver
    if wait2 > EPS:
        t_after_wait += wait2
        actions.append(("WAIT_TARGET", t_after_wait))

    d2 = dist(target, wh)
    t_return = t_after_wait + d2

    energy = d1 * (1.0 + weight) + d2
    if energy > 500.0 + EPS:
        return None

    return {
        "deliver_time": t_deliver,
        "return_time": t_return,
        "energy": energy,
        "wait_wh": wait1,
        "wait_target": wait2,
    }


def solve(data: Dict) -> Dict:
    w, h = data["map_size"]
    warehouse = (float(w) / 2.0, float(h) / 2.0)
    zones = parse_nfzs(data.get("no_fly_zones", []))

    drones = [
        DroneState(drone_id=d["id"], max_payload=float(d["max_payload"]))
        for d in data.get("drones", [])
    ]

    deliveries = sorted(data.get("deliveries", []), key=lambda d: float(d["deadline"]))

    for delivery in deliveries:
        weight = float(delivery["weight"])
        deadline = float(delivery["deadline"])

        best = None
        for i, drone in enumerate(drones):
            if weight > drone.max_payload + EPS:
                continue
            sim = simulate_single_delivery_trip(drone.available_time, warehouse, delivery, zones)
            if sim is None:
                continue
            if sim["deliver_time"] > deadline + EPS:
                continue

            candidate = (sim["return_time"], sim["deliver_time"], i, sim)
            if best is None or candidate < best:
                best = candidate

        if best is None:
            continue

        _, _, idx, sim = best
        drone = drones[idx]
        start_t = drone.available_time
        target = (float(delivery["x"]), float(delivery["y"]))

        add_action(
            drone.path,
            warehouse[0],
            warehouse[1],
            start_t,
            "PICKUP",
            {"delivery_ids": [delivery["id"]]},
        )

        if sim["wait_wh"] > EPS:
            add_action(drone.path, warehouse[0], warehouse[1], start_t + sim["wait_wh"], "WAIT")

        add_action(drone.path, target[0], target[1], sim["deliver_time"], "DELIVER", {"delivery_id": delivery["id"]})

        if sim["wait_target"] > EPS:
            add_action(drone.path, target[0], target[1], sim["deliver_time"] + sim["wait_target"], "WAIT")

        add_action(drone.path, warehouse[0], warehouse[1], sim["return_time"], "RETURN")

        drone.available_time = sim["return_time"]

    manifest = []
    for drone in drones:
        if not drone.path:
            continue
        # Ensure first action PICKUP and last action RETURN
        if drone.path[0]["action"] != "PICKUP" or drone.path[-1]["action"] != "RETURN":
            continue
        manifest.append({"drone_id": drone.drone_id, "path": drone.path})

    return {"flight_manifest": manifest}


def main() -> None:
    raw = sys.stdin.read().strip()
    if not raw:
        print(json.dumps({"flight_manifest": []}))
        return

    data = json.loads(raw)
    ans = solve(data)
    print(json.dumps(ans, separators=(",", ":")))


if __name__ == "__main__":
    main()
