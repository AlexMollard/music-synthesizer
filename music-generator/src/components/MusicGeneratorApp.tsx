'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Music, Copy, Download, Wand2 } from 'lucide-react';
import NoteInput from './NoteInput';
import SectionManagement from './SectionManagement';
import { expandChordProgression } from '@/lib/chord-utils';
import { generateSection } from '@/lib/music-logic';
import { GENRE_PRESETS } from '@/lib/genre-presets';

// Types
type Note = {
    pitch: string;
    duration: number;
    volume: number;
};

type Track = {
    instrument: string;
    notes: Note[];
};

type Section = {
    name: string;
    repeat: boolean;
    tracks: Track[];
};

const MusicGeneratorApp = () => {
    // State management
    const [sections, setSections] = useState<Section[]>([]);
    const [currentSectionNotes, setCurrentSectionNotes] = useState<Record<string, Note[]>>({});
    const [tempo, setTempo] = useState(120);
    const [loops, setLoops] = useState(4);
    const [genre, setGenre] = useState('pop');
    const [copyStatus, setCopyStatus] = useState('');

    // Constants
    const AVAILABLE_INSTRUMENTS = ['piano', 'guitar', 'bass', 'xylophone', 'bongos', 'claves'];
    const GENRES = ['pop', 'rock', 'jazz', 'electronic', 'classical', 'hiphop', 'ambient', 'funk'];

    // Generate random melody from chord progression
    const generateRandomMelody = (chordProgression: string[], length: number): Note[] => {
        const melody: Note[] = [];
        const durations = [250, 500, 1000];

        // Get all available notes from the chord progression
        const availableNotes = expandChordProgression(chordProgression).flat();

        for (let i = 0; i < length; i++) {
            const note = availableNotes[Math.floor(Math.random() * availableNotes.length)];
            const duration = durations[Math.floor(Math.random() * durations.length)];
            melody.push({
                pitch: note,
                duration,
                volume: 0.6 + Math.random() * 0.3
            });
        }

        return melody;
    };

    // Generate random song based on genre
    const generateRandomSong = () => {
        const preset = GENRE_PRESETS[genre as keyof typeof GENRE_PRESETS] || GENRE_PRESETS.pop;

        // Reset current state
        setSections([]);
        setCurrentSectionNotes({});

        // Set tempo from genre preset
        const randomTempo = preset.tempos[Math.floor(Math.random() * preset.tempos.length)];
        setTempo(randomTempo);

        // Get a random progression from the genre's progressions
        const progression = preset.progressions[
            Math.floor(Math.random() * preset.progressions.length)
        ];

        // Generate sections with proper musical structure
        const sectionStructure = [
            { type: 'Intro', progression },
            { type: 'Verse', progression },
            { type: 'Chorus', progression },
            { type: 'Verse', progression },
            { type: 'Chorus', progression },
            { type: 'Bridge', progression },
            { type: 'Chorus', progression },
            { type: 'Outro', progression }
        ];

        const generatedSections = sectionStructure.map(({ type, progression }) =>
            generateSection(
                type,
                progression,
                preset.instruments,
                preset,  // Pass the entire genre preset
                preset.melodyNotes
            )
        );

        setSections(generatedSections);
    };

    // Handle note addition
    const handleAddNote = (formData: {
        instrument: string;
        note: string;
        duration: number;
        volume: number;
    }) => {
        const { instrument, note, duration, volume } = formData;
        setCurrentSectionNotes(prev => ({
            ...prev,
            [instrument]: [
                ...(prev[instrument] || []),
                { pitch: note, duration, volume }
            ]
        }));
    };

    // Handle section addition
    const handleAddSection = (sectionData: { name: string; repeat: boolean }) => {
        const { name, repeat } = sectionData;
        const tracks = Object.entries(currentSectionNotes).map(([instrument, notes]) => ({
            instrument,
            notes: [...notes]
        }));

        setSections(prev => [...prev, { name, repeat, tracks }]);
        setCurrentSectionNotes({});
    };

    // Handle JSON export
    const handleExportJSON = () => {
        const musicData = {
            metadata: { tempo, loops },
            sections
        };
        return JSON.stringify(musicData, null, 2);
    };

    // Copy to clipboard
    const handleCopyJSON = async () => {
        const json = handleExportJSON();
        try {
            await navigator.clipboard.writeText(json);
            setCopyStatus('✓ Copied to clipboard!');
            setTimeout(() => setCopyStatus(''), 2000);
        } catch (err) {
            setCopyStatus('❌ Failed to copy');
            console.error('Copy failed:', err);
        }
    };

    // Download JSON file
    const handleDownload = () => {
        const json = handleExportJSON();
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'music.json';
        link.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="min-h-screen bg-gray-900 text-gray-100">
            {/* Header */}
            <header className="bg-gray-800 p-6 shadow-lg">
                <h1 className="text-3xl font-bold text-center text-yellow-500 mb-4">
                    Music JSON Generator
                </h1>
                <div className="flex justify-center space-x-4">
                    {copyStatus && (
                        <Alert>
                            <AlertDescription>{copyStatus}</AlertDescription>
                        </Alert>
                    )}
                    <button
                        onClick={handleCopyJSON}
                        className="flex items-center px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
                    >
                        <Copy className="w-4 h-4 mr-2" />
                        Copy JSON
                    </button>
                    <button
                        onClick={handleDownload}
                        className="flex items-center px-4 py-2 bg-green-600 rounded hover:bg-green-700"
                    >
                        <Download className="w-4 h-4 mr-2" />
                        Download JSON
                    </button>
                    <button
                        onClick={generateRandomSong}
                        className="flex items-center px-4 py-2 bg-purple-600 rounded hover:bg-purple-700"
                    >
                        <Wand2 className="w-4 h-4 mr-2" />
                        Generate Random Song
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Configuration Column */}
                <div className="space-y-6">
                    {/* Basic Settings */}
                    <Card>
                        <CardContent className="p-6">
                            <h2 className="text-xl font-semibold mb-4">Basic Settings</h2>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2">Tempo (BPM)</label>
                                    <input
                                        type="number"
                                        value={tempo}
                                        onChange={(e) => setTempo(Number(e.target.value))}
                                        className="w-full p-2 bg-gray-700 rounded"
                                        min={30}
                                        max={300}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">Loops</label>
                                    <input
                                        type="number"
                                        value={loops}
                                        onChange={(e) => setLoops(Number(e.target.value))}
                                        className="w-full p-2 bg-gray-700 rounded"
                                        min={1}
                                        max={10}
                                    />
                                </div>
                            </div>
                            <div className="mt-4">
                                <label className="block text-sm font-medium mb-2">Genre</label>
                                <select
                                    value={genre}
                                    onChange={(e) => setGenre(e.target.value)}
                                    className="w-full p-2 bg-gray-700 rounded"
                                >
                                    {GENRES.map(g => (
                                        <option key={g} value={g}>
                                            {g.charAt(0).toUpperCase() + g.slice(1)}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Note Input */}
                    <NoteInput
                        instruments={AVAILABLE_INSTRUMENTS}
                        onAddNote={handleAddNote}
                    />

                    {/* Section Management */}
                    <SectionManagement
                        onAddSection={handleAddSection}
                    />
                </div>

                {/* Preview Column */}
                <div className="space-y-6">
                    {/* Current Notes Preview */}
                    <Card>
                        <CardContent className="p-6">
                            <h2 className="text-xl font-semibold mb-4">Current Section Notes</h2>
                            <pre className="bg-gray-800 p-4 rounded overflow-auto max-h-60">
                                {JSON.stringify(currentSectionNotes, null, 2)}
                            </pre>
                        </CardContent>
                    </Card>

                    {/* All Sections Preview */}
                    <Card>
                        <CardContent className="p-6">
                            <h2 className="text-xl font-semibold mb-4">All Sections</h2>
                            <pre className="bg-gray-800 p-4 rounded overflow-auto max-h-60">
                                {JSON.stringify(sections, null, 2)}
                            </pre>
                        </CardContent>
                    </Card>
                </div>
            </main>
        </div>
    );
};

export default MusicGeneratorApp;