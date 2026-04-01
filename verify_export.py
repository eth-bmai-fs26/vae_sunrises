"""Verify the exported ONNX model matches the PyTorch decoder output."""

import argparse

import numpy as np
import onnxruntime as ort
import torch

from models.vae import SunriseVAE


def verify(checkpoint_path: str, onnx_path: str, n_tests: int = 100):
    """Compare ONNX and PyTorch decoder outputs on random z values."""
    # Load PyTorch model
    vae = SunriseVAE(latent_dim=2, img_size=32)
    state = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    vae.load_state_dict(state)
    vae.eval()

    # Load ONNX model
    sess = ort.InferenceSession(onnx_path)

    # Test on random z values
    torch.manual_seed(42)
    max_diffs = []

    for i in range(n_tests):
        z = torch.randn(1, 2)

        # PyTorch: decode and permute to channels-last
        with torch.no_grad():
            pt_out = vae.decode(z).permute(0, 2, 3, 1).numpy()

        # ONNX inference
        ort_out = sess.run(None, {"z": z.numpy()})[0]

        diff = np.max(np.abs(pt_out - ort_out))
        max_diffs.append(diff)

    max_diffs = np.array(max_diffs)
    print(f"Tested {n_tests} random z values:")
    print(f"  Max absolute difference: {max_diffs.max():.6f}")
    print(f"  Mean max difference:     {max_diffs.mean():.6f}")
    print(f"  Output range: [{pt_out.min():.3f}, {pt_out.max():.3f}]")

    if max_diffs.max() < 0.01:
        print("PASS: ONNX model matches PyTorch within tolerance.")
    else:
        print("FAIL: ONNX model output differs too much from PyTorch!")
        return False

    # Verify output is in [0, 1]
    z_test = torch.tensor([[0.0, 0.0]])
    ort_out = sess.run(None, {"z": z_test.numpy()})[0]
    if ort_out.min() >= 0.0 and ort_out.max() <= 1.0:
        print("PASS: Output values are in [0, 1].")
    else:
        print(f"FAIL: Output range [{ort_out.min():.3f}, {ort_out.max():.3f}] "
              "is outside [0, 1]!")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Verify ONNX export")
    parser.add_argument("--checkpoint", default="checkpoints/vae_final.pt")
    parser.add_argument("--onnx", default="decoder.onnx")
    parser.add_argument("--n_tests", type=int, default=100)
    args = parser.parse_args()

    success = verify(args.checkpoint, args.onnx, args.n_tests)
    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
