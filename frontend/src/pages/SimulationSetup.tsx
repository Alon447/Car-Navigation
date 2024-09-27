import { useState } from 'react';
import { Settings, ChevronDown, ChevronUp } from 'lucide-react';
import SimulationSettings from '../components/SimulationSettings';
import SetupCars from '../components/SetupCars';
import { useNavigate } from 'react-router-dom';

const SimulationSetup: React.FC = () => {
	const [showSettings, setShowSettings] = useState(false);
	const navigate = useNavigate();

	return (
		<div className="min-h-screen bg-gradient-to-r from-blue-400 to-blue-500 py-12 px-4 sm:px-6 lg:px-8">
			<div className="max-w-4xl mx-auto">
				<h1 className="text-4xl font-bold text-center mb-8 text-white">Set Up New Simulation</h1>
				<SetupCars />

				<div className="bg-white shadow-lg rounded-lg overflow-hidden mb-8">
					<button
						onClick={() => setShowSettings(!showSettings)}
						className="w-full p-4 text-left font-semibold text-gray-700 hover:bg-gray-50 transition-colors flex justify-between items-center"
					>
						<span className="flex items-center">
							<Settings className="w-5 h-5 mr-2" /> Simulation Settings
						</span>
						{showSettings ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
					</button>
					{showSettings && <SimulationSettings />}
				</div>

				<div className="text-center">
					<button
						// onClick={startSimulation}
						className="bg-green-500 text-white px-8 py-3 rounded-full text-lg font-semibold hover:bg-green-600 transition-colors shadow-lg"
					>
						Start Simulation
					</button>
					<button
						onClick={() => navigate('/')}
						className="bg-red-500 text-white px-8 py-3 rounded-full text-lg font-semibold hover:bg-red-600 transition-colors shadow-lg"
					>
						Go Back
					</button>
				</div>
			</div>
		</div>
	);
};
export default SimulationSetup;
