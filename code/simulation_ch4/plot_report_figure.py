"""Draw report Figure 4.5 from existing simulation CSVs; no invented samples."""
from pathlib import Path
import json

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/simulation_ch4"
cfg = json.loads((OUT/"config.json").read_text(encoding="utf-8"))
metrics = json.loads((OUT/"per_run_metrics.json").read_text(encoding="utf-8"))
plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":12,
                     "axes.unicode_minus":False})
fig, axes = plt.subplots(2,2,figsize=(10.6,8.0),layout="constrained")
chosen = {}
for row,name in enumerate(("straight","obstacle")):
    reference = np.loadtxt(OUT/name/"reference_path.csv",delimiter=",",skiprows=1)
    runs = [np.loadtxt(OUT/name/f"run_{j+1:02d}.csv",delimiter=",",skiprows=1)
            for j in range(30)]
    j = int(np.argsort([m["rmse_position_m"] for m in metrics[name]])[15])
    chosen[name] = {"run":j+1,"seed":metrics[name][j]["seed"],
                    "selection":"upper median of the 30 per-run position RMSEs"}
    a=runs[j]
    ax=axes[row,0]
    for b in runs:
        ax.plot(b[:,1],b[:,2],color="#688eae",alpha=.30,lw=.8)
    ax.plot(reference[:,1],reference[:,2],"k--",lw=1.6)
    ax.plot(a[:,1],a[:,2],color="#af3036",lw=1.8)
    if name=="obstacle":
        x0,y0,x1,y1=cfg["obstacle_xyxy_m"]
        ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,color="#333333"))
    ax.set(xlim=(0,3.8),ylim=(0,2.2),xlabel="x (m)",ylabel="y (m)",
           title="(a) Đường thẳng: 30 lượt" if row==0 else "(c) Có vật cản: 30 lượt")
    ax.set_aspect("equal",adjustable="box")
    ax.legend(handles=[Line2D([],[],color="k",ls="--",label="Tham chiếu"),
                       Line2D([],[],color="#af3036",label=f"Lượt {j+1}"),
                       Line2D([],[],color="#688eae",alpha=.6,label="Các lượt đã chạy")],
              fontsize=9,loc="upper right")
    # Analytic nominal trapezoid position at the recorded timestamps.
    length=reference[-1,0]
    acc,vmax=cfg["accel_m_s2"],cfg["vmax_m_s"]
    vp=min(vmax,np.sqrt(acc*length));ta=vp/acc
    tc=max(0,(length-vp*vp/acc)/vp);total=2*ta+tc
    t=a[:,0]
    progress=np.where(t<ta,.5*acc*t*t,
                      np.where(t<ta+tc,.5*acc*ta*ta+vp*(t-ta),
                               length-.5*acc*np.maximum(total-t,0)**2))
    progress=np.clip(progress,0,length)
    target=np.column_stack([np.interp(progress,reference[:,0],reference[:,k]) for k in (1,2)])
    err=np.linalg.norm(a[:,1:3]-target,axis=1)
    assert abs(float(np.sqrt(np.mean(err*err)))-metrics[name][j]["rmse_position_m"])<1e-7
    ax=axes[row,1]
    ax.plot(t,err,color="#1d6e9a",lw=1.8,label="Sai số vị trí theo thời gian")
    ax.plot(t,abs(a[:,17]),color="#d1791a",lw=1.6,label="Độ lớn sai số ngang")
    ax.set(xlabel="Thời gian (s)",ylabel="Sai số (m)",
           title=f"({'b' if row==0 else 'd'}) Sai số lượt {j+1}",ylim=(0,None))
    ax.legend(fontsize=9,loc="upper left")
for ax in axes.flat:
    ax.grid(alpha=.20)
fig.savefig(ROOT/"LaRex/picture/Hinh_4_5_Ket_qua_mo_phong.png",dpi=240)
plt.close(fig)
(OUT/"report_figure_selection.json").write_text(json.dumps(chosen,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(chosen,ensure_ascii=False))
