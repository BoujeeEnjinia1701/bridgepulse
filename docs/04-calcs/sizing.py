"""BridgePulse sizing calculations, BRP-CAL-001 v0.6 (TRL 3).

Run from the repo root:  python docs/04-calcs/sizing.py
Prints every number quoted in docs/04-calcs/01-sizing.md. Each line carries a tag such as
[A3] that the note cites. Geometry comes from cad/src/model.py (PARAMS, derived and the part
solids), the parts cost from bom/bom.csv and the budget from project.yaml. The spectral
simulation in section B uses a fixed random seed, so the printed figures repeat exactly.
First-principles estimates for a paper proof of concept; not a substitute for tests.
"""
import csv
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import yaml
from scipy import optimize, signal, stats

warnings.simplefilter("ignore", optimize.OptimizeWarning)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cad" / "src"))
from model import PARAMS as P, derived, build_parts, volumes, lanyard_geometry, DENSITY  # noqa: E402

D = derived(P)
G = 9.80665
rows = []          # results table (section L)


def tag(t, text):
    print(f"[{t}] {text}")


def result(rid, name, value, target, status):
    rows.append((rid, name, value, target, status))


# ------------------------------------------------------------------ assumptions
E_STEEL = 210e9            # Pa
DE_DT = -3.0e-4            # 1/K, relative change of steel modulus with temperature (assumed)
RHO_TIMBER = 500.0         # kg/m3, deck
RAILS = 20.0               # kg/m, rails and posts
ZETA = 0.01                # modal damping ratio of the first vertical mode (assumed)
WALKER = 75.0              # kg
STEP_HZ = 2.0              # walking pace
IMPULSE = 2.0              # N s, effective heel-strike impulse on a mode above 10 Hz (assumed, order of magnitude)
WALK_V = 1.3               # m/s
ACC_ND = 22.5e-6           # g/sqrt(Hz), ADXL355 noise density
FS, NSEG, REC_S = 250.0, 16384, 600.0
GF, V_EXC, R_G = 2.0, 3.3, 350.0
ADC_NOISE = 0.15e-6        # V rms input-referred at 20 SPS, gain 128 (assumed; ADS1220 class, to confirm)
ADC_FS = V_EXC / 128       # V, +/- full scale at gain 128, ratiometric reference
V_RAIL, ETA_HUB, ETA_FN = 5.0, 0.85, 0.90
T_WARM, T_PROC = 20.0, 60.0  # s gauge warm-up before the record; s post-processing after it
FN_ALLOW = 100.0           # mW, FieldNode sensor allowance (FND-CAL-001 design value; 115 mW ceiling)

print("BridgePulse sizing, BRP-CAL-001 v0.6")
print(f"Geometry from cad/src/model.py: girders {P['girder']} mm at +/-{P['gy']:.0f} mm, bearing span {P['bearing_span']:.0f} mm")

# ------------------------------------------------------------------ A. Example bridge dynamics (R2, R3)
print("\nA. Example bridge dynamics")
d, bf, tf, tw = [x / 1000 for x in P["girder"]]
A = 2 * bf * tf + tw * (d - 2 * tf)
I = (bf * d ** 3 - (bf - tw) * (d - 2 * tf) ** 3) / 12
Wel = I / (d / 2)
tag("A1", f"One girder from the model's rectangles: A = {A * 1e4:.1f} cm2, I = {I * 1e8:,.0f} cm4, W = {Wel * 1e6:.0f} cm3 "
          f"(catalog IPE 360 with root fillets: 72.7 cm2, 16,270 cm4, 904 cm3)")
L = P["bearing_span"] / 1000
m_g = 2 * A * 7850
m_deck = P["deck"][0] / 1000 * P["deck"][1] / 1000 * RHO_TIMBER
m = m_g + m_deck + RAILS
EI = 2 * E_STEEL * I
tag("A2", f"Mass {m:.0f} kg/m (girders {m_g:.0f}, deck {m_deck:.1f}, rails {RAILS:.0f}); EI = {EI:.2e} N m2 for two girders")
f1 = math.pi / (2 * L ** 2) * math.sqrt(EI / m)
M_mod = m * L / 2
K_mod = M_mod * (2 * math.pi * f1) ** 2
tag("A3", f"First vertical mode f1 = {f1:.1f} Hz; second {4 * f1:.0f} Hz (outside the 60 Hz band); modal mass {M_mod:.0f} kg")
tag("A4", "f is proportional to the square root of stiffness: a 1 % drop in frequency is a 2.0 % loss of bending stiffness")
dT = 70.0
tag("A5", f"Steel modulus alone: {DE_DT / 2 * 100:.3f} %/K in frequency, {abs(DE_DT) / 2 * dT * 100:.2f} % over -20 to +50 degC; "
          "bearings, deck and surfacing effects are not computable on paper")
