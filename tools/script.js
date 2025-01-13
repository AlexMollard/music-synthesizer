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
