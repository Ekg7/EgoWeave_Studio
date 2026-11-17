import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { Overview } from '../pages/Overview';
import { NewAnalysis } from '../pages/NewAnalysis';
import { VideoWorkspace } from '../pages/VideoWorkspace';
import { Library } from '../pages/Library';
import { Evaluation } from '../pages/Evaluation';
import { Settings } from '../pages/Settings';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <Overview />,
      },
      {
        path: 'workspace/new',
        element: <NewAnalysis />,
      },
      {
        path: 'workspace/:videoId',
        element: <VideoWorkspace />,
      },
      {
        path: 'library',
        element: <Library />,
      },
      {
        path: 'evaluation',
        element: <Evaluation />,
      },
      {
        path: 'settings',
        element: <Settings />,
      },
      {
        path: '*',
        element: <Navigate to="/" replace />,
      },
    ],
  },
]);