mass_cases = [("one walker at midspan", WALKER), ("one walker, averaged over the crossing", WALKER * 0.5),
              ("crowd of 1 person/m2 over the deck", 1.0 * L * P["deck"][1] / 1000 * WALKER * 0.5)]
for name, dm in mass_cases:
    tag("A6", f"Added modal mass, {name}: {dm:.0f} kg, frequency {100 * (math.sqrt(M_mod / (M_mod + dm)) - 1):+.1f} %")
tag("A7", f"For comparison, a road bridge with 20 t modal mass: one walker at midspan {100 * (math.sqrt(20000 / 20075) - 1):+.2f} %")

# ------------------------------------------------------------------ B. Excitation, noise and frequency precision (R1, R2)
print("\nB. Excitation, noise and frequency precision")
w1 = 2 * math.pi * f1
v0 = IMPULSE / M_mod
a0 = w1 * v0
tau = 1 / (ZETA * w1)
T = 1 / STEP_HZ
ms = a0 ** 2 / (2 * T) * (tau / 2) * (1 - math.exp(-2 * T / tau))
a_walk = math.sqrt(ms)
t_cross = L / WALK_V
tag("B1", f"Heel strike of {IMPULSE} N s: peak {a0 / G * 1000:.0f} mg, decay time constant {tau:.2f} s, "
          f"RMS {a_walk / G * 1000:.0f} mg while someone walks at midspan; a crossing takes {t_cross:.1f} s")
