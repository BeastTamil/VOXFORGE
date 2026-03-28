"""Audio Format Converter tab."""

from __future__ import annotations

import tempfile
from pathlib import Path

import gradio as gr
from pydub import AudioSegment

SUPPORTED_OUTPUT_FORMATS = ["wav", "mp3", "flac", "ogg", "m4a"]

FORMAT_PARAMS: dict[str, dict] = {
    "mp3": {"format": "mp3", "bitrate": "192k"},
    "wav": {"format": "wav"},
    "flac": {"format": "flac"},
    "ogg": {"format": "ogg"},
    "m4a": {"format": "mp4", "codec": "aac"},
}


def convert_audio_files(
    files: list[str] | None,
    output_format: str,
    sample_rate: int,
    bitrate: str,
) -> tuple[list[str], str]:
    """
    Convert uploaded audio files to the selected output format.

    Parameters
    ----------
    files : list[str] | None
        Paths to uploaded audio files.
    output_format : str
        Target audio format.
    sample_rate : int
        Output sample rate in Hz.
    bitrate : str
        Output bitrate (used for lossy formats like mp3).

    Returns
    -------
    converted_files : list[str]
        Paths to converted audio files.
    status : str
        Status message.

    """
    if not files:
        return [], "No files uploaded."

    converted: list[str] = []
    errors: list[str] = []

    for file_path in files:
        try:
            audio = AudioSegment.from_file(file_path)
            if sample_rate:
                audio = audio.set_frame_rate(sample_rate)

            suffix = f".{output_format if output_format != 'm4a' else 'm4a'}"
            out_file = tempfile.NamedTemporaryFile(
                suffix=suffix,
                delete=False,
            )
            out_path = out_file.name
            out_file.close()

            params = dict(FORMAT_PARAMS.get(output_format, {"format": output_format}))
            if output_format == "mp3" and bitrate:
                params["bitrate"] = bitrate
            if output_format == "m4a":
                audio.export(out_path, format="mp4", codec="aac")
            else:
                audio.export(out_path, **params)

            converted.append(out_path)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{Path(file_path).name}: {e}")

    status_parts = [f"Converted {len(converted)} file(s) to {output_format.upper()}."]
    if errors:
        status_parts.append("Errors: " + "; ".join(errors))
    return converted, " ".join(status_parts)


def render() -> None:
    """Render Audio Format Converter tab."""
    with gr.Tab("Audio Format Converter"):
        gr.Markdown(
            "Upload one or more audio files and convert them to your desired format."
        )
        with gr.Row():
            with gr.Column():
                input_files = gr.File(
                    label="Input audio files",
                    file_count="multiple",
                    file_types=[
                        "audio",
                        ".wav",
                        ".mp3",
                        ".flac",
                        ".ogg",
                        ".m4a",
                        ".aac",
                        ".wma",
                        ".opus",
                        ".aiff",
                    ],
                )
                with gr.Row():
                    output_format = gr.Dropdown(
                        label="Output format",
                        choices=SUPPORTED_OUTPUT_FORMATS,
                        value="wav",
                    )
                    sample_rate = gr.Dropdown(
                        label="Sample rate (Hz)",
                        choices=[8000, 16000, 22050, 44100, 48000],
                        value=44100,
                    )
                bitrate = gr.Dropdown(
                    label="Bitrate (MP3 only)",
                    choices=["96k", "128k", "192k", "256k", "320k"],
                    value="192k",
                    visible=True,
                )
                output_format.change(
                    lambda fmt: gr.Dropdown(visible=(fmt == "mp3")),
                    inputs=output_format,
                    outputs=bitrate,
                )
                convert_btn = gr.Button("Convert", variant="primary")
                status_box = gr.Textbox(label="Status", interactive=False)

            with gr.Column():
                output_files = gr.File(
                    label="Download converted files",
                    file_count="multiple",
                    interactive=False,
                )

        convert_btn.click(
            convert_audio_files,
            inputs=[input_files, output_format, sample_rate, bitrate],
            outputs=[output_files, status_box],
        )
