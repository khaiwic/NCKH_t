"""Reproducible desktop simulation for Table 4.3; NOT physical robot data.

Run from the project root: python -B code/simulation_ch4/simulate_ch4.py
All unmeasured plant/controller parameters are explicit assumptions in config.json.
Only numpy and matplotlib are required. No external planner/simulator service.
"""
from __future__ import annotations

import csv
import hashlib
import heapq
import json
import math
import platform
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/simulation_ch4"
CFG = {
    "data_type": "desktop numerical simulation, not hardware measurements",
    "seed": 20261031, "runs_per_scenario": 30,
    "wheel_radius_m": 0.022, "wheelbase_m": 0.135,
    "encoder_counts_per_output_revolution": 1400,
    "supply_label_V": 7.4,
    "supply_note": "Label only: no identification of motor gain from voltage/current.",
    "world_m": [4.0, 2.4], "grid_m": 0.05,
    "start_m": [0.3, 1.2], "goal_m": [3.3, 1.2],
    "obstacle_xyxy_m": [1.4, 0.85, 2.0, 1.55],
    "assumed_body_disc_radius_m": 0.11,
    "planner_extra_clearance_m": 0.15,
    "minimum_smoothed_extra_clearance_m": 0.10,
    "bezier_corner_trim_m": 0.15, "path_sample_m": 0.005,
    "vmax_m_s": 0.25, "accel_m_s2": 0.20,
    "wheel_reference_limit_m_s": 0.35, "omega_limit_rad_s": 1.5,
    "lookahead_m": 0.20,
    "dt_s": 0.01, "plant_substep_s": 0.0025,
    "outer_period_s": 0.05, "encoder_speed_window_s": 0.05,
    "PI_Kp_duty_per_m_s": 2.0, "PI_Ki_duty_per_m": 8.0,
    "PID_Kd": 0.0, "duty_limit": 0.8,
    "assumed_motor_max_rad_s": 25.0,
    "assumed_motor_tau_s": 0.12,
    "radius_relative_uniform_half_range": 0.01,
    "wheelbase_relative_uniform_half_range": 0.01,
    "motor_gain_relative_uniform_half_range": 0.05,
    "motor_tau_relative_uniform_half_range": 0.15,
    "initial_y_uniform_half_range_m": 0.02,
    "initial_heading_uniform_half_range_rad": 0.05,
    "wheel_slip_uniform_range": [0.0, 0.02],
    "slip_sine_amplitude": 0.002, "slip_sine_frequency_Hz": 0.7,
    "controller_position_stop_m": 0.015,
    "controller_heading_stop_rad": 0.025,
    "controller_settle_s": 0.5,
    "success_ground_truth_position_m": 0.05,
    "success_ground_truth_heading_rad": 0.10,
    "success_ground_truth_max_cross_track_m": 0.15,
    "timeout_s": 35.0,
    "assumptions": [
        "Circular body envelope, first-order wheel-speed dynamics; no identified electrical/torque model.",
        "Independent fixed perturbations per run, matched between the two scenarios.",
        "True wheel radius/base/gain/tau differ from controller nominal parameters.",
        "Encoder quantization and unobserved wheel slip; exact known initial pose.",
        "Controller uses encoder odometry only; ground truth never enters feedback.",
        "Signed normalized PWM, PI without feed-forward, derivative or anti-windup.",
        "Static known obstacle; no sensor, SLAM, online obstacle detection or replanning.",
        "No battery sag, gear backlash, caster dynamics, floor contact forces or current estimation.",
    ],
}


def wrap(a):
    return np.arctan2(np.sin(a), np.cos(a))


def point_obstacle_distance(p):
    p = np.asarray(p)
    x0, y0, x1, y1 = CFG["obstacle_xyxy_m"]
    dx = np.maximum(np.maximum(x0 - p[..., 0], p[..., 0] - x1), 0)
    dy = np.maximum(np.maximum(y0 - p[..., 1], p[..., 1] - y1), 0)
    return np.hypot(dx, dy)


def world_clearance(p):
    p = np.asarray(p)
    w, h = CFG["world_m"]
    return np.minimum.reduce([p[..., 0], p[..., 1], w-p[..., 0], h-p[..., 1]])


