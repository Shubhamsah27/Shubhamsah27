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


def simulate_trip(start_time: float, wh: Tuple[float, float], deliveries: List[Dict], zones: List[Dict]) -> Optional[Dict]:
    t = start_time
    pos = wh
    payload = sum(float(d["weight"]) for d in deliveries)
    energy = 0.0
    events: List[Dict] = []

    for d in deliveries:
        target = (float(d["x"]), float(d["y"]))
        wait = required_wait(pos, target, t, zones)
        if wait > EPS:
            t += wait
            events.append({"action": "WAIT", "x": pos[0], "y": pos[1], "t": t})

        leg = dist(pos, target)
        energy += leg * (1.0 + payload)
        t += leg
        if t > float(d["deadline"]) + EPS:
            return None

        events.append(
            {
                "action": "DELIVER",
                "x": target[0],
                "y": target[1],
                "t": t,
                "delivery_id": d["id"],
            }
        )
        payload -= float(d["weight"])
        pos = target

    wait = required_wait(pos, wh, t, zones)
    if wait > EPS:
        t += wait
        events.append({"action": "WAIT", "x": pos[0], "y": pos[1], "t": t})

    leg = dist(pos, wh)
    energy += leg * (1.0 + payload)
    t += leg
    if energy > 500.0 + EPS:
        return None

    events.append({"action": "RETURN", "x": wh[0], "y": wh[1], "t": t})
    return {"events": events, "return_time": t, "energy": energy}


def nearest_order(wh: Tuple[float, float], deliveries: List[Dict]) -> List[Dict]:
    unused = deliveries[:]
    order: List[Dict] = []
    cur = wh
    while unused:
        best_idx = min(
            range(len(unused)),
            key=lambda i: (dist(cur, (float(unused[i]["x"]), float(unused[i]["y"]))), float(unused[i]["deadline"])),
        )
        nxt = unused.pop(best_idx)
        order.append(nxt)
        cur = (float(nxt["x"]), float(nxt["y"]))
    return order


def plan_best_trip(start_time: float, wh: Tuple[float, float], max_payload: float, pending: List[Dict], zones: List[Dict]) -> Optional[Dict]:
    if not pending:
        return None

    candidates = sorted(
        pending,
        key=lambda d: (float(d["deadline"]), dist(wh, (float(d["x"]), float(d["y"])))),
    )

    selected: List[Dict] = []
    total_w = 0.0
    for d in candidates:
        w = float(d["weight"])
        if total_w + w <= max_payload + EPS:
            selected.append(d)
            total_w += w
    if not selected:
        return None

    while selected:
        orders: List[List[Dict]] = []
        deadline_order = sorted(selected, key=lambda d: float(d["deadline"]))
        orders.append(deadline_order)
        nn_order = nearest_order(wh, selected)
        if [x["id"] for x in nn_order] != [x["id"] for x in deadline_order]:
            orders.append(nn_order)

        best = None
        for order in orders:
            sim = simulate_trip(start_time, wh, order, zones)
            if sim is None:
                continue
            score = (-len(order), sim["return_time"], sim["energy"])
            if best is None or score < best[0]:
                best = (score, order, sim)
        if best is not None:
            _, order, sim = best
            return {"deliveries": order, "sim": sim}

        selected = sorted(selected, key=lambda d: float(d["deadline"]))[:-1]
    return None


def solve(data: Dict) -> Dict:
    w, h = data["map_size"]
    warehouse = (float(w) / 2.0, float(h) / 2.0)
    zones = parse_nfzs(data.get("no_fly_zones", []))

    drones = [
        DroneState(drone_id=d["id"], max_payload=float(d["max_payload"]))
        for d in data.get("drones", [])
    ]

    pending = {d["id"]: d for d in data.get("deliveries", [])}

    progress = True
    while progress and pending:
        progress = False
        for drone in sorted(drones, key=lambda x: x.available_time):
            plan = plan_best_trip(
                start_time=drone.available_time,
                wh=warehouse,
                max_payload=drone.max_payload,
                pending=list(pending.values()),
                zones=zones,
            )
            if plan is None:
                continue

            chosen = plan["deliveries"]
            sim = plan["sim"]
            if not chosen:
                continue

            add_action(
                drone.path,
                warehouse[0],
                warehouse[1],
                drone.available_time,
                "PICKUP",
                {"delivery_ids": [d["id"] for d in chosen]},
            )

            for ev in sim["events"]:
                if ev["action"] == "WAIT":
                    add_action(drone.path, ev["x"], ev["y"], ev["t"], "WAIT")
                elif ev["action"] == "DELIVER":
                    add_action(
                        drone.path,
                        ev["x"],
                        ev["y"],
                        ev["t"],
                        "DELIVER",
                        {"delivery_id": ev["delivery_id"]},
                    )
                elif ev["action"] == "RETURN":
                    add_action(drone.path, ev["x"], ev["y"], ev["t"], "RETURN")

            drone.available_time = sim["return_time"]
            for d in chosen:
                pending.pop(d["id"], None)
            progress = True

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
