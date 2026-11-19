import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
df = pd.read_csv(sys.argv[1]); out = sys.argv[2]
nomes = {'bottle':'garrafa','bucket':'balde','pool':'piscina','tire':'pneu','watertank':'caixa d\'água','puddle':'poça'}
ordem = df.groupby('classe').area_rel_pct.median().sort_values().index
rng = np.random.default_rng(2026)
fig, ax = plt.subplots(figsize=(3.4, 2.5), dpi=300)
for i, c in enumerate(ordem):
    s = df[df.classe == c]
    for alt, mk in [(16, 'o'), (40, '^')]:
        v = s[(s.altitude_m >= 40) == (alt == 40)].area_rel_pct
        y = i + rng.uniform(-0.18, 0.18, len(v))
        cor = '#c2410c' if c == 'bottle' else '#6b7280'
        ax.scatter(v, y, s=10, marker=mk, facecolor='none' if alt == 40 else cor, edgecolor=cor, linewidth=0.7, zorder=3)
    med = s.area_rel_pct.median(); ax.plot([med, med], [i-0.32, i+0.32], color='black', lw=1.5, zorder=4)
ax.set_xscale('log'); ax.set_yticks(range(len(ordem)))
ax.set_yticklabels([f'{nomes[c]} (n={(df.classe==c).sum()})' for c in ordem], fontsize=7)
ax.set_xlabel('Área relativa (% do quadro, escala log)', fontsize=7)
ax.tick_params(axis='x', labelsize=7); ax.grid(axis='x', color='#e5e7eb', lw=0.5, zorder=0)
for s in ['top','right']: ax.spines[s].set_visible(False)
from matplotlib.lines import Line2D
h = [Line2D([],[],marker='o',ls='',color='#6b7280',ms=3.5,label='15–16 m'),
     Line2D([],[],marker='^',ls='',mfc='none',color='#6b7280',ms=3.5,label='40 m'),
     Line2D([],[],color='black',lw=1.5,label='mediana')]
ax.legend(handles=h, fontsize=6, frameon=False, loc='lower center', bbox_to_anchor=(0.45,1.0), ncol=3)
fig.tight_layout(); fig.savefig(out); print('ok')
