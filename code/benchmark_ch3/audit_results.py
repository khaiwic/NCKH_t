"""Independent Gauss quadrature audit of saved quadratic segments."""
import importlib.util
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/benchmark_ch3'
paths=json.loads((OUT/'paths.json').read_text(encoding='utf-8'))
rows={r['id']:r for r in json.loads((OUT/'per_run_metrics.json').read_text(encoding='utf-8'))}
x,w=np.polynomial.legendre.leggauss(96);u=((x+1)/2)[:,None];weights=w/2
max_abs=0.;max_rel=0.;segments_count=0
for identity,data in paths.items():
    integral=0.
    for segment in data['quadratic_controls']:
        p0,p1,p2=np.array(segment)
        d1=2*(1-u)*(p1-p0)+2*u*(p2-p1);d2=2*(p2-2*p1+p0)
        speed=np.linalg.norm(d1,axis=1)
        cross=d1[:,0]*d2[1]-d1[:,1]*d2[0]
        integral+=float(np.sum(weights*cross**2/speed**5));segments_count+=1
    reported=rows[identity]['J_kappa_per_m']
    delta=abs(integral-reported)
    max_abs=max(max_abs,delta);max_rel=max(max_rel,delta/max(1.,abs(integral)))
    assert delta/max(1.,abs(integral))<.002,(identity,integral,reported)
assert len(rows)==450 and len(paths)==390
result={'audited_successful_paths':len(paths),'audited_quadratic_segments':segments_count,
        'quadrature':'96-point Gauss-Legendre vs 301-point trapezoidal rule',
        'max_absolute_J_difference':max_abs,'max_scaled_J_difference':max_rel,'passed':True}
(OUT/'independent_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
