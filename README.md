# Guide to Creating JSON Sheet Music Files

## Overview
This guide explains how to create JSON files for the Python synthesizer script. The music is structured as a collection of tracks, where each track represents a different instrument or voice in the composition.

## Basic Structure
The JSON file supports both a simple tracks array and a more advanced sectional structure with metadata:

### Simple Structure
```json
{
  "tracks": [
    {
      "instrument": "piano",
      "notes": []
    },
    {
      "instrument": "bass",
      "notes": []
    }
  ]
}
```

### Advanced Structure with Sections
```json
{
  "metadata": {
    "loops": 4,        // Number of times to repeat the entire piece
    "tempo": 120       // Tempo in beats per minute
  },
  "sections": [
    {
      "name": "verse",     // Section identifier
      "repeat": true,      // Whether to repeat this section
      "tracks": [
        {
          "instrument": "piano",
          "notes": []
        }
      ]
    },
    {
      "name": "chorus",
      "repeat": false,
      "tracks": []
    }
  ]
}
```

## Available Instruments
The script supports these instrument types, each with specific characteristics:

### Melody Instruments
- `piano`: Complex timbre with harmonics
  - Best used for: Main melodies, complex musical phrases
  - Volume range: 0.6-0.7
  - Optimal octaves: 4-5

- `xylophone`: Bright, short sounds
  - Best used for: Counter-melodies, accents
  - Volume range: 0.5-0.7
  - Optimal octaves: 4-5

### Accompaniment Instruments
- `bass`: Deep, sustained tones (Electric bass sound)
  - Best used for: Bass lines, foundational harmony
  - Volume range: 0.3-0.5
  - Optimal octaves: 2-3

- `guitar`: Balanced string sound (Acoustic guitar sound)
  - Best used for: Chords, arpeggios
  - Volume range: 0.4-0.6
  - Optimal octaves: 3-4

### Percussion Instruments
- `bongos`: Resonant percussion
  - Best used for: Rhythmic patterns
  - Volume range: 0.3-0.4
  - Uses C2 for all notes

- `claves`: Short, sharp clicks
  - Best used for: Accent beats
  - Volume range: 0.3-0.4
  - Uses C2 for all notes

## Writing Notes

### Single Notes
Single notes are written as objects with these properties:
```json
{
  "pitch": "C4",
  "duration": 500,
  "volume": 0.7
}
```

Properties:
- `pitch`: Note name with octave (e.g., "C4", "F#3", "Bb3")
- `duration`: Length in milliseconds
- `volume`: Float between 0.0 and 1.0

### Chords
Chords are written as objects with a "type" field and an array of notes:
```json
{
  "type": "chord",
  "notes": [
    {"pitch": "C4", "duration": 1000, "volume": 0.6},
    {"pitch": "E4", "duration": 1000, "volume": 0.6},
    {"pitch": "G4", "duration": 1000, "volume": 0.6}
  ]
}
```

## Available Notes
The script supports these notes across different octaves:

### Lower Octave (2)
C2, D2, E2, F2, G2, A2, B2, Bb2, Eb2

### Bass Octave (3)
C3, D3, E3, F3, G3, A3, B3, Bb3, Eb3

### Middle Octave (4)
C4, D4, E4, F4, G4, A4, B4, Bb4, Eb4

### Higher Octave (5)
C5, D5, E5, F5, G5, A5, B5, Bb5, Eb5

## Example Patterns

### Basic Melody
```json
{
  "instrument": "piano",
  "notes": [
    {"pitch": "C4", "duration": 250, "volume": 0.7},
    {"pitch": "D4", "duration": 250, "volume": 0.7},
    {"pitch": "E4", "duration": 500, "volume": 0.7},
    {"pitch": "REST", "duration": 250, "volume": 0.0}
  ]
}
```

### Bass Line
```json
{
  "instrument": "bass",
  "notes": [
    {"pitch": "C3", "duration": 1000, "volume": 0.4},
    {"pitch": "G2", "duration": 1000, "volume": 0.4}
  ]
}
```

### Chord Progression
```json
{
  "instrument": "guitar",
  "notes": [
    {
      "type": "chord",
      "notes": [
        {"pitch": "C3", "duration": 1000, "volume": 0.5},
        {"pitch": "E3", "duration": 1000, "volume": 0.5},
        {"pitch": "G3", "duration": 1000, "volume": 0.5}
      ]
    },
    {
      "type": "chord",
      "notes": [
        {"pitch": "G3", "duration": 1000, "volume": 0.5},
        {"pitch": "B3", "duration": 1000, "volume": 0.5},
        {"pitch": "D4", "duration": 1000, "volume": 0.5}
      ]
    }
  ]
}
```

### Percussion Pattern
```json
{
  "instrument": "claves",
  "notes": [
    {"pitch": "C2", "duration": 250, "volume": 0.3},
    {"pitch": "REST", "duration": 250, "volume": 0.0}
  ]
}
```

## Best Practices

### Volume Balancing
1. Melody instruments (piano, xylophone): 0.6-0.7
2. Bass instruments: 0.3-0.5
3. Chord instruments: 0.4-0.6
4. Percussion: 0.3-0.4

### Timing Guidelines
1. Use standard durations:
   - Short notes: 250ms
   - Medium notes: 500ms
   - Long notes: 1000ms
2. Use "REST" notes for precise timing
3. Ensure all track durations align properly

### Structure Guidelines
1. Build distinct sections (verse, chorus, bridge)
2. Layer instruments gradually
3. Use consistent patterns within sections
4. Create contrast between sections

### Common Issues and Solutions
1. Overly loud bass: Keep bass volume below 0.5
2. Muddy mix: Space out note ranges between instruments
3. Timing issues: Ensure note durations sum equally across tracks
4. Harsh sound: Keep all volumes below 0.9

