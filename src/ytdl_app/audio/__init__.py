"""Audio editing functionality."""

from .editor import AudioEditor, get_audio_info
from .effects import EffectChain, EffectPreset
from .mixing import crossfade, duck, fade_in, fade_out, load_audio, overlay
from .processing import (
    concatenate_audio,
    convert_audio,
    extract_audio_from_video,
    remove_noise_gate,
    remove_noise_spectral,
    split_audio,
)

__all__ = [
    "AudioEditor",
    "EffectChain",
    "EffectPreset",
    "concatenate_audio",
    "convert_audio",
    "crossfade",
    "duck",
    "extract_audio_from_video",
    "fade_in",
    "fade_out",
    "get_audio_info",
    "load_audio",
    "overlay",
    "remove_noise_gate",
    "remove_noise_spectral",
    "split_audio",
]
