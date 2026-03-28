"""
Module defining models for representing configuration settings for
VoxForge UI tabs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from ultimate_rvc.web.config.component import (
    AnyComponentConfig,
    AudioConfig,
    CheckboxConfig,
    ComponentConfig,
    DropdownConfig,
)
from ultimate_rvc.web.config.tab import SpeechGenerationConfig

if TYPE_CHECKING:
    import gradio as gr


class SpeechIntermediateAudioConfig(BaseModel):
    """
    Configuration settings for intermediate audio components in the
    one-click speech generation tab.

    Attributes
    ----------
    speech : AudioConfig
        Configuration settings for the input speech audio component.
    converted_speech : AudioConfig
        Configuration settings for the converted speech audio component.

    """

    speech: AudioConfig = AudioConfig.intermediate(label="Speech")
    converted_speech: AudioConfig = AudioConfig.intermediate(
        label="Converted speech",
    )

    @property
    def all(self) -> list[gr.Audio]:
        """
        Retrieve instances of all intermediate audio components.

        Returns
        -------
        list[gr.Audio]
            List of instances of all intermediate audio components.

        """
        return [getattr(self, field).instance for field in self.__annotations__]


class OneClickSpeechGenerationConfig(SpeechGenerationConfig):
    """
    Configuration settings for one-click speech generation tab.

    Attributes
    ----------
    intermediate_audio : SpeechIntermediateAudioConfig
        Configuration settings for intermediate audio components.
    show_intermediate_audio : CheckboxConfig
        Configuration settings for a show intermediate audio checkbox
        component.

    See Also
    --------
    SpeechGenerationConfig
        Parent model defining common component configuration settings
        for speech generation tabs.

    """

    intermediate_audio: SpeechIntermediateAudioConfig = (
        SpeechIntermediateAudioConfig()
    )
    show_intermediate_audio: CheckboxConfig = CheckboxConfig(
        label="Show intermediate audio",
        info="Show intermediate audio tracks produced during speech generation.",
        value=False,
        exclude_value=True,
    )


class SpeechInputAudioConfig(BaseModel):
    """
    Configuration settings for input audio components in the multi-step
    speech generation tab.

    Attributes
    ----------
    speech : AudioConfig
        Configuration settings for the input speech audio component.
    converted_speech : AudioConfig
        Configuration settings for the converted speech audio component.

    """

    speech: AudioConfig = AudioConfig.input("Speech")
    converted_speech: AudioConfig = AudioConfig.input("Converted speech")

    @property
    def all(self) -> list[AudioConfig]:
        """
        Retrieve configuration settings for all input audio components.

        Returns
        -------
        list[AudioConfig]
            List of configuration settings for all input audio
            components in the multi-step speech generation tab.

        """
        return [getattr(self, field) for field in self.__annotations__]


class MultiStepSpeechGenerationConfig(SpeechGenerationConfig):
    """
    Configuration settings for the multi-step speech generation tab.

    Attributes
    ----------
    input_audio : SpeechInputAudioConfig
        Configuration settings for input audio components.

    See Also
    --------
    SpeechGenerationConfig
        Parent model defining common component configuration settings
        for speech generation tabs.

    """

    input_audio: SpeechInputAudioConfig = SpeechInputAudioConfig()


class ModelManagementConfig(BaseModel):
    """
    Configuration settings for model management tab.

    Attributes
    ----------
    voices : DropdownConfig
        Configuration settings for delete voice models dropdown
        component.
    embedders : DropdownConfig
        Configuration settings for delete embedder models dropdown
        component.
    dummy_checkbox : CheckboxConfig
        Configuration settings for a dummy checkbox component.

    """

    voices: DropdownConfig = DropdownConfig.multi_delete(
        label="Voice models",
        info="Select one or more voice models to delete.",
    )
    embedders: DropdownConfig = DropdownConfig.multi_delete(
        label="Custom embedder models",
        info="Select one or more embedder models to delete.",
    )
    dummy_checkbox: CheckboxConfig = CheckboxConfig(
        value=False,
        visible=False,
        exclude_value=True,
    )


class SettingsManagementConfig(BaseModel):
    """Configuration settings for settings management tab."""

    load_config_name: DropdownConfig = DropdownConfig(
        label="Configuration name",
        info="The name of a configuration to load UI settings from",
        value=None,
        render=False,
        exclude_value=True,
    )
    delete_config_names: DropdownConfig = DropdownConfig.multi_delete(
        label="Configuration names",
        info="Select the name of one or more configurations to delete",
    )
    dummy_checkbox: CheckboxConfig = CheckboxConfig(
        value=False,
        visible=False,
        exclude_value=True,
    )


class TotalSpeechGenerationConfig(BaseModel):
    """
    All configuration settings for speech generation tabs.

    Attributes
    ----------
    one_click : OneClickSpeechGenerationConfig
        Configuration settings for the one-click speech generation tab.
    multi_step : MultiStepSpeechGenerationConfig
        Configuration settings for the multi-step speech generation tab.

    """

    one_click: OneClickSpeechGenerationConfig = OneClickSpeechGenerationConfig()
    multi_step: MultiStepSpeechGenerationConfig = MultiStepSpeechGenerationConfig()


class TotalManagementConfig(BaseModel):
    """
    All configuration settings for management tabs.

    Attributes
    ----------
    model : ModelManagementConfig
        Configuration settings for the model management tab.
    settings : SettingsManagementConfig
        Configuration settings for the settings management tab.

    """

    model: ModelManagementConfig = ModelManagementConfig()
    settings: SettingsManagementConfig = SettingsManagementConfig()


class TotalConfig(BaseModel):
    """
    All configuration settings for the VoxForge app.

    Attributes
    ----------
    speech : TotalSpeechGenerationConfig
        Configuration settings for speech generation tabs.
    management : TotalManagementConfig
        Configuration settings for management tabs.

    """

    speech: TotalSpeechGenerationConfig = TotalSpeechGenerationConfig()
    management: TotalManagementConfig = TotalManagementConfig()

    @property
    def all(self) -> list[AnyComponentConfig]:
        """
        Recursively collect non-excluded, instantiated component
        configuration models nested within this instance.

        Returns
        -------
        list[AnyComponentConfig]
            A list of instantiated component configuration models whose
            values are not excluded.

        """

        def _collect(model: BaseModel) -> list[Any]:
            result: list[Any] = []
            for _, value in model:
                if isinstance(value, ComponentConfig):
                    if not value.exclude_value and value._instance is not None:
                        result.append(value)
                elif isinstance(value, BaseModel):
                    result.extend(_collect(value))
            return result

        return _collect(self)
