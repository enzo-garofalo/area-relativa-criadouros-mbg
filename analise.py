"""Analise confirmatoria conforme protocolo (18/11/2026). Uso: python analise.py <pasta_xml> <pasta_saida>"""
import sys, os, xml.etree.ElementTree as ET
import numpy as np, pandas as pd
from scipy import stats

ALTITUDE = {'video02': 15, 'video06': 16, 'video09': 40, 'video12': 40}  # Passos et al., Tabela I
SEED, NBOOT, NPERM, N_MIN = 2026, 10_000, 10_000, 10
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)

rows = []
for f in sorted(os.listdir(src)):
    if not f.endswith('.xml'): continue
    vid = f[:-4]; r = ET.parse(os.path.join(src, f)).getroot()
    W = int(r.find('.//original_size/width').text); H = int(r.find('.//original_size/height').text)
    for t in r.findall('track'):
        b = [x for x in t.findall('box') if x.get('outside') == '0']
        if not b: continue
        w = np.array([float(x.get('xbr')) - float(x.get('xtl')) for x in b])
        h = np.array([float(x.get('ybr')) - float(x.get('ytl')) for x in b])
        rows.append(dict(video=vid, altitude_m=ALTITUDE[vid], track=int(t.get('id')), classe=t.get('label'),
                         n_frames=len(b), larg_px=np.median(w), alt_px=np.median(h), W=W, H=H,
                         area_rel_pct=100 * np.median(w * h) / (W * H)))
df = pd.DataFrame(rows); df['grupo'] = np.where(df.classe == 'bottle', 'garrafa', 'demais')
df['estrato'] = np.where(df.altitude_m >= 40, '40 m', '15-16 m')
df.to_csv(os.path.join(out, 'objetos.csv'), index=False)

print('== Objetos por video e classe'); print(pd.crosstab(df.video, df.classe, margins=True))
print('\n== Tracks curtos (< 10 frames):', (df.n_frames < 10).sum())

g40 = ((df.estrato == '40 m') & (df.grupo == 'garrafa')).sum()
print(f'\n== Regra da altitude: garrafas a 40 m = {g40} (N minimo = {N_MIN})')
estratos = ['40 m'] if g40 >= N_MIN else ['15-16 m', '40 m']
alpha = 0.05 if g40 >= N_MIN else 0.025
print('   -> analise:', 'so 40 m' if g40 >= N_MIN else 'estratificada, alfa = 0,025 por estrato')

def cliff(a, b):
    d = np.sign(a[:, None] - b[None, :]); return d.mean()

rng = np.random.default_rng(SEED)
for e in estratos:
    s = df[df.estrato == e]; a = s[s.grupo == 'garrafa'].area_rel_pct.values; b = s[s.grupo == 'demais'].area_rel_pct.values
    print(f'\n===== Estrato {e}: garrafa n={len(a)}, demais n={len(b)}')
    if len(a) == 0: print('   Sem garrafas: teste nao aplicavel.'); continue
    print(s.groupby('grupo').area_rel_pct.describe(percentiles=[.25, .5, .75]).round(4))
    obs = np.median(a) - np.median(b)
    alln = np.concatenate([a, b]); cnt = 0
    for _ in range(NPERM):
        p = rng.permutation(alln); cnt += (np.median(p[:len(a)]) - np.median(p[len(a):])) <= obs
    p_perm = (cnt + 1) / (NPERM + 1)
    u = stats.mannwhitneyu(a, b, alternative='less')
    d = cliff(a, b)
    bd, bm = [], []
    for _ in range(NBOOT):
        ra, rb = rng.choice(a, len(a)), rng.choice(b, len(b)); bd.append(cliff(ra, rb)); bm.append(np.median(ra) - np.median(rb))
    usa_alt = min(len(a), len(b)) < 10
    print(f'   Teste {"ALTERNATIVO (permutacao, n<10)" if usa_alt else "principal (Mann-Whitney)"} e o confirmatorio')
    print(f'   Dif. medianas (garrafa - demais) = {obs:.4f} p.p.; IC95% bootstrap [{np.percentile(bm,2.5):.4f}; {np.percentile(bm,97.5):.4f}]')
    print(f'   Permutacao unilateral: p = {p_perm:.5f}')
    print(f'   Mann-Whitney unilateral: U = {u.statistic:.0f}, p = {u.pvalue:.6f}')
    print(f'   Delta de Cliff = {d:.3f}; IC95% bootstrap [{np.percentile(bd,2.5):.4f}; {np.percentile(bd,97.5):.4f}]')
    pc = p_perm if usa_alt else u.pvalue
    print(f'   Decisao (alfa = {alpha}): {"rejeita H0" if pc < alpha else "nao rejeita H0"}')

print('\n===== EXPLORATORIO')
print('Kruskal-Wallis entre classes (todos os videos, excluindo classes com < 3 objetos):')
ok = df.classe.value_counts(); ok = ok[ok >= 3].index
kw = stats.kruskal(*[df[df.classe == c].area_rel_pct for c in ok]); print(f'   classes={list(ok)}, H = {kw.statistic:.2f}, p = {kw.pvalue:.2e}')
print(df.groupby('classe').area_rel_pct.median().sort_values().round(4))
bt = df[df.grupo == 'garrafa']
for wf, hf, nome in [(1536, 864, '1536x864'), (640, 640, '640x640 (premissa: esticado)')]:
    print(f'   Garrafa em {nome}: ~{np.median(bt.larg_px * wf / bt.W):.1f} x {np.median(bt.alt_px * hf / bt.H):.1f} px (mediana)')
