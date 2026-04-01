"""Export the VAE decoder directly to TF.js by rebuilding in TensorFlow.

Bypasses the problematic onnx-tf pipeline by manually constructing
an equivalent TF model and copying weights from PyTorch.
"""

import argparse
import os

import numpy as np
import torch
import tensorflow as tf
import tensorflowjs as tfjs

from models.vae import SunriseVAE


def build_tf_decoder():
    """Build TF decoder matching the PyTorch architecture exactly."""
    z_input = tf.keras.Input(shape=(2,), name="z")

    # decoder_fc
    x = tf.keras.layers.Dense(256, activation="relu", name="fc0")(z_input)
    x = tf.keras.layers.Dense(128 * 4 * 4, activation="relu", name="fc1")(x)

    # PyTorch reshapes to (128, 4, 4) channels-first, then convolutions expect that.
    # In TF we must match the memory layout: reshape as CHW then permute to HWC.
    x = tf.keras.layers.Reshape((128, 4, 4), name="reshape_chw")(x)
    x = tf.keras.layers.Permute((2, 3, 1), name="chw_to_hwc")(x)  # → (4, 4, 128)

    # decoder_conv (transposed convolutions)
    x = tf.keras.layers.Conv2DTranspose(
        64, 4, strides=2, padding="same", activation="relu", name="deconv0"
    )(x)  # → (8, 8, 64)
    x = tf.keras.layers.Conv2DTranspose(
        32, 4, strides=2, padding="same", activation="relu", name="deconv1"
    )(x)  # → (16, 16, 32)
    x = tf.keras.layers.Conv2DTranspose(
        3, 4, strides=2, padding="same", activation="sigmoid", name="deconv2"
    )(x)  # → (32, 32, 3)

    return tf.keras.Model(inputs=z_input, outputs=x, name="decoder")


def copy_weights(pt_vae: SunriseVAE, tf_model: tf.keras.Model):
    """Copy weights from PyTorch VAE decoder to TF model."""
    sd = pt_vae.state_dict()

    # FC layers: PyTorch Linear stores (out, in), TF Dense stores (in, out)
    fc_map = [
        ("fc0", "decoder_fc.0"),
        ("fc1", "decoder_fc.2"),
    ]
    for tf_name, pt_prefix in fc_map:
        layer = tf_model.get_layer(tf_name)
        w = sd[f"{pt_prefix}.weight"].numpy().T  # (out, in) → (in, out)
        b = sd[f"{pt_prefix}.bias"].numpy()
        layer.set_weights([w, b])

    # ConvTranspose layers: PyTorch stores (in_ch, out_ch, kH, kW)
    # TF Conv2DTranspose stores (kH, kW, out_ch, in_ch)
    conv_map = [
        ("deconv0", "decoder_conv.0"),
        ("deconv1", "decoder_conv.2"),
        ("deconv2", "decoder_conv.4"),
    ]
    for tf_name, pt_prefix in conv_map:
        layer = tf_model.get_layer(tf_name)
        # PyTorch: (in_ch, out_ch, kH, kW) → TF: (kH, kW, out_ch, in_ch)
        w_pt = sd[f"{pt_prefix}.weight"].numpy()
        w_tf = np.transpose(w_pt, (2, 3, 1, 0))
        b = sd[f"{pt_prefix}.bias"].numpy()
        layer.set_weights([w_tf, b])


def verify_outputs(pt_vae: SunriseVAE, tf_model: tf.keras.Model, n_tests: int = 50):
    """Verify TF model matches PyTorch decoder output."""
    torch.manual_seed(42)
    max_diffs = []

    for _ in range(n_tests):
        z_np = np.random.randn(1, 2).astype(np.float32)

        # PyTorch
        with torch.no_grad():
            pt_out = pt_vae.decode(torch.from_numpy(z_np))
            pt_out = pt_out.permute(0, 2, 3, 1).numpy()  # → (1, 32, 32, 3)

        # TF
        tf_out = tf_model.predict(z_np, verbose=0)

        diff = np.max(np.abs(pt_out - tf_out))
        max_diffs.append(diff)

    max_diffs = np.array(max_diffs)
    print(f"TF verification ({n_tests} tests):")
    print(f"  Max absolute diff: {max_diffs.max():.6f}")
    print(f"  Mean max diff:     {max_diffs.mean():.6f}")

    if max_diffs.max() < 0.01:
        print("PASS: TF model matches PyTorch.")
        return True
    else:
        print("FAIL: TF model differs too much!")
        return False


def quantize_to_float16(model_dir: str):
    """Post-process TF.js model: convert float32 weights to float16."""
    import json
    import struct

    model_json_path = os.path.join(model_dir, "model.json")
    with open(model_json_path) as f:
        model_json = json.load(f)

    for wg in model_json.get("weightsManifest", []):
        bin_filename = wg["paths"][0]
        bin_path = os.path.join(model_dir, bin_filename)

        with open(bin_path, "rb") as f:
            bin_data = f.read()

        new_chunks = []
        offset = 0
        for w in wg["weights"]:
            n_elements = 1
            for s in w["shape"]:
                n_elements *= s

            if w["dtype"] == "float32":
                n_bytes = n_elements * 4
                floats = struct.unpack(f"<{n_elements}f", bin_data[offset:offset + n_bytes])
                half_data = np.array(floats, dtype=np.float16).tobytes()
                new_chunks.append(half_data)
                w["dtype"] = "float16"
                offset += n_bytes
            elif w["dtype"] == "int32":
                n_bytes = n_elements * 4
                new_chunks.append(bin_data[offset:offset + n_bytes])
                offset += n_bytes
            else:
                n_bytes = n_elements * 4  # assume 4 bytes
                new_chunks.append(bin_data[offset:offset + n_bytes])
                offset += n_bytes

        new_bin = b"".join(new_chunks)
        with open(bin_path, "wb") as f:
            f.write(new_bin)

    with open(model_json_path, "w") as f:
        json.dump(model_json, f)

    print(f"Quantized weights to float16")


def main():
    parser = argparse.ArgumentParser(description="Export decoder to TF.js")
    parser.add_argument("--checkpoint", default="checkpoints/vae_final.pt")
    parser.add_argument("--output_dir", default="web/assets/model")
    args = parser.parse_args()

    # Load PyTorch model
    vae = SunriseVAE(latent_dim=2, img_size=32)
    state = torch.load(args.checkpoint, map_location="cpu", weights_only=True)
    vae.load_state_dict(state)
    vae.eval()

    # Build TF model and copy weights
    tf_model = build_tf_decoder()
    copy_weights(vae, tf_model)

    # Verify
    if not verify_outputs(vae, tf_model):
        raise SystemExit(1)

    # Export Keras model then manually quantize to float16
    os.makedirs(args.output_dir, exist_ok=True)
    tfjs.converters.save_keras_model(tf_model, args.output_dir)
    quantize_to_float16(args.output_dir)
    print(f"\nTF.js model saved to {args.output_dir}")

    # Report sizes
    total = 0
    for f in sorted(os.listdir(args.output_dir)):
        fpath = os.path.join(args.output_dir, f)
        sz = os.path.getsize(fpath)
        total += sz
        print(f"  {f}: {sz:,} bytes")
    print(f"  Total: {total:,} bytes ({total/1024:.1f} KB)")


if __name__ == "__main__":
    main()
