let sections = [];
let currentSectionNotes = {};

// Musical constants
const NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const OCTAVES = [2, 3, 4, 5];
const CHORD_PROGRESSIONS = [
    ['C', 'G', 'Am', 'F'],  // I-V-vi-IV
    ['Am', 'F', 'C', 'G'],  // vi-IV-I-V
    ['C', 'Am', 'F', 'G'],  // I-vi-IV-V
    ['F', 'G', 'Am', 'Em']  // IV-V-vi-iii
];

const GENRE_PRESETS = {
    pop: {
        tempos: [116, 120, 128],
        instruments: ['piano', 'synth', 'bass', 'guitar'],
        progressions: [
            ['C', 'G', 'Am', 'F'],  // I-V-vi-IV (most common pop progression)
            ['F', 'G', 'C', 'Am']   // IV-V-I-vi
        ],
        melodyNotes: 8,
        bassPattern: 'steady',
        repeatChorus: true
    },
    rock: {
        tempos: [128, 132, 138],
        instruments: ['guitar', 'bass', 'synth'],
        progressions: [
            ['Em', 'C', 'G', 'D'],  // Power chord progression
            ['Am', 'F', 'C', 'G']   // Minor rock progression
        ],
        melodyNotes: 6,
        bassPattern: 'driving',
        repeatChorus: true
    },
    jazz: {
        tempos: [92, 108, 116],
        instruments: ['piano', 'bass', 'synth'],
        progressions: [
            ['Cmaj7', 'Dm7', 'G7', 'Cmaj7'],  // ii-V-I progression
            ['Dm7', 'G7', 'Cmaj7', 'A7']      // Jazz standard progression
        ],
        melodyNotes: 12,
        bassPattern: 'walking',
        repeatChorus: false
    },
    electronic: {
        tempos: [128, 130, 140],
        instruments: ['synth', 'bass', 'synth'],
        progressions: [
            ['Cm', 'Ab', 'Eb', 'Bb'],  // Electronic progression
            ['Gm', 'Bb', 'Dm', 'F']    // Minor electronic progression
        ],
        melodyNotes: 16,
        bassPattern: 'arpeggio',
        repeatChorus: true
    },
    classical: {
        tempos: [88, 96, 108],
        instruments: ['piano', 'synth', 'piano'],
        progressions: [
            ['C', 'G', 'Dm', 'Em'],    // Classical progression
            ['Am', 'Dm', 'G', 'C']     // Minor classical progression
        ],
        melodyNotes: 10,
        bassPattern: 'alberti',
        repeatChorus: false
    },
    hiphop: {
        tempos: [85, 90, 95],
        instruments: ['synth', 'bass', 'piano'],
        progressions: [
            ['Cm', 'Ab', 'Bb', 'Gm'],  // Hip hop progression
            ['Dm', 'Am', 'Bb', 'C']    // Minor hip hop progression
        ],
        melodyNotes: 4,
        bassPattern: 'trap',
        repeatChorus: true
    },
    ambient: {
        tempos: [70, 80, 85],
        instruments: ['synth', 'synth', 'synth'],
        progressions: [
            ['Cmaj7', 'Am7', 'Fmaj7', 'G7'],  // Ambient progression
            ['Em7', 'Cmaj7', 'G', 'D']        // Ethereal progression
        ],
        melodyNotes: 6,
        bassPattern: 'drone',
        repeatChorus: false
    },
    funk: {
        tempos: [96, 104, 108],
        instruments: ['guitar', 'bass', 'synth'],
        progressions: [
            ['E9', 'G9', 'A9', 'B9'],  // Funk progression
            ['Dm7', 'G7', 'Em7', 'A7'] // Funk groove progression
        ],
        melodyNotes: 8,
        bassPattern: 'slap',
        repeatChorus: true
    }
};