def segment_samples(a, b, step=0.001):
    return np.linspace(a, b, max(2, int(np.linalg.norm(b-a)/step)+2))


def safe_points(p, gap):
    return bool(np.all(point_obstacle_distance(p) >= gap) and
                np.all(world_clearance(p) >= gap))


def dijkstra_path():
    """8-connected metric grid, fixed tie order, no diagonal corner cutting."""
    g = CFG["grid_m"]
    w, h = CFG["world_m"]
    gap = CFG["assumed_body_disc_radius_m"] + CFG["planner_extra_clearance_m"]
    start, goal = [tuple(np.rint(np.array(CFG[k])/g).astype(int))
                   for k in ("start_m", "goal_m")]
    free = {(i, j) for i in range(round(w/g)+1) for j in range(round(h/g)+1)
            if safe_points(np.array([[i*g, j*g]]), gap)}
    assert start in free and goal in free
    moves = [(1,0), (0,-1), (0,1), (-1,0), (1,-1), (1,1), (-1,-1), (-1,1)]
    q, dist, parent, counter = [(0., 0, start)], {start: 0.}, {}, 0
    while q:
        cost, _, u = heapq.heappop(q)
        if cost != dist[u]:
            continue
        if u == goal:
            break
        for dx, dy in moves:
            v = (u[0]+dx, u[1]+dy)
            if v not in free:
                continue
            if dx and dy and ((u[0]+dx, u[1]) not in free or (u[0], u[1]+dy) not in free):
                continue
            if not safe_points(segment_samples(np.array(u)*g, np.array(v)*g), gap):
                continue
            nd = cost + g*math.hypot(dx, dy)
            if nd < dist.get(v, math.inf)-1e-12:
                counter += 1
                dist[v], parent[v] = nd, u
                heapq.heappush(q, (nd, counter, v))
    if goal not in dist:
        raise RuntimeError("No Dijkstra route")
    route = [goal]
    while route[-1] != start:
        route.append(parent[route[-1]])
    raw = np.array(route[::-1], dtype=float)*g
    # Greedy visibility shortcuts, preserving the complete inflated collision check.
    short, i = [raw[0]], 0
    while i < len(raw)-1:
        j = len(raw)-1
        while not safe_points(segment_samples(raw[i], raw[j]), gap):
            j -= 1
        assert j > i
        short.append(raw[j])
        i = j
    short = np.asarray(short)
    # Quadratic Bezier fillets. Shrink a fillet if the reserved clearance is lost.
    check_gap = CFG["assumed_body_disc_radius_m"] + CFG["minimum_smoothed_extra_clearance_m"]
    smooth = [short[0]]
    for i in range(1, len(short)-1):
        a, b, c = short[i-1:i+2]
        trim = min(CFG["bezier_corner_trim_m"], .4*np.linalg.norm(b-a), .4*np.linalg.norm(c-b))
        for _ in range(14):
            p = b - trim*(b-a)/np.linalg.norm(b-a)
            q2 = b + trim*(c-b)/np.linalg.norm(c-b)
            u = np.linspace(0, 1, 301)[:, None]
            curve = (1-u)**2*p + 2*(1-u)*u*b + u*u*q2
            if safe_points(curve, check_gap):
                break
            trim *= .5
        else:
            raise RuntimeError("Unsafe Bezier fillet")
        smooth.extend(segment_samples(np.asarray(smooth[-1]), p, .002)[1:])
        smooth.extend(curve[1:])
    smooth.extend(segment_samples(np.asarray(smooth[-1]), short[-1], .002)[1:])
    smooth = np.asarray(smooth)
    assert safe_points(smooth, check_gap)
    return raw, short, smooth


