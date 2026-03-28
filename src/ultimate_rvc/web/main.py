"""Web application for VoxForge."""

from __future__ import annotations

from typing import Annotated

import os
from pathlib import Path

import gradio as gr
import typer

from ultimate_rvc.common import AUDIO_DIR, MODELS_DIR, TEMP_DIR
from ultimate_rvc.core.generate.speech import get_edge_tts_voice_names
from ultimate_rvc.core.manage.config import get_config_names, load_config
from ultimate_rvc.core.manage.models import (
    get_custom_embedder_model_names,
    get_voice_model_names,
)
from ultimate_rvc.web.common import initialize_dropdowns
from ultimate_rvc.web.config.main import TotalConfig
from ultimate_rvc.web.tabs.convert.audio_format import render as render_convert_tab
from ultimate_rvc.web.tabs.generate.speech.multi_step_generation import (
    render as render_speech_multi_step_tab,
)
from ultimate_rvc.web.tabs.generate.speech.one_click_generation import (
    render as render_speech_one_click_tab,
)
from ultimate_rvc.web.tabs.manage.models import render as render_models_tab
from ultimate_rvc.web.tabs.manage.settings import render as render_settings_tab

config_name = os.environ.get("URVC_CONFIG")
total_config = load_config(config_name, TotalConfig) if config_name else TotalConfig()


def render_app() -> gr.Blocks:
    """Render the VoxForge web application."""
    css = """
    h1 { text-align: center; margin-top: 20px; margin-bottom: 20px; }
    #generate-tab-button { font-weight: bold !important;}
    #manage-tab-button { font-weight: bold !important;}
    #convert-tab-button { font-weight: bold !important;}
    #settings-tab-button { font-weight: bold !important;}
    """
    cache_delete_frequency = 86400
    cache_delete_cutoff = 86400

    with gr.Blocks(
        title="VoxForge",
        theme=gr.Theme.load(str(Path(__file__).parent / "config/theme.json")),
        css=css,
        delete_cache=(cache_delete_frequency, cache_delete_cutoff),
    ) as app:
        gr.HTML("<h1>VoxForge 🎤</h1>")
        for component_config in [
            total_config.speech.one_click.edge_tts_voice,
            total_config.speech.one_click.voice_model,
            total_config.speech.one_click.custom_embedder_model,
            total_config.speech.multi_step.edge_tts_voice,
            total_config.speech.multi_step.voice_model,
            total_config.speech.multi_step.custom_embedder_model,
            total_config.management.model.voices,
            total_config.management.model.embedders,
            total_config.management.settings.load_config_name,
            total_config.management.settings.delete_config_names,
        ]:
            component_config.instantiate()

        with gr.Tab("Generate", elem_id="generate-tab"):
            render_speech_one_click_tab(total_config)
            render_speech_multi_step_tab(total_config)
        with gr.Tab("Models", elem_id="manage-tab"):
            render_models_tab(total_config)
        with gr.Tab("Convert", elem_id="convert-tab"):
            render_convert_tab()
        with gr.Tab("Settings", elem_id="settings-tab"):
            render_settings_tab(total_config)

        app.load(
            _init_dropdowns,
            outputs=[
                total_config.speech.one_click.edge_tts_voice.instance,
                total_config.speech.multi_step.edge_tts_voice.instance,
                total_config.speech.one_click.voice_model.instance,
                total_config.speech.multi_step.voice_model.instance,
                total_config.management.model.voices.instance,
                total_config.speech.one_click.custom_embedder_model.instance,
                total_config.speech.multi_step.custom_embedder_model.instance,
                total_config.management.model.embedders.instance,
                total_config.management.settings.load_config_name.instance,
                total_config.management.settings.delete_config_names.instance,
            ],
            show_progress="hidden",
        )
    return app


def _init_dropdowns() -> list[gr.Dropdown]:
    """
    Initialize all dropdowns on page load.

    Each section is wrapped independently so that a failure in one
    (e.g. Edge TTS 503) does not prevent the others from populating.
    """
    try:
        edge_tts_models = initialize_dropdowns(
            get_edge_tts_voice_names,
            2,
            "en-US-ChristopherNeural",
            range(2),
        )
    except Exception:
        edge_tts_models = [gr.Dropdown(choices=[], value=None) for _ in range(2)]

    try:
        voice_models = initialize_dropdowns(
            get_voice_model_names,
            3,
            value_indices=range(2),
        )
    except Exception:
        voice_models = [gr.Dropdown(choices=[], value=None) for _ in range(3)]

    try:
        custom_embedder_models = initialize_dropdowns(
            get_custom_embedder_model_names,
            3,
            value_indices=range(2),
        )
    except Exception:
        custom_embedder_models = [
            gr.Dropdown(choices=[], value=None) for _ in range(3)
        ]

    try:
        configs = initialize_dropdowns(get_config_names, 2, value_indices=range(1))
    except Exception:
        configs = [gr.Dropdown(choices=[], value=None) for _ in range(2)]

    return [
        *edge_tts_models,
        *voice_models,
        *custom_embedder_models,
        *configs,
    ]


app = render_app()
app_wrapper = typer.Typer()


@app_wrapper.command()
def start_app(
    share: Annotated[
        bool,
        typer.Option("--share", "-s", help="Enable sharing"),
    ] = False,
    listen: Annotated[
        bool,
        typer.Option("--listen", "-l", help="Make reachable from local network."),
    ] = False,
    listen_host: Annotated[
        str | None,
        typer.Option("--listen-host", "-h", help="The hostname the server will use."),
    ] = None,
    listen_port: Annotated[
        int | None,
        typer.Option("--listen-port", "-p", help="The listening port."),
    ] = None,
    ssr_mode: Annotated[
        bool,
        typer.Option("--ssr-mode", help="Enable server-side rendering mode."),
    ] = False,
) -> None:
    """Run the VoxForge web application."""
    os.environ["GRADIO_TEMP_DIR"] = str(TEMP_DIR)
    gr.set_static_paths([MODELS_DIR, AUDIO_DIR])
    app.queue()
    app.launch(
        share=share,
        server_name=(None if not listen else (listen_host or "0.0.0.0")),  # noqa: S104
        server_port=listen_port,
        ssr_mode=ssr_mode,
    )


if __name__ == "__main__":
    app_wrapper()