## Complete Example

```json
{
  "tracks": [
    {
      "instrument": "piano",
      "notes": [
        {"pitch": "C4", "duration": 500, "volume": 0.7},
        {"pitch": "E4", "duration": 500, "volume": 0.7},
        {"pitch": "G4", "duration": 500, "volume": 0.7},
        {"pitch": "REST", "duration": 500, "volume": 0.0}
      ]
    },
    {
      "instrument": "bass",
      "notes": [
        {"pitch": "C3", "duration": 1000, "volume": 0.4},
        {"pitch": "G2", "duration": 1000, "volume": 0.4}
      ]
    },
    {
      "instrument": "guitar",
      "notes": [
        {
          "type": "chord",
          "notes": [
            {"pitch": "C3", "duration": 2000, "volume": 0.5},
            {"pitch": "E3", "duration": 2000, "volume": 0.5},
            {"pitch": "G3", "duration": 2000, "volume": 0.5}
          ]
        }
      ]
    },
    {
      "instrument": "claves",
      "notes": [
        {"pitch": "C2", "duration": 250, "volume": 0.3},
        {"pitch": "REST", "duration": 250, "volume": 0.0},
        {"pitch": "C2", "duration": 250, "volume": 0.3},
        {"pitch": "REST", "duration": 250, "volume": 0.0}
      ]
    }
  ]
}
```

## Development Process
1. Start with a simple melody track
2. Add basic bass line
3. Layer in chords
4. Add percussion
5. Test and adjust volumes
6. Extend patterns for full composition
7. Fine-tune instrument balance

## Metadata and Section Properties

### Metadata Options
- `loops`: Number of times to repeat the entire composition (integer)
- `tempo`: Speed in beats per minute (integer, typically 60-180)

### Section Properties
- `name`: Section identifier (e.g., "verse", "chorus", "bridge")
- `repeat`: Boolean indicating whether to repeat the section
- `tracks`: Array of instrument tracks for this section

### Section Types
Common section names and their typical characteristics:
1. `verse`: Main narrative section
   - Usually simpler arrangement
   - Supports lyrical content
   - Often uses basic chord progressions

2. `chorus`: High-energy section
   - Fuller arrangement
   - More prominent melody
   - Often uses stronger chord progressions

3. `bridge`: Contrasting section
   - Different chord progression
   - Often introduces new melodic elements
   - Can modulate to different key

4. `intro`: Opening section
   - Gradually builds instruments
   - Sets up main themes
   - Often simplified arrangement

5. `outro`: Closing section
   - Gradually reduces instruments
   - May reprise main themes
   - Often includes fadeout effect

## Special Notes for LLM Assistance

### JSON Validation Requirements
1. Always verify these critical elements:
   - Every track must have both `instrument` and `notes` fields
   - Every note must have `pitch`, `duration`, and `volume`
   - Check that instrument names exactly match: "piano", "bass", "guitar", "xylophone", "bongos", "claves"
   - Ensure all pitches are valid (e.g., "C4", "G2", etc.)

### Common Error Prevention

1. When working with sections:
   - Verify that section names are unique
   - Check that metadata values are valid (positive integers)
   - Ensure all sections have complete track data
   - Validate timing across repeated sections

2. When using metadata:
   - `tempo` must be a positive integer (typically 60-180)
   - `loops` must be a positive integer
   - Both fields are required in metadata object
1. When modifying existing JSON:
   - Preserve all required fields
   - Maintain array brackets and nested structure
   - Keep track of comma placement
   - Ensure proper quotation marks around strings

2. Volume validation:
   - Must be between 0.0 and 1.0
   - Convert percentage inputs (e.g., 70%) to decimal (0.7)
   - Handle integer inputs by dividing by 100

3. Duration handling:
   - Always in milliseconds
   - Convert seconds to milliseconds (multiply by 1000)
   - Convert musical notation (e.g., quarter note at 120 BPM = 500ms)

### Response Formatting
1. When providing JSON examples:
   - Use proper indentation (2 or 4 spaces)
   - Include all required fields
   - Use consistent quotation marks (prefer double quotes)
   - End arrays and objects properly

2. When modifying user JSON:
   - Preserve their existing structure
   - Match their indentation style
   - Keep their comment style if present
   - Maintain their naming conventions

### Handling User Inputs
1. Musical notation conversion:
   - "Quarter note" → 500ms at default tempo
   - "Half note" → 1000ms at default tempo
   - "Whole note" → 2000ms at default tempo
   - "Eighth note" → 250ms at default tempo

2. Note name variations:
   - Convert "Sharp" to "#" (F sharp → F#)
   - Convert "Flat" to "b" (B flat → Bb)
   - Handle lowercase input (c4 → C4)

3. Instrument name variations:
   - "Electric bass" → "bass"
   - "Acoustic guitar" → "guitar"
   - "Percussion" → specify "bongos" or "claves"

### Template Generation
When asked to create a new piece, you can start with either a simple or advanced template:

#### Simple Template
```json
{
  "tracks": [
    {
      "instrument": "piano",
      "notes": [
        {"pitch": "C4", "duration": 500, "volume": 0.7}
      ]
    }
  ]
}
```

#### Advanced Template with Sections
```json
{
  "metadata": {
    "loops": 2,
    "tempo": 120
  },
  "sections": [
    {
      "name": "verse",
      "repeat": true,
      "tracks": [
        {
          "instrument": "piano",
          "notes": [
            {"pitch": "C4", "duration": 500, "volume": 0.7}
          ]
        }
      ]
    }
  ]
}
```

2. Then add layers following these steps:
   - Add melody track first
   - Add bass line for foundation
   - Add chords for harmony
   - Add percussion last
   - Verify timing alignment across tracks