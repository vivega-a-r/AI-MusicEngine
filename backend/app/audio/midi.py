import zipfile
from pathlib import Path
from typing import Dict, List
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
from backend.app.composition.drums import NoteEvent

STEM_MIDI_CHANNELS = {
    "drums": 9,     # General MIDI Drum channel 10 (0-indexed 9)
    "bass": 0,      # Channel 1
    "harmony": 1,   # Channel 2
    "melody": 2,    # Channel 3
}

def export_stem_to_midi(
    note_events: List[NoteEvent],
    stem_name: str,
    bpm: int,
    output_path: Path
) -> None:
    """Exports a single stem's note events to a Standard MIDI file."""
    mid = MidiFile(type=0) # Single track
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Tempo meta-message
    tempo = mido.bpm2tempo(bpm)
    track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
    track.append(MetaMessage('track_name', name=stem_name.title(), time=0))
    
    channel = STEM_MIDI_CHANNELS.get(stem_name, 0)
    ticks_per_beat = mid.ticks_per_beat
    
    # Convert NoteEvents to NoteOn / NoteOff pairs with absolute tick times
    events: List[Dict] = []
    seconds_per_beat = 60.0 / bpm
    
    for note in note_events:
        start_beat = note.time_s / seconds_per_beat
        duration_beat = note.duration_s / seconds_per_beat
        end_beat = start_beat + duration_beat
        
        start_tick = int(start_beat * ticks_per_beat)
        end_tick = int(end_beat * ticks_per_beat)
        vel = int(min(127, max(1, note.velocity * 127)))
        
        events.append({'tick': start_tick, 'type': 'note_on', 'note': note.midi_note, 'vel': vel})
        events.append({'tick': end_tick, 'type': 'note_off', 'note': note.midi_note, 'vel': 0})
        
    # Sort events by tick time (note_off before note_on at same tick)
    events.sort(key=lambda e: (e['tick'], 0 if e['type'] == 'note_off' else 1))
    
    current_tick = 0
    for ev in events:
        delta = max(0, ev['tick'] - current_tick)
        current_tick = ev['tick']
        track.append(Message(ev['type'], note=ev['note'], velocity=ev['vel'], time=delta, channel=channel))
        
    output_path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(str(output_path))

def export_all_midi_files(
    stem_events: Dict[str, List[NoteEvent]],
    bpm: int,
    output_dir: Path
) -> Path:
    """Exports all stem MIDI files and packages them into a zip archive."""
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / "midi.zip"
    
    with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zip_file:
        for stem_name, notes in stem_events.items():
            midi_path = output_dir / f"{stem_name}.mid"
            export_stem_to_midi(notes, stem_name, bpm, midi_path)
            zip_file.write(str(midi_path), arcname=f"{stem_name}.mid")
            
    return zip_path
