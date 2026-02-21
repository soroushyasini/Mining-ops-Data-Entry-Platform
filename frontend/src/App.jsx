import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import BunkerLoads from './pages/BunkerLoads'
import Shipments from './pages/Shipments'
import LabSamples from './pages/LabSamples'
import Payments from './pages/Payments'
import TransportCosts from './pages/TransportCosts'
import Drivers from './pages/Drivers'
import Trucks from './pages/Trucks'
import Facilities from './pages/Facilities'
import Alerts from './pages/Alerts'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/bunker-loads" replace />} />
          <Route path="bunker-loads" element={<BunkerLoads />} />
          <Route path="shipments" element={<Shipments />} />
          <Route path="lab-samples" element={<LabSamples />} />
          <Route path="payments" element={<Payments />} />
          <Route path="transport-costs" element={<TransportCosts />} />
          <Route path="drivers" element={<Drivers />} />
          <Route path="trucks" element={<Trucks />} />
          <Route path="facilities" element={<Facilities />} />
          <Route path="alerts" element={<Alerts />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
