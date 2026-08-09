# ENNEADS CUDA training handoff

## Prepared data

- Format: mono, 44.1 kHz, signed 16-bit PCM
- Sources: seven mastered mixes plus four distinct Track 05 stems
- Dataset: 1,410 windows, 69 minutes 47.8 seconds
- RAVE window size: 131,072 samples
- Architecture target: RAVE `v2`

The original masters are never modified. The duplicate Track 05 stem full mix
is intentionally excluded.

## GPU target

Use Linux with an NVIDIA GPU with at least 16 GB VRAM. A 24 GB RTX 3090 or 4090
provides useful headroom. The Mac's shared `music` environment is not used for
training.

## Clean environment

Create a dedicated Python 3.10 or 3.11 environment. Install a matching CUDA
build of Torch and TorchAudio first, following the selector at pytorch.org, then
install RAVE and FFmpeg:

```bash
python -m venv ~/venvs/enneads-rave
source ~/venvs/enneads-rave/bin/activate
python -m pip install --upgrade pip
# Install matching CUDA torch + torchaudio builds here.
python -m pip install acids-rave==2.3.1
sudo apt-get update
sudo apt-get install -y ffmpeg
```

Confirm that CUDA is available:

```bash
python -c 'import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))'
```

## Train

Upload this project directory to the GPU host, then run:

```bash
bash train_gpu.sh /absolute/path/to/enneads
```

Monitor validation audio and loss curves:

```bash
tensorboard --logdir /absolute/path/to/enneads/runs --bind_all
```

RAVE training has representation-learning and adversarial phases. Do not judge
the model only from early phase-one audio. Compare validation reconstructions
across checkpoints and retain multiple promising checkpoints.

## Export for Max/nn~

```bash
bash export_streaming.sh /absolute/path/to/enneads/runs/enneads_RUN_ID
```

The streaming flag is mandatory for cached real-time convolutions. Copy the
resulting `.ts` file to a Max search path and load it with:

```text
[nn~ enneads forward]
[nn~ enneads encode]
[nn~ enneads decode]
```

Training a latent prior is a separate follow-up stage after the reconstruction
quality of the base RAVE model is acceptable.

