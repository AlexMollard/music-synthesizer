import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Plus } from 'lucide-react';

type SectionManagementProps = {
  onAddSection: (sectionData: {
    name: string;
    repeat: boolean;
  }) => void;
};

const SectionManagement: React.FC<SectionManagementProps> = ({ onAddSection }) => {
  const [sectionName, setSectionName] = useState('');
  const [repeat, setRepeat] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (sectionName) {
      onAddSection({ name: sectionName, repeat });
      setSectionName('');
      setRepeat(false);
    }
  };

  return (
    <Card>
      <CardContent className="p-6">
        <h2 className="text-xl font-semibold mb-4">Section Management</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Section Name</label>
            <input
              type="text"
              value={sectionName}
              onChange={(e) => setSectionName(e.target.value)}
              placeholder="e.g., Verse, Chorus"
              className="w-full p-2 bg-gray-700 rounded"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="repeat"
              checked={repeat}
              onChange={(e) => setRepeat(e.target.checked)}
              className="w-4 h-4"
            />
            <label htmlFor="repeat" className="text-sm font-medium">
              Repeat Section
            </label>
          </div>

          <button
            type="submit"
            className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Section
          </button>
        </form>
      </CardContent>
    </Card>
  );
};

export default SectionManagement;