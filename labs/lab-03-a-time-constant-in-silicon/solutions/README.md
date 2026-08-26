# One good answer — read this after yours passes

```
resistor   L = 176.3564 um at W = 1 um       ->  176.36 um^2   ( 56,322 ohm )
capacitor  s =  12.8230 um square            ->  164.43 um^2   (  337.3 fF  )
                                       total     340.79 um^2
tau = 20.0517 ns  (+0.26 %)
```

## Where 56,322 Ω comes from

You are minimising area subject to $RC = \tau$. Both areas are easy:

$$A_R \approx \frac{R}{317.22}\ \mu\mathrm{m}^2 \qquad
A_C \approx \frac{C[\text{fF}]}{2}\ \mu\mathrm{m}^2$$

— the first from Lab 01's Ω per micrometre of length at $W = 1$ µm, the second
because a MIM plate is 2 fF per µm² and $s^2$ *is* the area. Substituting
$C = \tau/R$:

$$A(R) = \frac{R}{317.22} + \frac{\tau \times 10^{15}}{2R}$$

Differentiate, set to zero, and the two terms come out **equal** at the
optimum. For $\tau = 20$ ns that lands at $R = 56{,}322\ \Omega$ and
$C = 355.1$ fF — 176.36 µm² of resistor against 173.21 µm² of capacitor, a
total of 349.6 µm² split within 2 % of evenly. (The split is not exactly 50/50
because the approximations above drop Lab 01's 378 Ω and Lab 02's fringe; put
those back and the balance shifts by a couple of square micrometres.)

The equal-split result is not a coincidence and it is not special to this
problem: whenever cost is $aR + b/R$, the minimum is where the two halves of
the bill are the same size. It is worth remembering, because it makes "which
one should I make bigger?" answerable by inspection.

## Why the answer above is 337.3 fF and not 355.1 fF

Because a 176 µm strip of poly is not just a resistance. `make rc` measured
what one weighs:

```
    fitting both strips: 0.1994 fF per um of 1 um-wide poly, plus 1.1870 fF of ends.
```

176.36 µm of it carries about **36 fF** to the substrate. For a uniformly
distributed RC line, half of that adds to the time constant, so the circuit is
running $R \times C_{\text{par}}/2 \approx 1.0$ ns long — 5 % — before you have
drawn the capacitor at all. Shrinking the intended capacitor from 355.1 fF to
337.3 fF pays for it, and costs 8.8 µm² rather than the 176 µm² you would spend
lengthening the resistor instead.

## The dead end this lab is really about

Keep going. Push the resistor higher and the capacitor smaller, and area
should keep falling — the optimum was shallow, after all. `make rc` already
shows you what happens instead:

```
G  ideal 1 Mohm + ideal 1 pF                          999.9950 ns
H  real 1 Mohm of xhigh poly + your 1 pF             1049.9550 ns
```

**Five percent long, from parasitic capacitance alone.** The strip that makes
the megohm is 472 µm of poly and carries 95 fF. Past a certain resistance the
resistor *is* the capacitor, the time constant stops obeying the product you
designed, and shrinking the intended capacitor no longer helps because the
parasitic is not going anywhere.

Now scale it up. A millisecond needs a thousand times this $RC$ — say 100 MΩ
and 10 pF. 100 MΩ of `res_xhigh_po` at 1 µm wide is **47,197 µm of poly**,
which is 4.7 **centimetres**, and by the number you measured it carries about
9.4 pF to the substrate all on its own. The resistor is now the same size as
the capacitor it was supposed to charge, and the circuit does not work at any
value.

**You cannot build a millisecond out of an RC on a chip.** This is not a
tuning problem, it is a wall. What chips actually do is count: a crystal or
ring oscillator makes a short, repeatable time, and a digital counter
multiplies it. That is why [DD103](https://uoftasic.com/dd103/)'s elevator
controller measures its door dwell in *clock ticks* and not with a capacitor —
and it is one of the cleanest examples anywhere of a digital solution to an
analog problem.

## What to argue about

- The area budget in `check_rc.py` counts the MIM plate as area. It sits on
  metal 3, above the transistors. Does it really cost you anything, and what
  would you have to know about the block to answer?
- `res_xhigh_po` would have made the resistor 6.7× smaller and moved the
  optimum. It also has a voltage coefficient (Lab 01's `solutions/README.md`).
  In an RC that is deliberately used as a signal filter, is that acceptable?
- The 8.66 % temperature span on a circuit made of a poly resistor and a MIM
  capacitor is almost entirely the resistor's. What would you have to do to
  build a time constant that did *not* drift — and is there anything on this
  chip that would let you?
