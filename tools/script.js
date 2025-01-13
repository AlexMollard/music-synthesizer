let sections = [];
let currentSectionNotes = {};

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

        // If the instrument already exists in the current section, push the note into the array.
        if (!currentSectionNotes[instrument]) {
            currentSectionNotes[instrument] = [];
        }
        currentSectionNotes[instrument].push(newNote);

        displayNotes();
    } else {
        alert("Please enter valid note and duration!");
    }
}

function displayNotes() {
    const notesList = document.getElementById("notesList");
    const jsonString = JSON.stringify(currentSectionNotes, null, 2);
    notesList.innerHTML = `<pre><code class="language-json">${jsonString}</code></pre>`;
    Prism.highlightAll();  // Apply syntax highlighting
}

function addSection() {
    const sectionName = document.getElementById("sectionName").value;
    const repeat = document.getElementById("repeat").value === "true";
    
    if (sectionName) {
        // Convert current section notes to the appropriate format for tracks
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
    } else {
        alert("Please enter a section name!");
    }
}

function displaySections() {
    const sectionsList = document.getElementById("sectionsList");
    const jsonString = JSON.stringify(sections, null, 2);
    sectionsList.innerHTML = `<pre><code class="language-json">${jsonString}</code></pre>`;
    Prism.highlightAll();  // Apply syntax highlighting
}

function clearCurrentSectionNotes() {
    currentSectionNotes = {};  // Reset the current section notes
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

// Function to generate random song data
// Function to generate random song data
function generateRandomSong() {
    const randomInstruments = ["guitar", "piano", "bass", "synth"];
    const randomNotes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4"];
    const randomTempo = Math.floor(Math.random() * (300 - 30 + 1)) + 30;
    const randomLoops = Math.floor(Math.random() * (10 - 1 + 1)) + 1;
    
    // Set random metadata
    document.getElementById("tempo").value = randomTempo;
    document.getElementById("loops").value = randomLoops;

    // Generate a random section with notes
    const randomSectionName = ["Verse", "Chorus", "Bridge", "Outro"][Math.floor(Math.random() * 4)];
    const randomRepeat = Math.random() > 0.5;
    document.getElementById("sectionName").value = randomSectionName;
    document.getElementById("repeat").value = randomRepeat ? "true" : "false";

    // Generate random notes for current section
    currentSectionNotes = {};
    const numNotes = Math.floor(Math.random() * 5) + 3;  // Random number of notes between 3 and 7
    for (let i = 0; i < numNotes; i++) {
        const randomInstrument = randomInstruments[Math.floor(Math.random() * randomInstruments.length)];
        const randomNote = randomNotes[Math.floor(Math.random() * randomNotes.length)];
        const randomDuration = Math.floor(Math.random() * (500 - 100 + 1)) + 100; // Random duration between 100ms and 500ms
        const randomVolume = parseFloat((Math.random()).toFixed(1));  // Ensure volume is a float (0.0 to 1.0)
        const newNote = {
            pitch: randomNote,
            duration: randomDuration,
            volume: randomVolume
        };

        if (!currentSectionNotes[randomInstrument]) {
            currentSectionNotes[randomInstrument] = [];
        }
        currentSectionNotes[randomInstrument].push(newNote);
    }

    // Display generated section and notes
    addSection();
}
