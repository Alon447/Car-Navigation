import { BrowserRouter, Route, Routes } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SimulationSetup from './pages/SimulationSetup';
function App() {
	const queryClient = new QueryClient();
	return (
		<QueryClientProvider client={queryClient}>
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
		</QueryClientProvider>
	);
}

export default App;
