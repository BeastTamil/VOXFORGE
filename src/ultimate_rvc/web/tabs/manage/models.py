"""Module which defines the code for the Models tab (upload only)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from functools import partial

import gradio as gr

from ultimate_rvc.core.manage.models import (
    delete_all_custom_embedder_models,
    delete_all_models,
    delete_all_voice_models,
    delete_custom_embedder_models,
    delete_voice_models,
    get_custom_embedder_model_names,
    get_voice_model_names,
    upload_custom_embedder_model,
    upload_voice_model,
)
from ultimate_rvc.web.common import (
    exception_harness,
    render_msg,
    setup_delete_event,
    update_dropdowns,
)
from ultimate_rvc.web.config.event import ManageModelEventState

if TYPE_CHECKING:
    from ultimate_rvc.web.config.main import ModelManagementConfig, TotalConfig


def render(total_config: TotalConfig) -> None:
    """Render Models tab."""
    tab_config = total_config.management.model
    tab_config.dummy_checkbox.instantiate()
    event_state = ManageModelEventState()

    _render_upload_tab(event_state)
    _render_delete_tab(tab_config, event_state)

    *_, all_model_update = [
        click_event.success(
            partial(update_dropdowns, get_voice_model_names, 3, [], [0, 1, 2]),
            outputs=[
                total_config.speech.one_click.voice_model.instance,
                total_config.speech.multi_step.voice_model.instance,
                tab_config.voices.instance,
            ],
            show_progress="hidden",
        )
        for click_event in [
            event_state.upload_voice_click.instance,
            event_state.delete_voice_click.instance,
            event_state.delete_all_voices_click.instance,
            event_state.delete_all_click.instance,
        ]
    ]

    for click_event in [
        event_state.upload_embedder_click.instance,
        event_state.delete_embedder_click.instance,
        event_state.delete_all_embedders_click.instance,
        all_model_update,
    ]:
        click_event.success(
            partial(update_dropdowns, get_custom_embedder_model_names, 3, [], [2]),
            outputs=[
                total_config.speech.one_click.custom_embedder_model.instance,
                total_config.speech.multi_step.custom_embedder_model.instance,
                tab_config.embedders.instance,
            ],
            show_progress="hidden",
        )


def _render_upload_tab(event_state: ManageModelEventState) -> None:
    with gr.Tab("Upload"):
        with gr.Accordion("Voice models", open=True):
            with gr.Accordion("HOW TO USE", open=False):
                gr.Markdown("")
                gr.Markdown(
                    "1. Find the .pth file for your RVC model and optionally a"
                    " .index file.",
                )
                gr.Markdown(
                    "2. Upload the files directly or compress to .zip and upload.",
                )
                gr.Markdown("3. Enter a unique name for the model.")
                gr.Markdown("4. Click 'Upload'.")

            with gr.Row():
                voice_model_files = gr.File(
                    label="Files",
                    file_count="multiple",
                    file_types=[".zip", ".pth", ".index"],
                )
                local_voice_model_name = gr.Textbox(label="Model name")

            with gr.Row(equal_height=True):
                upload_voice_btn = gr.Button("Upload", variant="primary", scale=19)
                upload_voice_msg = gr.Textbox(
                    label="Output message",
                    interactive=False,
                    scale=20,
                )
                event_state.upload_voice_click.instance = upload_voice_btn.click(
                    exception_harness(upload_voice_model),
                    inputs=[voice_model_files, local_voice_model_name],
                    outputs=upload_voice_msg,
                ).success(
                    partial(render_msg, "[+] Successfully uploaded voice model!"),
                    outputs=upload_voice_msg,
                    show_progress="hidden",
                )

        with gr.Accordion("Custom embedder models", open=False):
            with gr.Accordion("HOW TO USE", open=False):
                gr.Markdown("")
                gr.Markdown(
                    "1. Find the config.json and pytorch_model.bin for your"
                    " custom embedder model.",
                )
                gr.Markdown(
                    "2. Upload directly or compress to .zip and upload.",
                )
                gr.Markdown("3. Enter a unique name.")
                gr.Markdown("4. Click 'Upload'.")

            with gr.Row():
                embedder_files = gr.File(
                    label="Files",
                    file_count="multiple",
                    file_types=[".zip", ".json", ".bin"],
                )
                local_embedder_name = gr.Textbox(label="Model name")

            with gr.Row(equal_height=True):
                upload_embedder_btn = gr.Button("Upload", variant="primary", scale=19)
                upload_embedder_msg = gr.Textbox(
                    label="Output message",
                    interactive=False,
                    scale=20,
                )
                event_state.upload_embedder_click.instance = upload_embedder_btn.click(
                    exception_harness(upload_custom_embedder_model),
                    inputs=[embedder_files, local_embedder_name],
                    outputs=upload_embedder_msg,
                ).success(
                    partial(
                        render_msg,
                        "[+] Successfully uploaded custom embedder model!",
                    ),
                    outputs=upload_embedder_msg,
                    show_progress="hidden",
                )


def _render_delete_tab(
    tab_config: ModelManagementConfig,
    event_state: ManageModelEventState,
) -> None:
    with gr.Tab("Delete"):
        _render_voices_accordion(tab_config, event_state)
        _render_embedders_accordion(tab_config, event_state)
        _render_all_accordion(tab_config, event_state)


def _render_voices_accordion(
    tab_config: ModelManagementConfig,
    event_state: ManageModelEventState,
) -> None:
    with gr.Accordion("Voice models", open=False), gr.Row():
        with gr.Column():
            tab_config.voices.instance.render()
            delete_voice_btn = gr.Button("Delete selected", variant="secondary")
            delete_all_voice_btn = gr.Button("Delete all", variant="primary")
        with gr.Column():
            delete_voice_msg = gr.Textbox(label="Output message", interactive=False)

    event_state.delete_voice_click.instance = setup_delete_event(
        delete_voice_btn,
        delete_voice_models,
        [tab_config.dummy_checkbox.instance, tab_config.voices.instance],
        delete_voice_msg,
        "Are you sure you want to delete the selected voice models?",
        "[-] Successfully deleted selected voice models!",
    )
    event_state.delete_all_voices_click.instance = setup_delete_event(
        delete_all_voice_btn,
        delete_all_voice_models,
        [tab_config.dummy_checkbox.instance],
        delete_voice_msg,
        "Are you sure you want to delete all voice models?",
        "[-] Successfully deleted all voice models!",
    )


def _render_embedders_accordion(
    tab_config: ModelManagementConfig,
    event_state: ManageModelEventState,
) -> None:
    with gr.Accordion("Custom embedder models", open=False), gr.Row():
        with gr.Column():
            tab_config.embedders.instance.render()
            delete_embedder_btn = gr.Button("Delete selected", variant="secondary")
            delete_all_embedder_btn = gr.Button("Delete all", variant="primary")
        with gr.Column():
            delete_embedder_msg = gr.Textbox(
                label="Output message", interactive=False
            )

    event_state.delete_embedder_click.instance = setup_delete_event(
        delete_embedder_btn,
        delete_custom_embedder_models,
        [tab_config.dummy_checkbox.instance, tab_config.embedders.instance],
        delete_embedder_msg,
        "Are you sure you want to delete the selected custom embedder models?",
        "[-] Successfully deleted selected custom embedder models!",
    )
    event_state.delete_all_embedders_click.instance = setup_delete_event(
        delete_all_embedder_btn,
        delete_all_custom_embedder_models,
        [tab_config.dummy_checkbox.instance],
        delete_embedder_msg,
        "Are you sure you want to delete all custom embedder models?",
        "[-] Successfully deleted all custom embedder models!",
    )


def _render_all_accordion(
    tab_config: ModelManagementConfig,
    event_state: ManageModelEventState,
) -> None:
    with gr.Accordion("All models"), gr.Row(equal_height=True):
        delete_all_btn = gr.Button("Delete", variant="primary")
        delete_all_msg = gr.Textbox(label="Output message", interactive=False)

    event_state.delete_all_click.instance = setup_delete_event(
        delete_all_btn,
        delete_all_models,
        [tab_config.dummy_checkbox.instance],
        delete_all_msg,
        "Are you sure you want to delete all models?",
        "[-] Successfully deleted all models!",
    )
