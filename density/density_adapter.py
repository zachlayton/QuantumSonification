from sklearn import metrics


class DensityAdapter:
    def __init__(self, engine):
        self.engine = engine

    def apply_hamiltonian_state(self, h):
        if hasattr(self.engine, "set_param"):
            self.engine.set_param("x0", h.x)
            self.engine.set_param("y0", h.y)
            self.engine.set_param("z0", h.z)
        elif hasattr(self.engine, "params"):
            self.engine.params["x0"] = h.x
            self.engine.params["y0"] = h.y
            self.engine.params["z0"] = h.z

        return self.engine

    def step(self, dt):
        return self.engine.step(dt)

    def purity(self, rho):
        try:
            return float((rho @ rho).trace().real)
        except Exception:
            return 0.0

    def coherence_l1(self, rho):
        try:
            import mlx.core as mx

            off_diag = rho.copy()
            n = off_diag.shape[0]

            for i in range(n):
                off_diag[i, i] = 0.0

            return float(mx.sum(mx.abs(off_diag)))
        except Exception:
            return 0.0

    def metrics(self, rho):
        metrics = {}

        metrics["purity"] = self.purity(rho)
        metrics["coherence"] = self.coherence_l1(rho)

        if hasattr(self.engine, "von_neumann_entropy"):
            try:
                metrics["entropy"] = float(self.engine.von_neumann_entropy(rho))
            except TypeError:
                metrics["entropy"] = float(self.engine.von_neumann_entropy())
            except Exception:
                metrics["entropy"] = 0.0
        else:
            metrics["entropy"] = 0.0

        if hasattr(self.engine, "entanglement_metrics"):
            try:
                ent = self.engine.entanglement_metrics(rho)
            except TypeError:
                ent = self.engine.entanglement_metrics()
            except Exception:
                ent = {}

            if isinstance(ent, dict):
                for k, v in ent.items():
                    try:
                        metrics[k] = float(v)
                    except Exception:
                        metrics[k] = v

# ----------------------------------------------------
# Compute one scalar entanglement value
# ----------------------------------------------------

            if "bipartition_entropy" in ent:

                values = list(ent["bipartition_entropy"].values())

                metrics["entanglement"] = (
            sum(values) / len(values)
         )

            elif "mean_single_entropy" in ent:

                metrics["entanglement"] = ent["mean_single_entropy"]

            else:

                metrics["entanglement"] = 0.0

        circuit_state = getattr(self.engine, "circuit_state", {})
        if isinstance(circuit_state, dict):
            for key in (
                "entropy_spread",
                "entropy_centroid",
                "entropy_centroid_norm",
                "entropy_motion",
                "entropy_motion_mean",
                "entropy_motion_vector",
                "entropy_dominant_qubit",
            ):
                if key in circuit_state:
                    metrics[key] = circuit_state[key]
       

        if hasattr(self.engine, "local_bloch_vectors"):
            try:
                bloch = self.engine.local_bloch_vectors(rho)
            except TypeError:
                bloch = self.engine.local_bloch_vectors()
            except Exception:
                bloch = None

            if bloch is not None:
                try:
                    b0 = bloch[0]
                    metrics["bloch_x"] = float(b0[0])
                    metrics["bloch_y"] = float(b0[1])
                    metrics["bloch_z"] = float(b0[2])
                except Exception:
                    metrics["bloch_x"] = 0.0
                    metrics["bloch_y"] = 0.0
                    metrics["bloch_z"] = 0.0
            else:
                metrics["bloch_x"] = 0.0
                metrics["bloch_y"] = 0.0
                metrics["bloch_z"] = 0.0
        else:
            metrics["bloch_x"] = 0.0
            metrics["bloch_y"] = 0.0
            metrics["bloch_z"] = 0.0

        return metrics
