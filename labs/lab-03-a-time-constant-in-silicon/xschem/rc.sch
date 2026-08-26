v {xschem version=3.4.8 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {AD102 Lab 03  -  an RC you could fabricate} -300 -270 0 0 0.5 0.5 {}
T {No ideal components anywhere.  The resistor is 30.3315 um of high-sheet poly,
the capacitor is a 22.1965 um square of MiM.  Same circuit as part E of
spice/rc.spice, drawn.

Netlist & Simulate, then read tau off the meas line in the terminal.} -300 -235 0 0 0.3 0.3 {}
T {The symbol does the sheet-resistance
arithmetic for you and prints the answer:
R = (378.3 + 317.17 * L) / W  ohms.
Change L and watch the number move.} 400 -120 0 0 0.3 0.3 {layer=5}
T {W and L are PLAIN MICRONS.
L=30.3315 is thirty microns of poly.
Never L=30.3315u.} 400 60 0 0 0.3 0.3 {layer=5}
N -220 -30 -220 -60 { lab=in}
N -220 -60 0 -60 { lab=in}
N 0 -60 0 -30 { lab=in}
N -220 30 -220 60 { lab=0}
N 0 30 0 90 { lab=out}
N 0 90 0 130 { lab=out}
N -20 0 -60 0 { lab=0}
N -60 0 -60 60 { lab=0}
N 0 190 0 220 { lab=0}
C {sky130_fd_pr/res_high_po.sym} 0 0 0 0 {name=R1
W=1
L=30.3315
model=res_high_po
spiceprefix=X
mult=1
}
C {sky130_fd_pr/cap_mim_m3_1.sym} 0 160 0 0 {name=C1
W=22.1965
L=22.1965
model=cap_mim_m3_1
spiceprefix=X
mult=1
}
C {devices/vsource.sym} -220 0 0 0 {name=Vin value="PULSE(0 1.8 1n 10p 10p 200n 400n)"}
C {devices/gnd.sym} -220 60 0 0 {name=g1 lab=0}
C {devices/gnd.sym} -60 60 0 0 {name=g2 lab=0}
C {devices/gnd.sym} 0 220 0 0 {name=g3 lab=0}
C {devices/lab_pin.sym} -110 -60 0 0 {name=l_in lab=in}
C {devices/lab_pin.sym} 0 90 0 1 {name=l_out lab=out}
C {devices/code_shown.sym} -300 300 0 0 {name=MODELS only_toplevel=true value=".lib /foss/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice.tt.red tt"}
C {devices/code_shown.sym} -300 365 0 0 {name=CONTROL only_toplevel=true value="
.control
tran 2p 80n
meas tran t_real WHEN v(out)=1.137816 RISE=1
plot v(out)
.endc
"}
C {devices/launcher.sym} -300 240 0 0 {name=h1 descr="Netlist & Simulate"
tclcommand="xschem save; xschem netlist; xschem simulate"}