// Musical utility functions
function generateBassPattern(pattern, rootNote, duration) {
    const patterns = {
        steady: () => [{
            pitch: rootNote,
            duration: duration * 4,
            volume: 0.8
        }],
        driving: () => [
            { pitch: rootNote, duration: duration, volume: 0.9 },
            { pitch: rootNote, duration: duration, volume: 0.7 },
            { pitch: rootNote, duration: duration, volume: 0.8 },
            { pitch: rootNote, duration: duration, volume: 0.7 }
        ],
        walking: () => {
            const scale = generateScale(rootNote, 'major');
            return scale.slice(0, 4).map(note => ({
                pitch: note,
                duration: duration,
                volume: 0.8
            }));
        },
        trap: () => [
            { pitch: rootNote, duration: duration * 2, volume: 0.9 },
            { pitch: shiftPitch(rootNote, -12), duration: duration * 2, volume: 0.8 }
        ],
        drone: () => [{
            pitch: rootNote,
            duration: duration * 8,
            volume: 0.6
        }],
        slap: () => [
            { pitch: rootNote, duration: duration / 2, volume: 0.9 },
            { pitch: shiftPitch(rootNote, 12), duration: duration / 2, volume: 0.7 },
            { pitch: rootNote, duration: duration / 2, volume: 0.8 },
            { pitch: shiftPitch(rootNote, 7), duration: duration / 2, volume: 0.7 }
        ]
    };
    
    return (patterns[pattern] || patterns.steady)();
}

function shiftPitch(note, semitones) {
    const pitch = note.replace(/\d/g, '');
    const octave = parseInt(note.match(/\d/g)[0]);
    const noteIndex = NOTES.indexOf(pitch);
    const newIndex = (noteIndex + semitones) % 12;
    const octaveShift = Math.floor((noteIndex + semitones) / 12);
    return `${NOTES[newIndex]}${octave + octaveShift}`;
}

function generateChord(root, type = 'major') {
    const noteIndex = NOTES.indexOf(root.replace(/\d/g, ''));
    const octave = parseInt(root.match(/\d/g)[0]);
    
    let intervals;
    switch(type) {
        case 'major': intervals = [0, 4, 7]; break;
        case 'minor': intervals = [0, 3, 7]; break;
        case '7th': intervals = [0, 4, 7, 10]; break;
        case 'maj7': intervals = [0, 4, 7, 11]; break;
        default: intervals = [0, 4, 7];
    }
    
    return intervals.map(interval => {
        const newNoteIndex = (noteIndex + interval) % 12;
        const octaveShift = Math.floor((noteIndex + interval) / 12);
        return `${NOTES[newNoteIndex]}${octave + octaveShift}`;
    });
}

function generateArpeggioPattern(chord, baseDuration) {
    const pattern = [];
    const velocities = [0.8, 0.6, 0.7, 0.6]; // Dynamic velocities
    
    chord.forEach((note, index) => {
        pattern.push({
            pitch: note,
            duration: baseDuration,
            volume: velocities[index % velocities.length]
        });
    });
    
    return pattern;
}

function generateRandomMelody(scale, length, baseDuration) {
    const melody = [];
    let previousNote = null;
    
    for (let i = 0; i < length; i++) {
        let note;
        do {
            const randomIndex = Math.floor(Math.random() * scale.length);
            note = scale[randomIndex];
        } while (note === previousNote); // Avoid repeated notes
        
        melody.push({
            pitch: note,
            duration: baseDuration * (Math.random() < 0.3 ? 2 : 1), // Occasional longer notes
            volume: 0.6 + Math.random() * 0.3 // Dynamic volume
        });
        
        previousNote = note;
    }
    
    return melody;
}

