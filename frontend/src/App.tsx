import { BrowserRouter, Route, Routes } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import NewSimulation from './pages/NewSimulation';
import 'leaflet/dist/leaflet.css';
import MapPopUp from './components/map/MapPopUp';
import SimulationSetup from './pages/SimulationSetup';

function App() {
	return (
		<BrowserRouter>
			<Routes>
				<Route
					path="/"
					element={<LandingPage />}
				/>
				<Route
					path="/setup"
					element={<SimulationSetup />}
				/>
			</Routes>
		</BrowserRouter>
	);
}

export default App;
