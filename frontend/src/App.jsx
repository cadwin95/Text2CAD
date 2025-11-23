import React, { useState } from 'react';
import Viewer3D from './components/Viewer3D';
import ChatInterface from './components/ChatInterface';

function App() {
  const [modelUrl, setModelUrl] = useState(null);

  return (
    <div className="flex h-screen w-screen bg-gray-900">
      {/* Left Panel: Chat & Code */}
      <div className="w-1/3 border-r border-gray-700">
        <ChatInterface onModelGenerated={setModelUrl} />
      </div>

      {/* Right Panel: 3D Viewer */}
      <div className="w-2/3 relative">
        <Viewer3D modelUrl={modelUrl} />

        <div className="absolute top-4 right-4 bg-black/50 text-white p-2 rounded text-sm pointer-events-none">
          Text2CAD (OCX Edition)
        </div>
      </div>
    </div>
  );
}

export default App;
