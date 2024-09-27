import { useNavigate } from 'react-router-dom';
import { Car } from 'lucide-react';
import { Button } from '../components/ui/button';
const LandingPage = () => {
	const navigate = useNavigate();
	return (
		<div className="min-h-screen flex flex-col items-center justify-center text-white bg-gradient-to-r from-blue-400 to-blue-500">
			<Car className="w-24 h-24 mb-8" />
			<h1 className="text-5xl font-bold mb-4">Car Navigation</h1>
			<p className="text-xl mb-8">Experience realistic navigation scenarios and optimize your routes</p>
			<Button
				className="bg-white text-blue-600 hover:bg-blue-50 hover:text-blue-700 transition-colors duration-200 font-semibold py-2 px-6 rounded-full text-lg shadow-lg hover:shadow-xl transform hover:scale-105"
				onClick={() => {
					navigate('/setup');
				}}
			>
				Start New Simulation
			</Button>
		</div>
	);
};
export default LandingPage;
