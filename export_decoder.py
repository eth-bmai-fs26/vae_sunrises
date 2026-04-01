"""Export the trained VAE decoder to ONNX and TensorFlow.js format.

Pipeline: PyTorch decoder → ONNX → TF SavedModel → TF.js (float16 quantized)
"""

import argparse
import os
import subprocess
import sys

import numpy as np
import torch
import torch.nn as nn

from models.vae import SunriseVAE


class DecoderWrapper(nn.Module):
    """Standalone decoder that takes z ∈ R² and outputs (H, W, C) in [0, 1]."""

    def __init__(self, vae: SunriseVAE):
        super().__init__()
        self.decoder_fc = vae.decoder_fc
        self.decoder_conv = vae.decoder_conv

    def forward(self, z):
        h = self.decoder_fc(z)
        h = h.view(-1, 128, 4, 4)
        out = self.decoder_conv(h)  # (B, 3, 32, 32)
        # Convert channels-first → channels-last for the browser
        out = out.permute(0, 2, 3, 1)  # (B, 32, 32, 3)
        return out


def export_onnx(checkpoint_path: str, onnx_path: str) -> DecoderWrapper:
    """Export decoder to ONNX format."""
    vae = SunriseVAE(latent_dim=2, img_size=32)
    state = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    vae.load_state_dict(state)
    vae.eval()

    decoder = DecoderWrapper(vae)
    decoder.eval()

    dummy_z = torch.randn(1, 2)
    torch.onnx.export(
        decoder,
        dummy_z,
        onnx_path,
        opset_version=17,
        input_names=["z"],
        output_names=["image"],
        dynamic_axes={"z": {0: "batch"}, "image": {0: "batch"}},
    )
    print(f"Exported ONNX model to {onnx_path}")
    return decoder


def convert_onnx_to_tfjs(onnx_path: str, output_dir: str):
    """Convert ONNX → TF SavedModel → TF.js with float16 quantization."""
    savedmodel_dir = onnx_path.replace(".onnx", "_savedmodel")

    # ONNX → SavedModel
    print("Converting ONNX → TF SavedModel...")
    subprocess.run(
        ["onnx-tf", "convert", "-i", onnx_path, "-o", savedmodel_dir],
        check=True,
    )

    # SavedModel → TF.js
    os.makedirs(output_dir, exist_ok=True)
    print("Converting SavedModel → TF.js (float16)...")
    subprocess.run(
        [
            "tensorflowjs_converter",
            "--input_format=tf_saved_model",
            "--output_format=tfjs_graph_model",
            "--quantize_float16",
            savedmodel_dir,
            output_dir,
        ],
        check=True,
    )
    print(f"TF.js model saved to {output_dir}")


def verify_onnx(decoder: DecoderWrapper, onnx_path: str):
    """Quick verification that ONNX output matches PyTorch output."""
    import onnxruntime as ort

    test_z = torch.randn(1, 2)

    # PyTorch reference
    with torch.no_grad():
        pt_out = decoder(test_z).numpy()

    # ONNX inference
    sess = ort.InferenceSession(onnx_path)
    ort_out = sess.run(None, {"z": test_z.numpy()})[0]

    max_diff = np.max(np.abs(pt_out - ort_out))
    print(f"ONNX verification: max abs diff = {max_diff:.6f}")
    if max_diff > 0.001:
        print("WARNING: ONNX output differs significantly from PyTorch!")
    else:
        print("ONNX output matches PyTorch output.")


def main():
    parser = argparse.ArgumentParser(description="Export VAE decoder to TF.js")
    parser.add_argument(
        "--checkpoint", default="checkpoints/vae_final.pt",
        help="Path to trained VAE checkpoint",
    )
    parser.add_argument(
        "--output_dir", default="web/assets/model",
        help="Output directory for TF.js model files",
    )
    args = parser.parse_args()

    onnx_path = "decoder.onnx"

    # Step 1: Export to ONNX
    decoder = export_onnx(args.checkpoint, onnx_path)

    # Step 2: Verify ONNX
    verify_onnx(decoder, onnx_path)

    # Step 3: Convert to TF.js
    try:
        convert_onnx_to_tfjs(onnx_path, args.output_dir)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"\nTF.js conversion failed: {e}")
        print("ONNX model is still available at:", onnx_path)
        print("You can manually convert with:")
        print(f"  onnx-tf convert -i {onnx_path} -o decoder_savedmodel")
        print(f"  tensorflowjs_converter --input_format=tf_saved_model "
              f"--output_format=tfjs_graph_model --quantize_float16 "
              f"decoder_savedmodel {args.output_dir}")
        sys.exit(1)

    # Verify output
    model_json = os.path.join(args.output_dir, "model.json")
    if os.path.exists(model_json):
        total_size = sum(
            os.path.getsize(os.path.join(args.output_dir, f))
            for f in os.listdir(args.output_dir)
        )
        print(f"\nOutput files in {args.output_dir}:")
        for f in sorted(os.listdir(args.output_dir)):
            fpath = os.path.join(args.output_dir, f)
            print(f"  {f}: {os.path.getsize(fpath):,} bytes")
        print(f"  Total: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    else:
        print("WARNING: model.json not found in output directory!")


if __name__ == "__main__":
    main()