// Enhanced random song generator
function generateRandomSong() {
    const genre = document.getElementById("genre").value;
    const preset = GENRE_PRESETS[genre];
    
    // Clear previous sections
    sections = [];
    currentSectionNotes = {};
    
    // Use genre-specific tempo
    const randomTempo = preset.tempos[Math.floor(Math.random() * preset.tempos.length)];
    document.getElementById("tempo").value = randomTempo;
    document.getElementById("loops").value = -1; // Infinite loops
    
    // Generate sections based on genre
    const sectionTypes = ['Intro', 'Verse', 'Chorus', 'Bridge', 'Outro'];
    const progression = preset.progressions[Math.floor(Math.random() * preset.progressions.length)];
    
    sectionTypes.forEach((sectionType, sectionIndex) => {
        currentSectionNotes = {};
        document.getElementById("sectionName").value = sectionType;
        document.getElementById("repeat").value = 
            (sectionType === 'Chorus' && preset.repeatChorus) ? "true" : "false";
        
        const baseDuration = Math.floor(60000 / randomTempo);
        
        // Generate bass line using genre-specific pattern
        const bassline = progression.map(chord => {
            const rootNote = `${chord.replace(/[^A-G#]/g, '')}3`;
            return generateBassPattern(preset.bassPattern, rootNote, baseDuration);
        }).flat();
        currentSectionNotes['bass'] = bassline;
        
        // Generate chord progression
        progression.forEach(chord => {
            const isMinor = chord.includes('m');
            const rootNote = chord.replace(/[^A-G#]/g, '') + '4';
            const chordNotes = generateChord(rootNote, isMinor ? 'minor' : 'major');
            
            // Apply genre-specific instrument arrangements
            preset.instruments.forEach((instrument, idx) => {
                if (!currentSectionNotes[instrument]) {
                    currentSectionNotes[instrument] = [];
                }
                
                if (sectionType === 'Chorus' || sectionType === 'Bridge') {
                    // Generate genre-specific melodies
                    const scale = generateChord(`${progression[0].replace(/[^A-G#]/g, '')}4`, 'major');
                    currentSectionNotes[instrument].push(
                        ...generateRandomMelody(scale, preset.melodyNotes, baseDuration)
                    );
                } else {
                    // Generate genre-specific accompaniment
                    currentSectionNotes[instrument].push(
                        ...generateArpeggioPattern(chordNotes, baseDuration)
                    );
                }
            });
        });
        
        addSection();
    });
    
    displaySections();
}

// Keep existing utility functions
function addNote() {
    const instrument = document.getElementById("instrument").value;
    const note = document.getElementById("note").value;
    const duration = parseInt(document.getElementById("duration").value);
    const volume = parseFloat(document.getElementById("volume").value);

    if (note && duration) {
        const newNote = {
            pitch: note,
            duration: duration,
            volume: volume
        };

        if (!currentSectionNotes[instrument]) {
            currentSectionNotes[instrument] = [];
        }
        currentSectionNotes[instrument].push(newNote);
        displayNotes();
    }
}

// Keep existing display and utility functions
function displayNotes() {
    const notesList = document.getElementById("notesList");
    const jsonString = JSON.stringify(currentSectionNotes, null, 2);
    notesList.innerHTML = `<pre><code class="language-json">${jsonString}</code></pre>`;
    Prism.highlightAll();
}

function addSection() {
    const sectionName = document.getElementById("sectionName").value;
    const repeat = document.getElementById("repeat").value === "true";
    
    if (sectionName) {
        const sectionTracks = Object.keys(currentSectionNotes).map(instrument => ({
            instrument: instrument,
            notes: currentSectionNotes[instrument]
        }));

        const newSection = {
            name: sectionName,
            repeat: repeat,
            tracks: sectionTracks
        };

        sections.push(newSection);
        displaySections();
        clearCurrentSectionNotes();
    }
}

function displaySections() {
    const sectionsList = document.getElementById("sectionsList");
    const jsonString = JSON.stringify(sections, null, 2);
    sectionsList.innerHTML = `<pre><code class="language-json">${jsonString}</code></pre>`;
    Prism.highlightAll();
}

function clearCurrentSectionNotes() {
    currentSectionNotes = {};
    document.getElementById("notesList").textContent = '';
}

function downloadJSON() {
    const metadata = {
        tempo: parseInt(document.getElementById("tempo").value),
        loops: parseInt(document.getElementById("loops").value)
    };
    
    const json = {
        metadata: metadata,
        sections: sections
    };

    const jsonString = JSON.stringify(json, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "music.json";
    link.click();
}

function copyJSON() {
    const metadata = {
        tempo: parseInt(document.getElementById("tempo").value),
        loops: parseInt(document.getElementById("loops").value)
    };
    
    const json = {
        metadata: metadata,
        sections: sections
    };

    const jsonString = JSON.stringify(json, null, 2);
    
    // Copy to clipboard
    navigator.clipboard.writeText(jsonString).then(() => {
        // Show success message
        const statusElement = document.getElementById("copyStatus");
        statusElement.textContent = "✓ Copied to clipboard!";
        statusElement.classList.add("visible");
        
        // Hide message after 2 seconds
        setTimeout(() => {
            statusElement.classList.remove("visible");
        }, 2000);
    }).catch(err => {
        // Show error message
        const statusElement = document.getElementById("copyStatus");
        statusElement.textContent = "❌ Failed to copy. Please try again.";
        statusElement.classList.add("visible");
        
        setTimeout(() => {
            statusElement.classList.remove("visible");
        }, 2000);
        
        console.error('Failed to copy JSON:', err);
    });
}