"""Five-planner desktop benchmark for report section 3.4.
Run: python -B code/benchmark_ch3/benchmark_ch3.py
This is geometric path planning, not robot tracking or ESP32 measurements.
Existing educational four-neighbour demos and Chapter 4 data are unchanged.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import heapq
import itertools
import json
import math
import platform
import sys
import time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/benchmark_ch3'
ALGORITHMS = ['Dijkstra', 'A*', 'PRM', 'RRT*', 'APF']
CFG = {
    'measurement_environment': 'local Windows CPU; not Google Colab or ESP32',
    'world_m': [6.0, 4.0], 'grid_m': .10,
    'start_m': [.35, 1.95], 'goal_m': [5.65, 1.95],
    'body_disc_radius_m': .11, 'planning_margin_m': .15,
    'smoothing_margin_m': .10, 'corner_trim_m': .15,
    'bezier_samples': 301, 'clearance_sample_step_m': .002,
    'runs_per_map': 30, 'seed_base': 20261102,
    'planner_wall_limit_s': 2.0,
    'prm_samples': 500, 'prm_neighbors': 12,
    'rrtstar_iterations': 1500, 'rrtstar_step_m': .40,
    'rrtstar_goal_bias': .05, 'rrtstar_radius_gamma': 6.0,
    'apf_k_att': 1.0, 'apf_k_rep': .035,
    'apf_influence_m': .60, 'apf_step_m': .03,
    'apf_boundary_policy': 'hard boundary collision check; repulsive potential only for internal rectangles',
    'apf_max_steps': 3000, 'apf_stall_window': 100,
    'apf_stall_progress_m': .001, 'apf_goal_tolerance_m': .04,
    'rectangular_expansion': 'axis-aligned box inflated by disc radius + margin; conservative at corners',
    'timing': 'perf_counter_ns elapsed wall time; all attempts for planning; found paths for postprocessing; no I/O/plotting',
    'success': 'planner connects exact goal within elapsed-time cap and common smoothing passes clearance checks',
    'quality': 'mean and sample SD over final successful paths only; failed metrics remain null',
    'collision': 'closed inflated rectangles; exact segment/slab tests; conservative quadratic chord error bound',
    'smoothness': 'analytic quadratic derivatives; 301-point trapezoidal integral of kappa^2 * speed du',
    'repeat_policy': 'fixed maps/start-goal; deterministic repeats assess runtime, not independent environment reliability',
}
MAPS = {
    'open': [],
    'maze': [[1.7, 0., 1.9, 2.7], [3.9, 1.3, 4.1, 4.0]],
    'clutter': [[1.15,.4,1.65,1.0],[1.15,1.7,1.65,2.3],[1.15,3.,1.65,3.6],
                [2.7,0.,3.2,.8],[2.7,1.5,3.2,2.1],[2.7,2.8,3.2,4.],
                [4.25,.4,4.75,1.0],[4.25,1.7,4.75,2.3],[4.25,3.,4.75,3.6]],
}
NAMES = {'open':'Không vật cản', 'maze':'Mê cung tĩnh', 'clutter':'Nhiều vật cản'}

class World:
    def __init__(self, name, obstacles=None):
        self.name = name
        self.boxes = np.asarray(MAPS[name] if obstacles is None else obstacles,dtype=float).reshape(-1,4)
        self.boxlist = self.boxes.tolist()
        self.width, self.height = CFG['world_m']
        self.start, self.goal = np.array(CFG['start_m']), np.array(CFG['goal_m'])
        self.gap = CFG['body_disc_radius_m']+CFG['planning_margin_m']
        self.smooth_gap = CFG['body_disc_radius_m']+CFG['smoothing_margin_m']
    def free(self, p, gap=None):
        gap = self.gap if gap is None else gap
        x,y = p
        if x <= gap or y <= gap or x >= self.width-gap or y >= self.height-gap:
            return False
        return all(not (x0-gap <= x <= x1+gap and y0-gap <= y <= y1+gap)
                   for x0,y0,x1,y1 in self.boxlist)
    def edge_free(self, a, b, gap=None):
        gap = self.gap if gap is None else gap
        if not self.free(a,gap) or not self.free(b,gap):
            return False
        dx,dy = b[0]-a[0], b[1]-a[1]
        for x0,y0,x1,y1 in self.boxlist:
            lo,hi = 0.,1.
            for origin,direction,vmin,vmax in [(a[0],dx,x0-gap,x1+gap),(a[1],dy,y0-gap,y1+gap)]:
                if abs(direction)<1e-15:
                    if origin < vmin or origin > vmax:
                        lo,hi=1.,0.
                        break
                else:
                    t0,t1=(vmin-origin)/direction,(vmax-origin)/direction
                    lo,hi=max(lo,min(t0,t1)),min(hi,max(t0,t1))
                    if lo>hi:
                        break
            if lo<=hi:
                return False
        return True
    def polyline_free(self, p, gap):
        if len(p)<2:
            return False
        x,y=p[:,0],p[:,1]
        if np.any((x<=gap)|(y<=gap)|(x>=self.width-gap)|(y>=self.height-gap)):
            return False
        a,d=p[:-1],np.diff(p,axis=0)
        for x0,y0,x1,y1 in self.boxlist:
            lo=np.zeros(len(a)); hi=np.ones(len(a));possible=np.ones(len(a),dtype=bool)
            for axis,vmin,vmax in [(0,x0-gap,x1+gap),(1,y0-gap,y1+gap)]:
                moving=np.abs(d[:,axis])>1e-15
                possible &= moving | ((a[:,axis]>=vmin)&(a[:,axis]<=vmax))
                denom=np.where(moving,d[:,axis],1.)
                t0=(vmin-a[:,axis])/denom;t1=(vmax-a[:,axis])/denom
                lo=np.maximum(lo,np.where(moving,np.minimum(t0,t1),-np.inf))
                hi=np.minimum(hi,np.where(moving,np.maximum(t0,t1),np.inf))
            if np.any(possible & (lo<=hi)):
                return False
        return True
    def sample(self,rng):
        for _ in range(10000):
            p=rng.uniform([self.gap,self.gap],[self.width-self.gap,self.height-self.gap])
            if self.free(p):
                return p
        raise RuntimeError('Sampling failed')
    def clearance(self, points):
        x,y=points[:,0],points[:,1]
        c=np.minimum.reduce([x,y,self.width-x,self.height-y])
        for x0,y0,x1,y1 in self.boxlist:
            dx=np.maximum(np.maximum(x0-x,x-x1),0.)
            dy=np.maximum(np.maximum(y0-y,y-y1),0.)
            c=np.minimum(c,np.hypot(dx,dy))
        return float(np.min(c)-CFG['body_disc_radius_m'])

def length(path):
    return float(np.linalg.norm(np.diff(path,axis=0),axis=1).sum())

def unwind(parent,goal):
    path=[goal]
    while parent[path[-1]]>=0:
        path.append(int(parent[path[-1]]))
    return path[::-1]

def grid_search(world,rng,deadline,astar=False):
    h=CFG['grid_m'];nx,ny=round(world.width/h),round(world.height/h)
    def point(cell):return ((cell[0]+.5)*h,(cell[1]+.5)*h)
    start=tuple(np.floor(world.start/h).astype(int));goal=tuple(np.floor(world.goal/h).astype(int))
    # Rasterization is included in each timed call.
    free={(i,j) for i in range(nx) for j in range(ny) if world.free(point((i,j)))}
    moves=[(1,0),(0,-1),(0,1),(-1,0),(1,-1),(1,1),(-1,-1),(-1,1)]
    def heuristic(cell):
        if not astar:return 0.
        dx,dy=abs(cell[0]-goal[0]),abs(cell[1]-goal[1])
        return h*(max(dx,dy)+(math.sqrt(2)-1)*min(dx,dy))
    serial=itertools.count();dist={start:0.};parent={};closed=set()
    q=[(heuristic(start),heuristic(start),next(serial),0.,start)]
    while q:
        if time.perf_counter()>deadline:return None,{'reason':'time_limit'}
        _,_,_,cost,u=heapq.heappop(q)
        if u in closed or cost>dist[u]+1e-12:continue
        closed.add(u)
        if u==goal:
            route=[u]
            while route[-1]!=start:route.append(parent[route[-1]])
            return np.array([point(c) for c in route[::-1]]),{'expanded':len(closed),'graph_cost_m':cost}
        pa=point(u)
        for dx,dy in moves:
            v=(u[0]+dx,u[1]+dy)
            if v not in free or v in closed:continue
            if dx and dy and ((u[0]+dx,u[1]) not in free or (u[0],u[1]+dy) not in free):continue
            if not world.edge_free(pa,point(v)):continue
            candidate=cost+h*math.hypot(dx,dy)
            if candidate<dist.get(v,math.inf)-1e-12:
                dist[v]=candidate;parent[v]=u;hv=heuristic(v)
                heapq.heappush(q,(candidate+hv,hv,next(serial),candidate,v))
    return None,{'reason':'no_grid_path'}

def prm(world,rng,deadline):
    t0=time.perf_counter_ns()
    points=np.array([world.start,world.goal]+[world.sample(rng) for _ in range(CFG['prm_samples'])])
    ds=np.sum((points[:,None,:]-points[None,:,:])**2,axis=2)
    np.fill_diagonal(ds,np.inf)
    k=CFG['prm_neighbors'];near=np.argsort(ds,axis=1)[:,:k]
    adj=[[] for _ in points];checked=set()
    for i in range(len(points)):
        if time.perf_counter()>deadline:return None,{'reason':'time_limit'}
        for j in near[i]:
            j=int(j);pair=(min(i,j),max(i,j))
            if pair in checked:continue
            checked.add(pair)
            if world.edge_free(points[i],points[j]):
                w=math.sqrt(ds[i,j]);adj[i].append((j,w));adj[j].append((i,w))
    build=(time.perf_counter_ns()-t0)/1e6;tq=time.perf_counter_ns()
    costs=np.full(len(points),np.inf);costs[0]=0.;parent=np.full(len(points),-1);q=[(0.,0)]
    while q:
        if time.perf_counter()>deadline:return None,{'reason':'time_limit','build_ms':build}
        cost,i=heapq.heappop(q)
        if cost>costs[i]+1e-12:continue
        if i==1:
            return points[unwind(parent,1)],{'build_ms':build,'query_ms':(time.perf_counter_ns()-tq)/1e6,'samples':len(points)}
        for j,w in adj[i]:
            if cost+w<costs[j]-1e-12:
                costs[j]=cost+w;parent[j]=i;heapq.heappush(q,(cost+w,j))
    return None,{'reason':'disconnected_roadmap','build_ms':build,'query_ms':(time.perf_counter_ns()-tq)/1e6}

def rrtstar(world,rng,deadline):
    limit=CFG['rrtstar_iterations'];step=CFG['rrtstar_step_m']
    points=np.zeros((limit+1,2));points[0]=world.start
    parents=np.full(limit+1,-1);costs=np.full(limit+1,np.inf);costs[0]=0.
    children=[set() for _ in range(limit+1)]
    n=1;first_ms=None;t0=time.perf_counter_ns();goal_candidates=set()
    for iteration in range(limit):
        if time.perf_counter()>deadline:break
        sample=world.goal if rng.random()<CFG['rrtstar_goal_bias'] else world.sample(rng)
        delta=sample-points[:n];d2=np.sum(delta*delta,axis=1);nearest=int(np.argmin(d2));d=math.sqrt(d2[nearest])
        if d<1e-10:continue
        new=points[nearest]+(sample-points[nearest])*min(1.,step/d)
        if not world.edge_free(points[nearest],new):continue
        dists=np.linalg.norm(points[:n]-new,axis=1)
        radius=min(step,CFG['rrtstar_radius_gamma']*math.sqrt(math.log(max(2,n))/max(2,n)))
        neighbors=np.flatnonzero(dists<=radius)
        parent=nearest;best=costs[nearest]+dists[nearest]
        for j in neighbors:
            if costs[j]+dists[j]<best-1e-12 and world.edge_free(points[j],new):
                parent=int(j);best=costs[j]+dists[j]
        idx=n;points[idx]=new;parents[idx]=parent;costs[idx]=best;children[parent].add(idx);n+=1
        for j in neighbors:
            j=int(j)
            if j==parent:continue
            candidate=best+dists[j]
            if candidate<costs[j]-1e-12 and world.edge_free(new,points[j]):
                children[int(parents[j])].remove(j);parents[j]=idx;children[idx].add(j)
                diff=candidate-costs[j];stack=[j]
                while stack:
                    child=stack.pop();costs[child]+=diff;stack.extend(children[child])
        if np.linalg.norm(new-world.goal)<=step and world.edge_free(new,world.goal):
            goal_candidates.add(idx)
            if first_ms is None:first_ms=(time.perf_counter_ns()-t0)/1e6
    if not goal_candidates:return None,{'reason':'no_connection_in_budget','nodes':n}
    best=min(goal_candidates,key=lambda i:costs[i]+np.linalg.norm(points[i]-world.goal))
    route=points[unwind(parents,best)]
    if np.linalg.norm(route[-1]-world.goal)>1e-10:route=np.vstack((route,world.goal))
    return route,{'nodes':n,'iterations':iteration+1,'first_solution_ms':first_ms,'selection':'best goal connection at end of budget'}

def apf(world,rng,deadline):
    p=world.start.copy();route=[p.copy()];rho0=CFG['apf_influence_m']
    for iteration in range(CFG['apf_max_steps']):
        if time.perf_counter()>deadline:return None,{'reason':'time_limit'}
        dg=np.linalg.norm(p-world.goal)
        if dg<=CFG['apf_goal_tolerance_m'] and world.edge_free(p,world.goal):
            return np.vstack((route,world.goal)),{'steps':iteration+1}
        force=CFG['apf_k_att']*(world.goal-p)
        # Repulsion uses the same conservative inflated geometry as other planners.
        # Map boundary is a hard collision constraint; APF repulsion sums internal obstacles.
        surfaces=[]
        for x0,y0,x1,y1 in world.boxlist:
            closest=np.clip(p,[x0-world.gap,y0-world.gap],[x1+world.gap,y1+world.gap])
            d=p-closest;rho=np.linalg.norm(d)
            if rho>0:surfaces.append((rho,d/rho))
        for rho,normal in surfaces:
            if 0<rho<rho0:force+=CFG['apf_k_rep']*(1/rho-1/rho0)/rho**2*normal
        norm=np.linalg.norm(force)
        if norm<1e-10:return None,{'reason':'zero_force','steps':iteration+1}
        step=min(CFG['apf_step_m'],dg);accepted=False
        for _ in range(14):
            nxt=p+step*force/norm
            if world.edge_free(p,nxt):accepted=True;break
            step*=.5
        if not accepted:return None,{'reason':'blocked_step','steps':iteration+1}
        p=nxt;route.append(p.copy())
        window=CFG['apf_stall_window']
        if len(route)>window:
            older=np.linalg.norm(route[-window]-world.goal)
            if older-np.linalg.norm(p-world.goal)<CFG['apf_stall_progress_m']:
                return None,{'reason':'stagnation','steps':iteration+1}
    return None,{'reason':'step_limit'}

def segment_points(a,b):
    return np.linspace(a,b,max(2,int(np.ceil(np.linalg.norm(b-a)/CFG['clearance_sample_step_m']))+1))

def smooth(world,raw):
    keep=np.r_[True,np.linalg.norm(np.diff(raw,axis=0),axis=1)>1e-10];raw=raw[keep]
    short=[raw[0]];i=0
    while i<len(raw)-1:
        j=len(raw)-1
        while j>i and not world.edge_free(raw[i],raw[j]):j-=1
        if j==i:raise ValueError('shortcut_failed')
        short.append(raw[j]);i=j
    short=np.array(short);out=[short[0]];segments=[];jk=0.;kmax=0.
    us=np.linspace(0,1,CFG['bezier_samples']);u=us[:,None]
    for i in range(1,len(short)-1):
        a,b,c=short[i-1:i+2]
        trim=min(CFG['corner_trim_m'],.4*np.linalg.norm(b-a),.4*np.linalg.norm(c-b))
        for _ in range(14):
            p0=b-trim*(b-a)/np.linalg.norm(b-a);p2=b+trim*(c-b)/np.linalg.norm(c-b)
            curve=(1-u)**2*p0+2*(1-u)*u*b+u*u*p2
            # Uniform bound on maximum distance from quadratic to each sample chord.
            error=np.linalg.norm(p0-2*b+p2)/(4*(len(us)-1)**2)
            if world.polyline_free(curve,world.smooth_gap+error):break
            trim*=.5
        else:raise ValueError('bezier_clearance_failed')
        d1=2*(1-u)*(b-p0)+2*u*(p2-b);d2=2*(p2-2*b+p0)
        speed=np.linalg.norm(d1,axis=1)
        if speed.min()<1e-10:raise ValueError('nonregular_curve')
        cross=d1[:,0]*d2[1]-d1[:,1]*d2[0];curv=cross/speed**3
        jk+=float(np.trapezoid(curv*curv*speed,us));kmax=max(kmax,float(np.max(np.abs(curv))))
        out.extend(segment_points(np.array(out[-1]),p0)[1:]);out.extend(curve[1:])
        segments.append([p0.tolist(),b.tolist(),p2.tolist()])
    out.extend(segment_points(np.array(out[-1]),short[-1])[1:]);out=np.array(out)
    if not world.polyline_free(out,world.smooth_gap):raise ValueError('final_collision')
    return short,out,{'raw_length_m':length(raw),'smooth_length_m':length(out),'J_kappa_per_m':jk,
                     'max_curvature_per_m':kmax,'min_body_clearance_m':world.clearance(out)},segments

def call_planner(name,world,rng,deadline):
    if name=='Dijkstra':return grid_search(world,rng,deadline,False)
    if name=='A*':return grid_search(world,rng,deadline,True)
    return {'PRM':prm,'RRT*':rrtstar,'APF':apf}[name](world,rng,deadline)

def validate():
    # Collision cases include crossing with safe endpoints and boundary contact.
    w=World('open',[[2.,1.,3.,2.]])
    assert not w.edge_free(np.array([1.,1.5]),np.array([4.,1.5]))
    assert w.edge_free(np.array([1.,.5]),np.array([4.,.5]))
    assert not w.free([2.-w.gap,1.5])
    checks={}
    for name in MAPS:
        w=World(name);paths=[]
        for astar in [False,True]:
            p,info=grid_search(w,None,time.perf_counter()+20,astar)
            assert p is not None and w.polyline_free(p,w.gap)
            assert np.linalg.norm(p[0]-w.start)<1e-10 and np.linalg.norm(p[-1]-w.goal)<1e-10
            paths.append((p,info))
        assert abs(paths[0][1]['graph_cost_m']-paths[1][1]['graph_cost_m'])<1e-9
        _,p,metrics,_=smooth(w,paths[0][0])
        assert metrics['min_body_clearance_m']>=CFG['smoothing_margin_m']-1e-9
        checks[name]={'graph_cost_agrees_m':paths[0][1]['graph_cost_m'],'smooth_clearance_m':metrics['min_body_clearance_m']}
    assert abs(checks['open']['graph_cost_agrees_m']-5.3)<1e-9
    return checks

def stats(items,key):
    values=[float(x[key]) for x in items if x.get(key) is not None]
    return None if not values else {'n':len(values),'mean':float(np.mean(values)),
                                    'sample_sd':float(np.std(values,ddof=1)) if len(values)>1 else 0.}

def aggregate(rows):
    summary={}
    for mapname in MAPS:
        summary[mapname]={}
        for alg in ALGORITHMS:
            runs=[r for r in rows if r['map']==mapname and r['algorithm']==alg]
            ok=[r for r in runs if r['success']];found=[r for r in runs if r['planner_found']]
            reasons={}
            for r in runs:
                if not r['success']:reasons[r['reason']]=reasons.get(r['reason'],0)+1
            s={'trials':len(runs),'found':len(found),'successes':len(ok),'failure_reasons':reasons}
            for key in ['planning_ms','post_ms','raw_length_m','smooth_length_m','J_kappa_per_m','min_body_clearance_m','max_curvature_per_m','build_ms','query_ms','expanded']:
                subset=runs if key=='planning_ms' else found if key=='post_ms' else ok
                s[key]=stats(subset,key)
            summary[mapname][alg]=s
    return summary

def draw_outputs(rows,paths):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    def background(ax,mapname):
        w=World(mapname)
        for x0,y0,x1,y1 in w.boxlist:
            ax.add_patch(Rectangle((x0-w.gap,y0-w.gap),x1-x0+2*w.gap,y1-y0+2*w.gap,facecolor='.88',edgecolor='.7',lw=.4))
            ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,facecolor='.25'))
        ax.scatter(*w.start,s=25,c='black',marker='o',zorder=5);ax.scatter(*w.goal,s=32,c='black',marker='*',zorder=5)
        ax.text(w.start[0]-.12,w.start[1]+.16,'S',fontsize=9);ax.text(w.goal[0]+.04,w.goal[1]+.16,'G',fontsize=9)
        ax.set(xlim=(0,w.width),ylim=(0,w.height),xticks=range(7),yticks=range(5));ax.set_aspect('equal');ax.tick_params(labelsize=8)
    fig,axes=plt.subplots(1,3,figsize=(12,3.4))
    for ax,mapname in zip(axes,MAPS):
        background(ax,mapname);ax.set_title(NAMES[mapname]);ax.set_xlabel('x (m)')
    axes[0].set_ylabel('y (m)');fig.tight_layout()
    fig.savefig(ROOT/'LaRex/picture/Hinh3_8_Ban_do_so_sanh.png',dpi=260,facecolor='white');plt.close(fig)
    fig,axes=plt.subplots(5,3,figsize=(10.2,12.2))
    selection={}
    for j,mapname in enumerate(MAPS):
        for i,alg in enumerate(ALGORITHMS):
            ax=axes[i,j];background(ax,mapname)
            candidates=[r for r in rows if r['map']==mapname and r['algorithm']==alg and r['success']]
            if candidates:
                r=sorted(candidates,key=lambda r:r['smooth_length_m'])[len(candidates)//2]
                data=paths[r['id']];p=np.array(data['smooth']);raw=np.array(data['raw'])
                ax.plot(raw[:,0],raw[:,1],color='.6',ls='--',lw=.7)
                ax.plot(p[:,0],p[:,1],color='#155c81',lw=1.6)
                selection[mapname+' / '+alg]=r['id']
            else:
                ax.text(3.,.45,'Không có lượt đạt',ha='center',fontsize=9,color='#9b3026')
            if i==0:ax.set_title(NAMES[mapname],fontsize=11)
            if j==0:ax.set_ylabel(alg+'\ny (m)',fontsize=11)
            if i==4:ax.set_xlabel('x (m)')
    fig.tight_layout(h_pad=.9,w_pad=.9)
    fig.savefig(ROOT/'LaRex/picture/Hinh3_9_Duong_di_so_sanh.png',dpi=240,facecolor='white');plt.close(fig)
    return selection

def run():
    parser=argparse.ArgumentParser();parser.add_argument('--validate-only',action='store_true');args=parser.parse_args()
    checks=validate()
    if args.validate_only:
        print(json.dumps(checks,indent=2));return
    OUT.mkdir(parents=True,exist_ok=True)
    rows=[];paths={}
    # One unrecorded warm-up for each algorithm/map; same configuration, separate seed.
    for mapname in MAPS:
        w=World(mapname)
        for alg in ALGORITHMS:call_planner(alg,w,np.random.default_rng(0),time.perf_counter()+CFG['planner_wall_limit_s'])
        for run_no in range(CFG['runs_per_map']):
            seed=CFG['seed_base']+run_no
            order=list(np.random.default_rng(seed).permutation(ALGORITHMS))
            for position,alg in enumerate(order):
                identity=f'{mapname}_{ALGORITHMS.index(alg)}_{run_no+1:02d}'
                row={'id':identity,'map':mapname,'algorithm':alg,'run':run_no+1,'seed':seed,'order':position,
                     'success':False,'planner_found':False,'reason':'','post_ms':None,
                     'raw_length_m':None,'smooth_length_m':None,'J_kappa_per_m':None,'min_body_clearance_m':None,'max_curvature_per_m':None}
                t0=time.perf_counter_ns();p,info=call_planner(alg,w,np.random.default_rng(seed),time.perf_counter()+CFG['planner_wall_limit_s'])
                row['planning_ms']=(time.perf_counter_ns()-t0)/1e6;row.update(info)
                if p is not None:
                    assert w.polyline_free(p,w.gap)
                    assert np.linalg.norm(p[0]-w.start)<1e-9 and np.linalg.norm(p[-1]-w.goal)<1e-9
                    row['planner_found']=True;t1=time.perf_counter_ns()
                    try:
                        short,sm,metrics,segments=smooth(w,p)
                        row.update(metrics);row['success']=True;row['reason']='success'
                        # Dense path remains in CSV/JSON evidence; downsampled figure path preserves endpoints.
                        paths[identity]={'raw':p.tolist(),'shortcuts':short.tolist(),'smooth':sm.tolist(),'quadratic_controls':segments}
                    except ValueError as exc:row['reason']=str(exc)
                    row['post_ms']=(time.perf_counter_ns()-t1)/1e6
                rows.append(row)
            if (run_no+1)%10==0:print(f'{mapname}: {run_no+1}/{CFG["runs_per_map"]}',flush=True)
    summary=aggregate(rows)
    cfg=dict(CFG,maps=MAPS,software={'python':platform.python_version(),'numpy':np.__version__},
             platform={'system':platform.system(),'release':platform.release(),'machine':platform.machine(),'processor':platform.processor()},
             source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    for name,obj in [('config.json',cfg),('per_run_metrics.json',rows),('summary.json',summary),('paths.json',paths)]:
        (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with (OUT/'per_run_metrics.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(rows)
    # Independent aggregate verification from the emitted CSV, not just in-memory rows.
    with (OUT/'per_run_metrics.csv').open(encoding='utf-8-sig',newline='') as f:csvrows=list(csv.DictReader(f))
    for mapname in MAPS:
        for alg in ALGORITHMS:
            subset=[r for r in csvrows if r['map']==mapname and r['algorithm']==alg]
            ok=[r for r in subset if r['success']=='True']
            assert len(ok)==summary[mapname][alg]['successes']
            for key in ['planning_ms','smooth_length_m','J_kappa_per_m','min_body_clearance_m']:
                vals=[float(r[key]) for r in (subset if key=='planning_ms' else ok)]
                if vals:assert abs(np.mean(vals)-summary[mapname][alg][key]['mean'])<1e-9
    checks['csv_recomputed']=True;checks['all_raw_and_final_paths_collision_checked']=True
    checks['figure_selection']=draw_outputs(rows,paths)
    (OUT/'validation.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='sha256.json'}
    (OUT/'sha256.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
    print(json.dumps({m:{a:summary[m][a]['successes'] for a in ALGORITHMS} for m in MAPS},ensure_ascii=True),flush=True)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    run()