class ReferencePath:
    def __init__(self, points):
        s = np.r_[0., np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
        keep = np.r_[True, np.diff(s)>1e-10]
        s, points = s[keep], points[keep]
        self.length = float(s[-1])
        self.s = np.linspace(0, self.length, int(np.ceil(self.length/CFG["path_sample_m"]))+1)
        self.p = np.column_stack([np.interp(self.s, s, points[:, k]) for k in range(2)])
        self.d = np.diff(self.p, axis=0)
        self.ds = np.linalg.norm(self.d, axis=1)
        self.th = np.unwrap(np.arctan2(self.d[:, 1], self.d[:, 0]))

    def at(self, s):
        return np.column_stack([np.interp(np.atleast_1d(s), self.s, self.p[:, k]) for k in range(2)])

    def project(self, xy, previous=0):
        # Forward branch window, allowing small backward changes during steering.
        lo, hi = max(0, previous-10), min(len(self.d), previous+100)
        d, a = self.d[lo:hi], self.p[lo:hi]
        z = np.clip(np.sum((xy-a)*d, axis=1)/np.sum(d*d, axis=1), 0, 1)
        feet = a + z[:, None]*d
        j = int(np.argmin(np.sum((xy-feet)**2, axis=1)))
        ix = lo+j
        cross = float(np.dot(np.array([-math.sin(self.th[ix]), math.cos(self.th[ix])]), xy-feet[j]))
        return float(self.s[ix]+z[j]*self.ds[ix]), ix, cross

    def lookahead(self, xy, ix):
        radius = CFG["lookahead_m"]
        # First forward crossing of the actual lookahead circle.
        for j in range(ix, min(len(self.d), ix+150)):
            d, f = self.d[j], self.p[j]-xy
            aa, bb, cc = np.dot(d,d), 2*np.dot(f,d), np.dot(f,f)-radius**2
            disc = bb*bb-4*aa*cc
            if disc >= 0:
                roots = [(-bb-math.sqrt(disc))/(2*aa), (-bb+math.sqrt(disc))/(2*aa)]
                for z in roots:
                    if 0 <= z <= 1:
                        return self.p[j]+z*d
        if np.linalg.norm(self.p[-1]-xy) <= radius:
            return self.p[-1]
        raise RuntimeError("Lost forward path")


def nominal_profile(t, length):
    a, vmax = CFG["accel_m_s2"], CFG["vmax_m_s"]
    vp = min(vmax, math.sqrt(a*length))
    ta = vp/a
    tc = max(0., (length-vp*vp/a)/vp)
    T = 2*ta+tc
    t = np.asarray(t)
    s = np.where(t<ta, .5*a*t*t,
                 np.where(t<ta+tc, .5*a*ta*ta+vp*(t-ta), length-.5*a*np.maximum(T-t,0)**2))
    v = np.where(t<ta, a*t, np.where(t<ta+tc, vp, a*np.maximum(T-t,0)))
    return np.clip(s,0,length), np.maximum(v,0), T


def integrate_pose(p, dl, dr, base):
    ds, dth = .5*(dl+dr), (dr-dl)/base
    # Exact constant-twist SE(2) update, with a stable zero-angle limit.
    scale = np.sinc(dth/(2*np.pi))
    mid = p[2]+dth/2
    return p + np.array([ds*scale*math.cos(mid), ds*scale*math.sin(mid), dth])


def parameters(seed, ideal=False):
    rng = np.random.default_rng(seed)
    def pair(key):
        return 1+rng.uniform(-CFG[key], CFG[key], 2)
    r = CFG["wheel_radius_m"]*pair("radius_relative_uniform_half_range")
    base = CFG["wheelbase_m"]*(1+rng.uniform(-CFG["wheelbase_relative_uniform_half_range"], CFG["wheelbase_relative_uniform_half_range"]))
    gain = CFG["assumed_motor_max_rad_s"]*pair("motor_gain_relative_uniform_half_range")
    tau = CFG["assumed_motor_tau_s"]*pair("motor_tau_relative_uniform_half_range")
    slip = rng.uniform(*CFG["wheel_slip_uniform_range"], 2)
    phase = rng.uniform(0, 2*np.pi, 2)
    y = rng.uniform(-CFG["initial_y_uniform_half_range_m"], CFG["initial_y_uniform_half_range_m"])
    th = rng.uniform(-CFG["initial_heading_uniform_half_range_rad"], CFG["initial_heading_uniform_half_range_rad"])
    if ideal:
        r[:], base, gain[:], tau[:], slip[:], y, th = .022, .135, 25., .12, 0., 0., 0.
    return {"r":r, "base":base, "gain":gain, "tau":tau, "slip":slip, "phase":phase, "y":y, "th":th, "ideal":ideal}


def simulate(path, obstacle, seed, *, substep=None, ideal=False):
    pa = parameters(seed, ideal)
    dt = CFG["dt_s"]
    substep = substep or CFG["plant_substep_s"]
    nsub = round(dt/substep)
    assert abs(nsub*substep-dt)<1e-12
    r0, base0 = CFG["wheel_radius_m"], CFG["wheelbase_m"]
    tick = 2*np.pi/CFG["encoder_counts_per_output_revolution"]
    th0 = path.th[0]+pa["th"]
    truth = np.r_[path.p[0]+np.array([0., pa["y"]]), th0]
    odom = truth.copy()
    angle, omega, integ, measured = [np.zeros(2) for _ in range(4)]
    oldcounts = np.zeros(2, dtype=int)
    counts_history = [oldcounts.copy()]
    win = round(CFG["encoder_speed_window_s"]/dt)
    outer = round(CFG["outer_period_s"]/dt)
    reference, duty = np.zeros(2), np.zeros(2)
    stage, stage_time, ix, ig, rows = "follow", 0., 0, 0, []
    status = "timeout"
    for k in range(round(CFG["timeout_s"]/dt)):
        t = k*dt
        # The controller sees ONLY nominal encoder odometry and nominal geometry.
        if k % outer == 0:
            s, ix, _ = path.project(odom[:2], ix)
            remaining = max(0., path.length-s)
            goal_dist = np.linalg.norm(odom[:2]-path.p[-1])
            if stage == "follow" and goal_dist <= CFG["controller_position_stop_m"]:
                stage, stage_time = "align", t
            if stage == "align":
                heading_err = float(wrap(path.th[-1]-odom[2]))
                if abs(heading_err) < CFG["controller_heading_stop_rad"]:
                    stage, stage_time = "settle", t
                v, w = 0., float(np.clip(2*heading_err, -.5, .5))
            elif stage == "settle":
                v, w = 0., 0.
            else:
                target = path.lookahead(odom[:2], ix)
                dx, dy = target-odom[:2]
                yr = -math.sin(odom[2])*dx+math.cos(odom[2])*dy
                kappa = 2*yr/max(dx*dx+dy*dy, 1e-6)
                v = min(CFG["vmax_m_s"], CFG["accel_m_s2"]*t,
                        math.sqrt(2*CFG["accel_m_s2"]*remaining))
                w = v*kappa
                ratio = max(1., abs(w)/CFG["omega_limit_rad_s"],
                            max(abs(v-base0*w/2),abs(v+base0*w/2))/CFG["wheel_reference_limit_m_s"])
                v, w = v/ratio, w/ratio
            if stage == "settle":
                v, w = 0., 0.
            reference = np.array([v-base0*w/2, v+base0*w/2])
        e = reference-measured
        integ += e*dt
        unsat = CFG["PI_Kp_duty_per_m_s"]*e+CFG["PI_Ki_duty_per_m"]*integ
        duty = np.clip(unsat,-CFG["duty_limit"],CFG["duty_limit"])
        # Body clearance is evaluated on every plant substep, not only saved samples.
        minstep = math.inf
        for h in range(nsub):
            target_omega = pa["gain"]*duty
            decay = np.exp(-substep/pa["tau"])
            da = target_omega*substep + (omega-target_omega)*pa["tau"]*(1-decay)
            omega = target_omega+(omega-target_omega)*decay
            angle += da
            slip = pa["slip"] + (0 if ideal else CFG["slip_sine_amplitude"]*np.sin(2*np.pi*CFG["slip_sine_frequency_Hz"]*(t+(h+.5)*substep)+pa["phase"]))
            ds = pa["r"]*da*(1-slip)
            truth = integrate_pose(truth, ds[0], ds[1], pa["base"])
            clear = float(world_clearance(truth[:2]))-CFG["assumed_body_disc_radius_m"]
            if obstacle:
                clear = min(clear,float(point_obstacle_distance(truth[:2]))-CFG["assumed_body_disc_radius_m"])
            minstep = min(minstep,clear)
        counts = np.rint(angle/tick).astype(int)
        dc = counts-oldcounts
        odom = integrate_pose(odom, *(dc*tick*r0), base0)
        counts_history.append(counts.copy())
        span = min(win,len(counts_history)-1)
        measured = (counts-counts_history[-1-span])*tick*r0/(span*dt)
        oldcounts = counts
        _, ig, cross = path.project(truth[:2], ig)
        rows.append([t+dt, *truth, *odom, *reference, *measured, *duty, *unsat,
                     int(counts[0]),int(counts[1]), cross, minstep, float(stage=="follow")])
        if minstep <= 0:
            status = "collision"
            break
        if stage == "settle" and t-stage_time >= CFG["controller_settle_s"] and max(abs(omega*r0))<.01:
            status = "controller_finished"
            break
    a = np.asarray(rows)
    sd, _, Tnom = nominal_profile(a[:,0], path.length)
    pd = path.at(sd)
    thd = np.interp(sd,path.s[:-1],path.th)
    ep = np.linalg.norm(a[:,1:3]-pd,axis=1)
    eh = np.abs(wrap(a[:,3]-thd))
    final = float(np.linalg.norm(a[-1,1:3]-path.p[-1]))
    final_h = float(abs(wrap(a[-1,3]-path.th[-1])))
    crossmax = float(max(abs(a[:,17])))
    success = (status == "controller_finished" and final <= CFG["success_ground_truth_position_m"]
               and final_h <= CFG["success_ground_truth_heading_rad"]
               and crossmax <= CFG["success_ground_truth_max_cross_track_m"] and np.min(a[:,18])>0)
    metrics = {"seed":seed,"success":bool(success),"termination":status,
               "rmse_position_m":float(np.sqrt(np.mean(ep**2))),
               "max_cross_track_m":crossmax,"mean_abs_heading_rad":float(np.mean(eh)),
               "final_position_error_m":final,"final_heading_error_rad":final_h,
               "completion_s":float(a[-1,0]),"nominal_profile_s":Tnom,
               "min_clearance_m":float(np.min(a[:,18])) if obstacle else None,
               "pwm_saturation_percent":float(100*np.mean(np.any(np.abs(a[:,13:15])>=CFG["duty_limit"]-1e-12,axis=1)))}
    return a, metrics, pa


COLUMNS = ["time_s","gt_x_m","gt_y_m","gt_heading_rad","odo_x_m","odo_y_m","odo_heading_rad",
           "vref_L_m_s","vref_R_m_s","vmeas_L_m_s","vmeas_R_m_s","pwm_L","pwm_R",
           "unclipped_pwm_L","unclipped_pwm_R","encoder_count_L","encoder_count_R",
           "cross_track_m","body_clearance_m","following"]


def aggregate(results):
    stats = {"trials":len(results), "successes":sum(r["success"] for r in results),
             "collisions":sum(r["termination"]=="collision" for r in results),
             "aggregation":"all runs for errors; completion time for successful runs only; extrema over all runs"}
    for key in results[0]:
        if key in ("seed","success","termination") or results[0][key] is None:
            continue
        v = np.array([r[key] for r in results])
        stats[key] = {"mean":float(v.mean()),"sample_sd":float(v.std(ddof=1)),
                      "min":float(v.min()),"max":float(v.max())}
    successful = [r["completion_s"] for r in results if r["success"]]
    stats["successful_completion_s"] = {"n":len(successful),
        "mean":float(np.mean(successful)) if successful else None,
        "sample_sd":float(np.std(successful,ddof=1)) if len(successful)>1 else None}
    return stats


def export_table(summary):
    def ms(s,key):
        return f"{s[key]['mean']:.3f} ± {s[key]['sample_sd']:.3f}"
    rows=[]
    for title,key in [("Số lượt thử / số lượt thành công","counts"),
                      ("RMSE vị trí theo thời gian (m)","rmse_position_m"),
                      ("Sai số ngang lớn nhất toàn bộ lượt (m)","max_cross_track_m"),
                      ("Sai số hướng tuyệt đối trung bình (rad)","mean_abs_heading_rad"),
                      ("Sai số vị trí khi kết thúc (m)","final_position_error_m"),
                      ("Thời gian hoàn thành - chỉ lượt thành công (s)","successful_completion_s"),
                      ("Khoảng hở thân xe nhỏ nhất toàn bộ lượt (m)","min_clearance_m"),
                      ("Tỷ lệ thời gian ít nhất một kênh PWM bão hòa (%)","pwm_saturation_percent")]:
        values=[]
        for name,s in summary.items():
            if key=="counts":value=f"{s['trials']} / {s['successes']}"
            elif key=="max_cross_track_m":value=f"{s[key]['max']:.3f}"
            elif key=="min_clearance_m":value="Không áp dụng" if name=="straight" else f"{s[key]['min']:.5f}"
            else:value=ms(s,key)
            values.append(value)
        rows.append([title,*values])
    with (OUT/"table_4_3.csv").open("w",encoding="utf-8-sig",newline="") as f:
        wr=csv.writer(f);wr.writerow(["Chỉ tiêu","Đường thẳng","Có vật cản"]);wr.writerows(rows)


def plot_results(paths, logs, results):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.unicode_minus":False})
    fig, axes = plt.subplots(2,3,figsize=(14,7.2),constrained_layout=True)
    for row,name in enumerate(("straight","obstacle")):
        path = paths[name]
        # Median RMSE representative chosen AFTER statistics, all other runs still shown.
        idx = int(np.argsort([m["rmse_position_m"] for m in results[name]])[len(results[name])//2])
        a = logs[name][idx]
        ax = axes[row,0]
        for run in logs[name]:
            ax.plot(run[:,1],run[:,2],color="#4693bb",alpha=.15,lw=.7)
        ax.plot(path.p[:,0],path.p[:,1],"k--",lw=1.5,label="Tham chiếu hình học")
        ax.plot(a[:,1],a[:,2],color="#b02b35",lw=1.3,label=f"Lượt {idx+1} (đại diện)")
        if row:
            x0,y0,x1,y1=CFG["obstacle_xyxy_m"]
            ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,color="#333333"))
        ax.set(xlabel="x (m)",ylabel="y (m)",title="Đường thẳng: 30 lượt" if not row else "Dijkstra + Bézier: 30 lượt")
        ax.set_aspect("equal",adjustable="box")
        ax.set_xlim(0,4.0);ax.set_ylim(0,2.4)
        ax.legend(fontsize=8,loc="upper right")
        ax=axes[row,1]
        sd,_,_=nominal_profile(a[:,0],path.length)
        pd=path.at(sd)
        ax.plot(a[:,0],np.linalg.norm(a[:,1:3]-pd,axis=1),label="Sai số vị trí theo thời gian")
        ax.plot(a[:,0],abs(a[:,17]),label="|Sai số ngang|")
        ax.set(xlabel="t (s)",ylabel="Sai số (m)",title=f"Lượt {idx+1}: sai số từ trạng thái thật mô phỏng")
        ax.legend(fontsize=8)
        ax=axes[row,2]
        ax.plot(a[:,0],a[:,7],"--",label="Đặt L",lw=1)
        ax.plot(a[:,0],a[:,8],"--",label="Đặt R",lw=1)
        ax.plot(a[:,0],a[:,9],label="Encoder L",lw=.9)
        ax.plot(a[:,0],a[:,10],label="Encoder R",lw=.9)
        ax.set(xlabel="t (s)",ylabel="Vận tốc bánh (m/s)",title="Profile hình thang và vận tốc hai bánh")
        ax.legend(fontsize=8,ncol=2)
    for ax in axes.flat:
        ax.grid(alpha=.2)
    fig.suptitle("MÔ PHỎNG SỐ: Pure Pursuit – PI, không phải kết quả đo trên robot",fontsize=14,weight="bold")
    fig.savefig(OUT/"simulation_summary.png",dpi=190)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    CFG["software"]={"python":platform.python_version(),"numpy":np.__version__}
    CFG["source_sha256"]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    raw, short, smooth = dijkstra_path()
    paths = {"straight":ReferencePath(np.array([CFG["start_m"],CFG["goal_m"]])),"obstacle":ReferencePath(smooth)}
    np.savetxt(OUT/"dijkstra_raw.csv",raw,delimiter=",",header="x_m,y_m",comments="")
    np.savetxt(OUT/"dijkstra_shortcuts.csv",short,delimiter=",",header="x_m,y_m",comments="")
    CFG["path_lengths_m"] = {k:v.length for k,v in paths.items()}
    results, logs, params_all = {}, {}, {}
    for name,path in paths.items():
        results[name],logs[name],params_all[name]=[],[],[]
        (OUT/name).mkdir(exist_ok=True)
        np.savetxt(OUT/name/"reference_path.csv",np.c_[path.s,path.p],delimiter=",",header="s_m,x_m,y_m",comments="")
        for run in range(CFG["runs_per_scenario"]):
            seed=CFG["seed"]+run
            a,m,pa=simulate(path,name=="obstacle",seed)
            # Verify numeric metrics independently from saved raw arrays below.
            np.savetxt(OUT/name/f"run_{run+1:02d}.csv",a,delimiter=",",header=",".join(COLUMNS),comments="",fmt="%.10g")
            results[name].append(m);logs[name].append(a)
            params_all[name].append({k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in pa.items()})
        print(name,json.dumps(aggregate(results[name]),ensure_ascii=False),flush=True)
    # Physical checks: perfect symmetric straight plant, dense path clearance, integrator convergence.
    ideal,im,_=simulate(paths["straight"],False,CFG["seed"],ideal=True)
    assert max(abs(ideal[:,2]-CFG["start_m"][1]))<1e-10
    assert max(abs(ideal[:,3]))<1e-10
    assert im["success"]
    checks={"ideal_straight_max_lateral_m":float(max(abs(ideal[:,2]-CFG["start_m"][1]))),
            "smoothed_path_min_body_obstacle_clearance_m":float(np.min(point_obstacle_distance(paths["obstacle"].p)))-CFG["assumed_body_disc_radius_m"],
            "numerical_convergence":{}}
    for name,path in paths.items():
        _,fine,_=simulate(path,name=="obstacle",CFG["seed"],substep=CFG["plant_substep_s"]/2)
        coarse=results[name][0]
        delta={key:abs(fine[key]-coarse[key]) for key in ("rmse_position_m","max_cross_track_m","final_position_error_m","completion_s")}
        assert delta["rmse_position_m"]<.002 and delta["final_position_error_m"]<.002 and delta["completion_s"]<.15
        checks["numerical_convergence"][name]=delta
    # Reload the exported CSVs and recompute every reported table metric.
    reload_max=0.
    for name,path in paths.items():
        for j,m in enumerate(results[name]):
            a=np.loadtxt(OUT/name/f"run_{j+1:02d}.csv",delimiter=",",skiprows=1)
            s,_,_=nominal_profile(a[:,0],path.length)
            p=path.at(s);theta=np.interp(s,path.s[:-1],path.th)
            recalculated={"rmse_position_m":float(np.sqrt(np.mean(np.sum((a[:,1:3]-p)**2,axis=1)))),
                          "max_cross_track_m":float(max(abs(a[:,17]))),
                          "mean_abs_heading_rad":float(np.mean(abs(wrap(a[:,3]-theta)))),
                          "final_position_error_m":float(np.linalg.norm(a[-1,1:3]-path.p[-1])),
                          "completion_s":float(a[-1,0]),
                          "pwm_saturation_percent":float(100*np.mean(np.any(abs(a[:,13:15])>=CFG["duty_limit"]-1e-8,axis=1)))}
            if name=="obstacle":
                recalculated["min_clearance_m"]=float(min(a[:,18]))
            for key,value in recalculated.items():
                err=abs(m[key]-value);reload_max=max(reload_max,err)
                assert err<1e-6,(name,j,key,m[key],value)
    checks["csv_recompute_max_absolute_difference"]=reload_max
    summary={k:aggregate(v) for k,v in results.items()}
    export_table(summary)
    for file,obj in (("config.json",CFG),("per_run_metrics.json",results),("per_run_parameters.json",params_all),
                     ("summary.json",summary),("validation.json",checks)):
        (OUT/file).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
    with (OUT/"per_run_metrics.csv").open("w",encoding="utf-8-sig",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=["scenario",*results["straight"][0]])
        wr.writeheader()
        for name,rs in results.items():
            wr.writerows({"scenario":name,**r} for r in rs)
    plot_results(paths,logs,results)
    manifest={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(OUT.rglob("*")) if p.is_file() and p.name!="sha256.json"}
    (OUT/"sha256.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print("VALIDATION",json.dumps(checks,ensure_ascii=False),flush=True)


if __name__ == "__main__":
    main()
