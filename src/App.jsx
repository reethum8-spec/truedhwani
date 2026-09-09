import { Routes, Route } from 'react-router-dom';
import RootLayout from '@/layouts/RootLayout';
import LandingPage from '@/pages/LandingPage';
import LiveMonitorPage from '@/pages/LiveMonitorPage';
import AnalyticsPage from '@/pages/AnalyticsPage';

export default function App() {
  return (
    <Routes>
      <Route element={<RootLayout />}>
        <Route index element={<LandingPage />} />
        <Route path="live-monitor" element={<LiveMonitorPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
      </Route>
    </Routes>
  );
}
