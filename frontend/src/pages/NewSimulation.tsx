import { useNavigate } from 'react-router-dom';
import useGlobalStore from '../store/useGlobalStore';
import { NavigationMethod } from '../types/types';
import MapPopUp from '../components/map/MapPopUp';
import { Plus, Trash2, Settings, ChevronDown, ChevronUp } from 'lucide-react';

const NewSimulation: React.FC = () => {
	const { startingPoint, setStartingPoint, destinationPoint, setDestinationPoint, navigationMethod, setNavigationMethod, setIsMapVisible } =
		useGlobalStore();
	const navigate = useNavigate();

	const handleNavigationMethodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
		setNavigationMethod(e.target.value as NavigationMethod);
	};
	return (
		<div className="container h-screen bg-slate-200  mx-auto px-4 py-12">
			<h1 className="text-3xl font-bold text-center mb-8">New Simulation</h1>
			<form className="max-w-lg mx-auto bg-white shadow-md px-8 pt-6 mb-4 pb-6">
				<div className="mb-4">
					<label>Selected Point: {startingPoint}</label>
					<button
						type="button"
						className="bg-blue-500 hover:bg-blue-700 text-white py-2 px-6 rounded w-full mt-2"
						onClick={() => setIsMapVisible(true)}
					>
						Choose Starting Point
					</button>
				</div>
				<div className="mb-4">
					<label>Selected Point: {destinationPoint}</label>
					<button
						type="button"
						className="bg-blue-500 hover:bg-blue-700 text-white py-2 px-6 rounded w-full mt-2"
						onClick={() => setIsMapVisible(true)}
					>
						Choose Destination Point
					</button>
				</div>
				<div className="mb-4">
					<label>Choose Navigation Method</label>
					<select
						className="shadow appearance-none border rounded w-full py-2 px-4
						text-gray-700 leading-tight focus:outline-none"
						id="navigationMethod"
						name="navigationMethod"
						value={navigationMethod}
						onChange={handleNavigationMethodChange}
					>
						<option value="Shortest"> Shortest Route</option>
						<option value="AI"> AI Genetated Route</option>
						<option value="Random"> Random Route</option>
						<option value="Scenic"> Scenic Route</option>
					</select>
				</div>
			</form>
			<div className=" max-w-lg mx-auto ">
				<button className="rounded-lg bg-blue-500 text-white px-4 py-2">Confirm</button>
				<button className="rounded-lg bg-pink-400 text-black  px-4 py-2 ml-2">Go Back</button>
			</div>
			<MapPopUp />
		</div>
	);
};
export default NewSimulation;