nbin = FS / NSEG
nseg = int((REC_S * FS - NSEG) // (NSEG // 2)) + 1
tag("B2", f"Bin width {nbin:.4f} Hz ({NSEG / FS:.1f} s segments), {nseg} averaged segments with 50 % overlap in {REC_S:.0f} s")
tag("B3", f"Noise in one bin {ACC_ND * math.sqrt(nbin) * 1e6:.1f} ug; over 0.5 to 62.5 Hz {ACC_ND * math.sqrt(62.0) * 1e6:.0f} ug rms")
bw = 2 * ZETA * f1
a_need = math.sqrt(10 * math.pi * ZETA * f1) * ACC_ND
tag("B4", f"Half-power bandwidth of the mode {bw:.2f} Hz = {bw / nbin:.0f} bins, so the bin width does not limit precision; "
          f"a 10 dB peak above noise needs about {a_need * 1e6:.0f} ug rms of modal response")

rng = np.random.default_rng(20260925)
wa = 2 * FS * math.tan(w1 / (2 * FS))       # prewarped so the digital resonance sits at f1
bz, az = signal.bilinear([2 * ZETA * wa, 0], [1, 2 * ZETA * wa, wa ** 2], FS)   # modal (band-pass) response
nsamp = int(REC_S * FS)
noise_sd = ACC_ND * math.sqrt(FS / 2)
sim = {}
def sdof_psd(f, logA, fn, z, logN):
    r = f / fn
    with np.errstate(over="ignore"):
        return np.log(np.exp(logA) * (2 * z * r) ** 2 / ((1 - r ** 2) ** 2 + (2 * z * r) ** 2) + np.exp(logN))


for lvl_ug in (10, 30, 100, 300, 1000):
    est, fit = [], []
    for _ in range(60):
        x = signal.lfilter(bz, az, rng.standard_normal(nsamp + 2000))[2000:]
        x *= lvl_ug * 1e-6 / x.std()
        x += noise_sd * rng.standard_normal(nsamp)
        f, pxx = signal.welch(x, FS, window="hann", nperseg=NSEG, noverlap=NSEG // 2)
        band = (f > 5) & (f < 60)
        fb, pb = f[band], np.log(pxx[band])
        k = int(np.argmax(pb))
        k = min(max(k, 1), len(pb) - 2)
        den = pb[k - 1] - 2 * pb[k] + pb[k + 1]
        off = 0.5 * (pb[k - 1] - pb[k + 1]) / den if den != 0 else 0.0
        fp = fb[k] + off * nbin
        est.append(fp)
        win = np.abs(fb - fp) < 1.5                      # SDOF fit to about 200 bins round the peak
        try:
            popt, _ = optimize.curve_fit(sdof_psd, fb[win], pb[win],
                                         p0=[pb[k], fp, 0.02, np.median(pb)], maxfev=4000)
            fit.append(popt[1])
        except RuntimeError:
            fit.append(np.nan)
    stats_ = []
    for arr in (np.array(est), np.array(fit)):
        ok = np.abs(arr / f1 - 1) < 0.02
        stats_.append((ok.mean(), 100 * np.std(arr[ok] / f1) if ok.sum() > 2 else float("nan")))
    sim[lvl_ug] = stats_[1]
    tag("B5", f"Modal response {lvl_ug:>4} ug rms: found in {100 * stats_[0][0]:.0f} % of 60 records; 1 sigma of the hourly estimate "
              f"{stats_[0][1]:.3f} % by peak picking, {stats_[1][1]:.3f} % by an SDOF curve fit")
good = [lv for lv, (fr, sd) in sim.items() if fr >= 0.95 and sd <= 0.2]
tag("B6", f"With the curve fit the instrument alone meets the R2 repeatability of 0.2 % from {min(good) if good else 'no'} ug rms of modal response; "
          f"one walker gives about {a_walk / G * 1e6:,.0f} ug rms while on the span")
tag("B6a", f"Theoretical floor for a random-excited mode, sqrt(zeta / (2 pi f T)): {100 * math.sqrt(ZETA / (2 * math.pi * f1 * REC_S)):.3f} %")

cross = 0.75 * 0.5 * np.array([WALKER]) / M_mod
sd_mass = 0.75 * 0.5 * (50 / math.sqrt(12)) / M_mod
tag("B7", f"Mass loading: an energy-weighted crossing lowers the estimate by {100 * cross[0]:.1f} %; walker mass spread "
          f"(50 to 100 kg) gives {100 * sd_mass:.2f} % per crossing")
for n in (1, 5, 20):
    tag("B8", f"Scatter from walker mass alone, ungated, with {n:>2} crossings during the 10 min record: {100 * sd_mass / math.sqrt(n):.2f} % (1 sigma)")
n_need = (sd_mass / 0.002) ** 2
tag("B9", f"Ungated, R2 (0.2 %) would need about {n_need:.0f} single crossings in every record, and fails whenever two people cross together "
          f"({100 * 0.75 * 0.5 * 2 * WALKER / M_mod:.1f} % bias)")

# Load gating (BRP-DDR-002, decision on review item 4): the hub drops the part of the record while a
# walker is on the span, found from the strain step, plus 0.25 s each side, tapers the gate edges over
# 0.1 s and fits the rest. The walker is simulated as a moving mass and a train of heel-strike impulses,
# both weighted by the mode shape, in a time-varying SDOF model stepped exactly at each sample.
AMB = 10e-6                 # g rms, ambient (wind) response with nobody on the span; quiet bridge (assumed)
GATE_PAD = 0.25             # s either side of the strain-detected crossing


def crossing(mass, rg, pad=6.0):
    dt = 1 / FS
    n_on = int(t_cross * FS)
    n = n_on + int(pad * FS)
    c = 2 * ZETA * w1 * M_mod
    q = v = 0.0
    acc = np.empty(n)
    every = int(FS / STEP_HZ)
    ph = int(rg.integers(every))
    for i in range(n):
        if i < n_on:
            phi = math.sin(math.pi * i / n_on)
            Mt = M_mod + mass * phi ** 2
            if (i + ph) % every == 0:
                v += IMPULSE * phi / Mt
        else:
            Mt = M_mod
        wn = math.sqrt(K_mod / Mt)
        z = c / (2 * Mt * wn)
        wd = wn * math.sqrt(1 - z * z)
        e = math.exp(-z * wn * dt)
        cs, sn = math.cos(wd * dt), math.sin(wd * dt)
        q, v = (e * (q * (cs + z * wn / wd * sn) + v / wd * sn),
                e * (v * (cs - z * wn / wd * sn) - q * wn * wn / wd * sn))
        acc[i] = -(c * v + K_mod * q) / Mt
    return acc, n_on


def fit_f(x):
    f, pxx = signal.welch(x, FS, window="hann", nperseg=NSEG, noverlap=NSEG // 2)
    band = (f > 5) & (f < 60)
    fb, pb = f[band], np.log(pxx[band] + 1e-30)
    k = int(np.argmax(pb))
    win = np.abs(fb - fb[k]) < 1.5
    try:
        popt, _ = optimize.curve_fit(sdof_psd, fb[win], pb[win], p0=[pb[k], fb[k], 0.02, np.median(pb)], maxfev=4000)
    except RuntimeError:
        return np.nan
    # acceptance rule in the hub: the fitted peak must stand 10 dB above the fitted noise floor and the
    # fitted damping must be plausible (0.2 to 5 %); otherwise the hour is reported as "no clear peak"
    if popt[0] - popt[3] < math.log(10) or not 0.002 <= abs(popt[2]) <= 0.05:
        return np.nan
    return popt[1]


rg = np.random.default_rng(20260926)
hann = np.hanning(int(0.1 * FS))
gated = {}
for ncross in (1, 5, 20):
    ug, gt, frac = [], [], []
    for _ in range(30):
        x = signal.lfilter(bz, az, rg.standard_normal(nsamp + 2000))[2000:]
        x *= AMB * G / x.std()
        gate = np.ones(nsamp)
        for s0 in rg.uniform(0, REC_S - 12, ncross):
            a, n_on = crossing(rg.uniform(50, 100), rg)
            i0 = int(s0 * FS)
            x[i0:i0 + len(a)] += a[:nsamp - i0]
            gate[max(i0 - int(GATE_PAD * FS), 0):min(i0 + n_on + int(GATE_PAD * FS), nsamp)] = 0
        x = x / G + noise_sd * rg.standard_normal(nsamp)
        taper = np.minimum(np.convolve(gate, hann / hann.sum(), "same"), gate)
        ug.append(fit_f(x))
        gt.append(fit_f(x * taper))
        frac.append(1 - gate.mean())
    ug, gt = 100 * (np.array(ug) / f1 - 1), 100 * (np.array(gt) / f1 - 1)
    gated[ncross] = (np.nanmean(gt), np.nanstd(gt))
    tag("B10", f"{ncross:>2} crossings in the record (30 simulated records, walkers 50 to 100 kg): ungated bias {np.nanmean(ug):+.2f} %, "
               f"scatter {np.nanstd(ug):.2f} %; gated bias {np.nanmean(gt):+.3f} %, scatter {np.nanstd(gt):.3f} % (1 sigma), "
               f"{100 * np.mean(~np.isnan(gt)):.0f} % of records accepted; {100 * np.mean(frac):.1f} % of the record gated out")
tag("B11", f"Gating keeps the free decay after each crossing at the unloaded frequency; with the ambient response at an assumed "
           f"{AMB * 1e6:.0f} ug an hour with nobody crossing gives no clear peak and is reported as missing, not as a shift")
worst_g = max(sd for _, sd in gated.values())
bias_span = max(b for b, _ in gated.values()) - min(b for b, _ in gated.values())
tag("B12", f"Gated: worst scatter {worst_g:.3f} % against the 0.2 % of R2; the bias moves by {bias_span:.3f} % between 1 and 20 crossings, "
           "so a change in traffic hardly moves the daily mean")
result("R2", "Track natural frequencies",
       f"Bin {nbin:.4f} Hz; instrument 1 sigma {sim[100][1]:.3f} % at 100 ug (curve fit); with load gating {worst_g:.3f} % or less "
       f"in simulation (1 to 20 crossings per record)",
       "Bin 0.02 Hz; 0.2 % (1 sigma) over a steady day", "At risk (met in simulation with gating; to be checked on recorded data)")
result("R1", "Measure bridge acceleration", "22.5 ug/sqrt(Hz), 3 axes, 250 Hz output, filter corner 62.5 Hz",
       "25 ug/sqrt(Hz); 0.5 to 60 Hz", "Met by design (datasheet)")

# ------------------------------------------------------------------ C. Change detection statistics (R3)
print("\nC. Change detection statistics")
z_fa = stats.norm.ppf(1 - 1 / 365)
z_det = stats.norm.ppf(0.90)
tag("C1", f"One false flag per year with a daily test: z = {z_fa:.2f}; 90 % detection: z = {z_det:.2f}")
need = {}
for k in (7, 14):
    for nb in (28, 365):
        s = 1.0 / ((z_fa + z_det) * math.sqrt(1 / k + 1 / nb))
        need[(k, nb)] = s
        tag("C2", f"{k:>2}-day mean against a {nb:>3}-day baseline: daily residual after temperature compensation must be {s:.2f} % or less")
tag("C3", f"Residual budget items: temperature reading error 0.5 K gives {abs(DE_DT) / 2 * 0.5 * 100:.4f} %; "
          f"walker mass scatter at 5 crossings/h, 24 h, gives {100 * sd_mass / math.sqrt(5 * 24):.2f} % per day but a 10 % change in the share of "
          f"hours with two people on the span at once shifts the daily mean by {100 * cross[0] * 0.1:.2f} %")
tag("C4", f"With load gating the traffic term falls to the {bias_span:.3f} % bias span of B12; temperature and the rest of the model "
          "must then take the remainder of the allowance")
result("R3", "Flag structural change",
       f"Works if the daily residual after compensation is {need[(14, 28)]:.2f} % or less (14 days, 4-week baseline)",
       "1 % within 14 days; 1 false flag per year", "Not verifiable at TRL 3")

# ------------------------------------------------------------------ D. Strain (R4)
print("\nD. Strain")
sens = V_EXC * GF / 4
tag("D1", f"Half-bridge (one active, one dummy), GF {GF}, {V_EXC} V: {sens:.2f} uV per ue")
res = ADC_NOISE / (sens * 1e-6)
tag("D2", f"ADC noise {ADC_NOISE * 1e6:.2f} uV rms: {res:.2f} ue rms per sample, {6.6 * res:.2f} ue peak to peak; "
          f"range +/-1000 ue is +/-{sens * 1000 / 1000:.2f} mV against +/-{ADC_FS * 1000:.1f} mV full scale")
w = 5e3 * P["deck"][1] / 1000
Mc = w * L ** 2 / 8 / 2
eps_c = Mc / Wel / E_STEEL
Pw = WALKER * G
Mw = Pw * L / 4 / 2
eps_w = Mw / Wel / E_STEEL
tag("D3", f"Crowd 5 kN/m2: {Mc / 1000:.1f} kN m per girder, {Mc / Wel / 1e6:.1f} MPa, {eps_c * 1e6:.0f} ue; "
          f"one {WALKER:.0f} kg walker at midspan shared by two girders: {eps_w * 1e6:.1f} ue")
y_dyn = a0 / w1 ** 2
eps_dyn = (math.pi / L) ** 2 * y_dyn * d / 2
tag("D4", f"Dynamic strain in the {f1:.0f} Hz mode at the {a0 / G * 1000:.0f} mg heel-strike peak: {y_dyn * 1e6:.0f} um, "
          f"{eps_dyn * 1e6:.2f} ue; sampled at 20 SPS it aliases to {abs(f1 - 20 * round(f1 / 20)):.1f} Hz but is below the resolution")
tag("D5", "Gauge-to-dummy thermal mismatch of 1 ue/K (assumed) with a 2 K difference between flange and coupon: 2 ue apparent strain")
p_g = (V_EXC / 2) ** 2 / R_G
tag("D6", f"Self-heating {p_g * 1000:.1f} mW per gauge; a 20 s warm-up precedes each record")
result("R4", "Measure strain", f"{res:.2f} ue rms resolution; +/-1000 ue uses {sens * 1e-6 * 1000 / ADC_FS * 100:.0f} % of full scale; drift unknown",
       "2 ue; +/-1000 ue; 5 ue/month drift", "Not verifiable at TRL 3 (drift); resolution and range met on paper")

# ------------------------------------------------------------------ E. Temperature (R5)
print("\nE. Temperature")
tag("E1", "TMP1826 class 1-Wire probe (WSON package): +/-0.3 degC from -40 to +105 degC, +/-0.2 degC from +10 to +45 degC (maker's page); "
          "the DS18B20 class probe of v0.1 was +/-0.5 degC only from -10 degC upward")
tag("E2", f"Effect on compensation: 0.5 K error moves the steel-modulus correction by {abs(DE_DT) / 2 * 0.5 * 100:.4f} %, negligible against 1 %")
tag("E3", "Verification: an ice-point check (0 degC) of both probes plus a comparison against a reference in CalRig above about 10 degC")
result("R5", "Measure temperature", "+/-0.3 degC from -40 to +105 degC on the datasheet; ice-point check", "+/-0.5 degC over -20 to +50 degC",
       "Met on paper (datasheet)")

# ------------------------------------------------------------------ F. Power (R6)
print("\nF. Power")
loads = {"Microcontroller at reduced clock": 33.0, "Accelerometer": 0.66, "24-bit ADC": 1.4,
         "Gauge excitation, two 700 ohm half-bridges": 2 * V_EXC ** 2 / (2 * R_G) * 1000,
         "Bridge completion resistors, 2 x 20 kohm": 2 * V_EXC ** 2 / 20e3 * 1000,
         "microSD writes (average)": 10.0, "RS-485 transceiver": 1.7}
for k, v in loads.items():
    tag("F1", f"{k}: {v:.1f} mW")
p_rec = sum(loads.values())
p_rec_port = p_rec / ETA_HUB
p_proc = (loads["Microcontroller at reduced clock"] + loads["microSD writes (average)"] + loads["RS-485 transceiver"]) / ETA_HUB
tag("F2", f"Recording: {p_rec:.1f} mW at 3.3 V, {p_rec_port:.1f} mW at the FieldNode port ({ETA_HUB:.0%} buck from the {V_RAIL:.0f} V rail)")
e_h = p_rec_port * (REC_S + T_WARM) + p_proc * T_PROC
p_avg = e_h / 3600
tag("F3", f"Per hour: {REC_S + T_WARM:.0f} s recording and {T_PROC:.0f} s processing, then the rail is switched off: "
          f"{e_h / 3600:.1f} mWh; average {p_avg:.1f} mW at the port, {p_avg / ETA_FN:.1f} mW from the FieldNode cell, "
          f"{p_avg * 24 / 1000:.2f} Wh per day")
tag("F4", f"Continuous recording would need {p_rec_port:.0f} mW; share of the {FN_ALLOW:.0f} mW FieldNode allowance used: {p_avg / FN_ALLOW:.0%}")
fft_flop = 2.5 * NSEG * math.log2(NSEG)
flops = fft_flop * nseg * 3
ram = NSEG * 4 + 3 * (NSEG // 2 + 1) * 4 + NSEG * 4
tag("F5", f"Processing: {flops / 1e6:.0f} Mflop of FFTs; at an assumed 1 Mflop/s software float about {flops / 1e6:.0f} s, "
          f"plus about 6 s to read the record back from the card; RAM {ram / 1024:.0f} kB of 264 kB (one axis at a time from the card)")
result("R6", "Stay within the FieldNode energy budget", f"{p_avg:.1f} mW average at the port", "30 mW", "Met on paper")

# ------------------------------------------------------------------ G. Data, storage and uplink (R7)
print("\nG. Data, storage and uplink")
raw_acc = REC_S * FS * 3 * 4
raw_str = REC_S * 20 * 2 * 4
raw_h = raw_acc + raw_str + 10 * 60 * 2 * 4
month = raw_h * 24 * 30.44
tag("G1", f"Raw per hour {raw_h / 1e6:.2f} MB (acceleration {raw_acc / 1e6:.2f} MB); per day {raw_h * 24 / 1e6:.0f} MB; "
          f"per month {month / 1e9:.2f} GB; a 32 GB card holds {32e9 * 0.97 / month:.0f} months")
tag("G2", f"Card wear: {month * 12 / 1e9:.1f} GB written per year, {month * 12 / 32e9:.2f} full-card writes")
fields = {"three mode frequencies, 1 mHz steps": 6, "three peak amplitudes": 6, "RMS acceleration, 3 axes": 6,
          "strain min, max, mean, 2 channels, 0.1 ue steps": 12, "two temperatures, 0.01 K steps": 4, "status": 2}
pl = sum(fields.values())
tag("G3", f"Hourly summary: {pl} bytes ({', '.join(f'{k} {v}' for k, v in fields.items())})")


def toa(pl_bytes, sf, bw=125e3, cr=1, preamble=8):
    ts = 2 ** sf / bw
    de = 1 if (sf >= 11 and bw == 125e3) else 0
    n = 8 + max(math.ceil((8 * pl_bytes - 4 * sf + 28 + 16) / (4 * (sf - 2 * de))) * (cr + 4), 0)
    return (preamble + 4.25) * ts + n * ts


for sf in (7, 9, 10, 11, 12):
    t = toa(pl + 13, sf)
    tag("G4", f"SF{sf}: {1000 * t:.0f} ms per uplink ({pl + 13} bytes on air), {24 * t:.1f} s per day at 24 uplinks")
limits = {"EU868 DR0 to DR2 (SF12 to SF10)": 51, "US915 DR0 (SF10)": 11, "US915 DR1 (SF9)": 53,
          "AS923 with dwell time, DR2 (SF10)": 11, "AS923 with dwell time, DR3 (SF9)": 53}
for k, v in limits.items():
    tag("G5", f"{k}: {v} bytes maximum; the {pl}-byte summary {'fits' if pl <= v else 'does not fit'}")
small = {"first frequency, 1 mHz steps": 2, "its peak amplitude": 2, "two strain means, 0.1 ue steps": 4,
         "steel temperature, 0.01 K steps": 2, "status incl. gated seconds": 1}
pl_s = sum(small.values())
tag("G6", f"Reduced summary for 11-byte data rates (BRP-DDR-002): {pl_s} bytes ({', '.join(f'{k} {v}' for k, v in small.items())}); "
          f"{1000 * toa(pl_s + 13, 10):.0f} ms at SF10; the hub picks it when FieldNode reports an 11-byte limit")
fits_all = all((pl if v >= pl else pl_s) <= v for v in limits.values())
result("R7", "Send and keep the data", f"{pl} bytes, or {pl_s} bytes where the limit is 11; {32e9 * 0.97 / month:.0f} months on 32 GB; "
       "fits every listed data rate", "48 bytes within regional limits; 12 months on site",
       "Met on paper (AS923 limit assumed)" if fits_all else "At risk")

# ------------------------------------------------------------------ H. Mounting, mass and clearance (R8, R9)
print("\nH. Mounting, mass and clearance")
V = volumes(P)
m_shell = V["hub_shell"] * DENSITY["al"]
m_hub = m_shell + 0.10
m_plate = V["plate"] * DENSITY["al"]
m_other = V["mount_al"] * DENSITY["al"] + V["mount_steel"] * DENSITY["steel"]
m_lan = V["lanyard"] * DENSITY["steel"]
m_gird = m_hub + m_plate + m_other + m_lan
tag("H1", f"Hub {m_hub:.2f} kg (die-cast shell {m_shell:.2f} kg, boards 0.10 kg assumed); plate {m_plate:.2f} kg; "
          f"foot blocks, jaws, packers, jack block, jack screw and fixings {m_other:.2f} kg "
          f"({V['mount_al'] * DENSITY['al']:.2f} kg aluminium, {V['mount_steel'] * DENSITY['steel']:.2f} kg steel); "
          f"lanyard girder clamp, pad eye and wire {m_lan:.2f} kg; "
          f"on the girder {m_gird:.2f} kg; FieldNode core 2.41 kg (FND-CAL-001)")
E_al = 69e9
b_, t_, Lp = P["plate_w"] / 1000, P["plate_t"] / 1000, D["plate_h"] / 1000
Ip = b_ * t_ ** 3 / 12
a_ = (D["hub_zc"] - D["plate_z0"]) / 1000
bb_ = Lp - a_
k_pin = 3 * E_al * Ip * Lp / (a_ ** 2 * bb_ ** 2)
k_fix = 3 * E_al * Ip * Lp ** 3 / (a_ ** 3 * bb_ ** 3)
m_eff = m_hub + 0.5 * m_plate
f_pin = math.sqrt(k_pin / m_eff) / (2 * math.pi)
f_fix = math.sqrt(k_fix / m_eff) / (2 * math.pi)
tag("H2", f"Plate {P['plate_w']:.0f} x {D['plate_h']:.0f} x {P['plate_t']:.0f} mm, hub {a_ * 1000:.0f} mm above its foot: "
          f"out-of-plane mode {f_pin:.0f} Hz (ends pinned) to {f_fix:.0f} Hz (ends fixed), target 120 Hz (twice the band)")
t2, b2, L2 = 0.006, 0.26, 0.19
k_cant = 3 * 193e9 * (b2 * t2 ** 3 / 12) / L2 ** 3
m2 = m_hub + 0.25 * 0.26 * 0.26 * 0.006 * 7950
f_cant = math.sqrt(k_cant / m2) / (2 * math.pi)
tag("H3", f"TRL 2 arrangement (6 mm stainless plate held only at the bottom flange, hub {L2 * 1000:.0f} mm up): {f_cant:.0f} Hz, inside the measured band")
tag("H4", "Retention: each foot block is clamped to the bottom flange by a steel jaw under the flange, a packer outside the tip and an "
          "M10 bolt; the jack screw bears on the top flange; the lanyard to an independent girder clamp is the second path")
# Lanyard and girder clamp rating (BRP-DEC-001, 2026-10-02). If the mount lets go, everything on the
# plate falls until the lanyard takes it up. Energy method for a mass dropped onto an elastic line:
# F = W (1 + sqrt(1 + 2 h k / W)), with k = E A / L for the wire.
LAN = lanyard_geometry(P)
SLACK = 0.025              # m, most slack allowed when the lanyard is fitted (fitting rule)
E_ROPE = 100e9             # Pa, effective modulus of 7 x 7 stainless wire rope (assumed)
A_ROPE = 0.53 * math.pi / 4 * (2 * P["lan_r"] / 1000) ** 2   # m2, metallic area, 7 x 7 fill factor 0.53 (assumed)
MBL_ROPE = 4.8e3           # N, minimum breaking load of 3 mm 7 x 7 stainless rope (typical catalogue value, assumed)
SF_CLAMP = 4.0             # maker's design factor between working load limit and ultimate load (typical)
m_fall = m_hub + m_plate + m_other
W_fall = m_fall * G
L_lan = LAN["length"] / 1000
k_lan = E_ROPE * A_ROPE / L_lan
F_pk = W_fall * (1 + math.sqrt(1 + 2 * SLACK * k_lan / W_fall))
DF = F_pk / W_fall
wll_need = F_pk / SF_CLAMP / G
tag("H4a", f"Lanyard: 3 mm 7 x 7 stainless wire, {LAN['length']:.0f} mm between the pad eye and the girder clamp eye "
           f"(straight run {LAN['run_len']:.0f} mm), clamp {LAN['clear_x']:.0f} mm clear of the foot clamps along the span; "
           f"falling mass {m_fall:.2f} kg ({W_fall:.0f} N), slack {SLACK * 1000:.0f} mm at most, wire stiffness {k_lan / 1e6:.2f} kN/mm")
tag("H4c", f"Peak lanyard load if the mount lets go: {F_pk / 1000:.2f} kN, a dynamic factor of {DF:.0f} on the {W_fall:.0f} N weight; "
           f"with the maker's usual {SF_CLAMP:.0f}:1 design factor the girder clamp needs a working load limit of {wll_need:.0f} kg or more "
           f"(specified: 100 kg or more); the wire's breaking load ({MBL_ROPE / 1000:.1f} kN, assumed) is {MBL_ROPE / F_pk:.1f} times the peak")
tag("H4b", f"Root fillets (IPE 360, {P['root_r']:.0f} mm): plate ends {P['fillet_gap']:.0f} mm from each flange; foot blocks chamfered "
           f"{P['foot'][3]:.0f} mm over the fillet; checked in cad/src/model.py --check")
shapes = build_parts(P)
soffit = P["g_z0"]
low = {k: soffit - s.bounding_box().min.Z for k, s in shapes.items()}
worst = max(low.values())
tag("H5", "Depth below the soffit: " + ", ".join(f"{k} {v:.0f} mm" for k, v in low.items() if v > 0)
          + f"; worst {worst:.0f} mm against 15 mm")
tag("H6", f"Hub front face {D['hub_inside_tip']:.0f} mm inside the flange tip line, so the hub is inside the girder outline")
q = 0.5 * 1.225 * 35 ** 2
F_enc = q * 1.3 * P["fn_enc"][0] * P["fn_enc"][2] / 1e6
F_pan = 52.2
M_post = F_pan * (D["fn_panel_cz"] - D["deck_top"]) / 1000 + F_enc * (D["fn_z0"] + P["fn_enc"][2] / 2 - D["deck_top"]) / 1000
s_, t3 = P["post"][0], P["post"][1]
W_post = (s_ ** 4 - (s_ - 2 * t3) ** 4) / 12 / (s_ / 2) * 1e-9
tag("H7", f"FieldNode on the post at 35 m/s: panel 52.2 N (FND-CAL-001), enclosure {F_enc:.0f} N; moment at deck level {M_post:.0f} N m; "
          f"stress in a {s_:.0f} x {t3:.0f} mm post {M_post / W_post / 1e6:.1f} MPa; a 1 kN load at the rail top would give "
          f"{1000 * P['post'][2] / 1000 / W_post / 1e6:.0f} MPa")
tag("H8", f"FieldNode V-blocks fit round poles, not a {s_:.0f} mm square post (diagonal {s_ * math.sqrt(2):.1f} mm); on the post the V-blocks "
          "are left off, the back plate bears on the post's flat face and longer bands go round the post and through the plate slots (BRP-DDR-004)")
result("R9", "Keep clear of what passes under and over", f"{worst:.0f} mm below the soffit; hub inside the flange outline",
       "15 mm; deck side only the FieldNode", "Met on paper")

# ------------------------------------------------------------------ I. Installation time (R8)
print("\nI. Installation time")
tasks = [("A+B", "Access, safety briefing, check lead test result from the earlier visit", 30),
         ("A", "Remove paint and prepare two gauge sites", 40), ("A", "Bond two active gauges and place two dummy coupons", 30),
         ("A", "Wire and coat both gauges, fit covers", 40), ("B", "Fit plate, jack screw, clamps, lanyard and hub", 30),
         ("B", "Fit FieldNode core on the post", 20), ("B", "Route and clip cables", 40),
         ("A+B", "Connect, test record, check the uplink", 20), ("A+B", "Photos, clean up", 10)]
crit = sum(t for who, _, t in tasks if who != "B")
b_only = sum(t for who, _, t in tasks if who == "B")
pm = sum(t * (2 if who == "A+B" else 1) for who, _, t in tasks)
tag("I1", f"Tasks {pm} person-minutes; critical path (fitter A on the gauges) {crit} min = {crit / 60:.1f} h; fitter B's own tasks {b_only} min; target 4 h")
result("R8", "Fit without harming the structure", f"No drilling or welding; {crit / 60:.1f} h estimate for two people",
       "No drilling; 4 h for two people", "Not verifiable at TRL 3 (time); fixing met by design")

# ------------------------------------------------------------------ J. Outdoor life (R10)
print("\nJ. Outdoor life")
tag("J1", "Ratings: hub IP67 and FieldNode IP65 by choice of part; ADXL355 -40 to +125 degC; RP2040 class -20 to +85 degC (assumed); "
          "industrial microSD -25 to +85 degC (assumed); FieldNode interior 58.7 to 73.3 degC on a 45 degC day without a shield (FND-CAL-001)")
result("R10", "Survive outdoors", "Hub in shade under the deck; FieldNode heat not met in its own repo; gauge coating life unknown",
       "IP67/IP65; -20 to +50 degC; 5 years", "At risk")
result("R11", "Protect privacy", "No camera or microphone in the BOM", "Structural readings only", "Met by design")
result("R13", "Present results responsibly", "Wording rule in the precis; not yet implemented", "No safety rating anywhere", "Met by design")

# ------------------------------------------------------------------ K. Cost (R12)
print("\nK. Cost")
bom = list(csv.DictReader((ROOT / "bom" / "bom.csv").open()))
tot, fn = 0.0, 0.0
for r in bom:
    c = float(r["qty"]) * float(r["unit_cost_usd"])
    tot += c
    if "FieldNode" in r["item"]:
        fn += c
budget = float(yaml.safe_load((ROOT / "project.yaml").read_text())["budget_usd"])
spec = tot - fn
tag("K1", f"BOM {len(bom)} lines, all priced: BridgePulse-specific ${spec:.2f} against ${budget:.0f} (margin ${budget - spec:.2f}, "
          f"{(budget - spec) / budget:.1%}); FieldNode core ${fn:.2f}; complete monitor ${tot:.2f}, ${tot - budget:.2f} over ${budget:.0f}")
result("R12", "Affordable", f"${spec:.2f} BridgePulse-specific (complete ${tot:.2f})", f"${budget:.0f} BridgePulse-specific parts",
       f"At risk ({(budget - spec) / budget:.1%} margin)" if budget - spec < 0.05 * budget and spec <= budget else ("Met on paper" if spec <= budget else "**Not met**"))

# ------------------------------------------------------------------ L. Results
print("\nL. Results against every requirement")
order = {f"R{i}": i for i in range(1, 14)}
for r in sorted(rows, key=lambda r: order[r[0]]):
    tag("L", " | ".join(r))
