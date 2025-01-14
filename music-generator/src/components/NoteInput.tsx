import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Plus } from 'lucide-react';

type NoteInputProps = {
  instruments: string[];
  onAddNote: (noteData: {
    instrument: string;
    note: string;
    duration: number;
    volume: number;
  }) => void;
};

const NoteInput: React.FC<NoteInputProps> = ({ instruments, onAddNote }) => {
  const [instrument, setInstrument] = useState(instruments[0]);
  const [note, setNote] = useState('');
  const [duration, setDuration] = useState(250);
  const [volume, setVolume] = useState(0.7);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (note && duration) {
      onAddNote({ instrument, note, duration, volume });
      setNote('');
    }
  };

  return (
    <Card>
      <CardContent className="p-6">
        <h2 className="text-xl font-semibold mb-4">Note Input</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Instrument</label>
              <select
                value={instrument}
                onChange={(e) => setInstrument(e.target.value)}
                className="w-full p-2 bg-gray-700 rounded"
              >
                {instruments.map(inst => (
                  <option key={inst} value={inst}>
                    {inst.charAt(0).toUpperCase() + inst.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Note</label>
              <input
                type="text"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="e.g., C4"
                className="w-full p-2 bg-gray-700 rounded"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Duration (ms)</label>
              <input
                type="number"
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                min={0}
                step={250}
                className="w-full p-2 bg-gray-700 rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Volume (0-1)</label>
              <input
                type="number"
                value={volume}
                onChange={(e) => setVolume(Number(e.target.value))}
                min={0}
                max={1}
                step={0.1}
                className="w-full p-2 bg-gray-700 rounded"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Note
          </button>
        </form>
      </CardContent>
    </Card>
  );
};

export default NoteInput;