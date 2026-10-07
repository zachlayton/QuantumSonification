import soundfile as sf

from dsp.ir import make_transition_ir


def main():
    print("Quantum Material Workstation v0.1")
    print("--------------------------------")
    print("Generating transition-spectrum impulse response...")

    ir = make_transition_ir(
        sr=48000,
        ir_seconds=6.0,
        base_freq=30.0,
        field_z=(0.80, 1.20, 1.90, 2.70),
        coupling_xx=0.65,
        coupling_zz=0.25,
        coupling_dm=0.70,
        temperature="inf",
        t2=5.0,
        t2_freq_scaling=0.5,
    )

    filename = "qmat_transition_ir.wav"
    sf.write(filename, ir, 48000)

    print(f"Wrote {filename}")
    print("Done.")


if __name__ == "__main__":
    main()