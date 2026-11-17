import React from 'react';
import { Outlet, useParams } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';

export const AppLayout: React.FC = () => {
  const { videoId } = useParams<{ videoId?: string }>();

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-background">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar currentVideoId={videoId} />
        <main className="flex-1 overflow-y-auto bg-[#080b11] p-5">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

