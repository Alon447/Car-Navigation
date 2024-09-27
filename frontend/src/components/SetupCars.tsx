import { MapPin, Plus, Trash2 } from 'lucide-react';
import useGlobalStore from '../store/useGlobalStore';
import { Car } from 'src/types/types';
import { useState } from 'react';
import { LatLngExpression } from 'leaflet';

const SetupCars: React.FC = () => {
	const { cars, setCars, isMapVisible, setIsMapVisible } = useGlobalStore();

	// const [currentEditingCar, setCurrentEditingCar] = useState<{ id: number; field: 'startPoint' | 'endPoint' } | null>(null);
	const addCar = () => {
		const newCar: Car = {
			id: Date.now(),
			startPoint: '',
			endPoint: '',
			navigationMethod: 'fastest',
			useTollRoad: false,
			startTime: '09:00',
		};
		setCars([...cars, newCar]);
	};

	const updateCar = (id: number, field: keyof Car, value: string | boolean) => {
		setCars(cars.map((car) => (car.id === id ? { ...car, [field]: value } : car)));
	};

	const removeCar = (id: number) => {
		setCars(cars.filter((car) => car.id !== id));
	};

	// const handleMapPointSelect = (position: LatLngExpression) => {
	// 	if (currentEditingCar) {
	// 		const { id, field } = currentEditingCar;
	// 		// updateCar(id, field, `${position[0]}, ${position[1]}`);
	// 		setCurrentEditingCar(null);
	// 	}
	// };
	// const openMap = (id: number, field: 'startPoint' | 'endPoint') => {
	// 	setCurrentEditingCar({ id, field });
	// 	setIsMapVisible(true);
	// };
	return (
		<div className="bg-white shadow-lg rounded-lg overflow-hidden mb-8">
			<div className="p-6">
				<h2 className="text-2xl font-semibold mb-4 text-gray-700">Cars in Simulation</h2>
				{cars.map((car) => (
					<div
						key={car.id}
						className="mb-6 p-4 border border-gray-200 rounded-lg shadow-sm"
					>
						<div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
							<input
								type="text"
								placeholder="Start Point"
								value={car.startPoint}
								onChange={(e) => updateCar(car.id, 'startPoint', e.target.value)}
								className="border rounded-md p-2 w-full"
							/>

							<input
								type="text"
								placeholder="End Point"
								value={car.endPoint}
								onChange={(e) => updateCar(car.id, 'endPoint', e.target.value)}
								className="border rounded-md p-2 w-full"
							/>
							<input
								type="time"
								value={car.startTime}
								onChange={(e) => updateCar(car.id, 'startTime', e.target.value)}
								className="border rounded-md p-2 w-full"
							/>
						</div>
						<div className="flex flex-wrap items-center justify-between gap-4">
							<select
								value={car.navigationMethod}
								onChange={(e) => updateCar(car.id, 'navigationMethod', e.target.value)}
								className="border rounded-md p-2 flex-grow"
							>
								<option value="fastest">Fastest Route</option>
								<option value="shortest">Shortest Route</option>
								<option value="economical">Most Economical</option>
							</select>
							<label className="flex items-center">
								<input
									type="checkbox"
									checked={car.useTollRoad}
									onChange={(e) => updateCar(car.id, 'useTollRoad', e.target.checked)}
									className="mr-2"
								/>
								Use Toll Roads
							</label>
							<button
								onClick={() => removeCar(car.id)}
								className="text-red-500 hover:text-red-700 transition-colors"
							>
								<Trash2 className="w-5 h-5" />
							</button>
						</div>
					</div>
				))}
				<button
					onClick={addCar}
					className="flex items-center text-blue-500 hover:text-blue-700 transition-colors font-semibold"
				>
					<Plus className="w-5 h-5 mr-1" /> Add Car
				</button>
			</div>
		</div>
	);
};

export default SetupCars;
