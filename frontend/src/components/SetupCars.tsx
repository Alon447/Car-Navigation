import { Plus, Trash2 } from 'lucide-react';
import { Car, osmData } from 'src/types/types';
import useGlobalStore from '../store/useGlobalStore';
import { Button } from './ui/button';
import { useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import Autosuggest from 'react-autosuggest';
import debounce from 'lodash.debounce';

const SetupCars: React.FC = () => {
	const { cars, setCars } = useGlobalStore();
	const [input, setInput] = useState('');
	const { data: suggestions = [], refetch } = useQuery<osmData[]>({
		queryKey: ['suggestions', input],
		queryFn: async () => {
			const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&countrycodes=il&q=${input}`);
			const data = await res.json();
			return data;
		},
		enabled: false,
	});
	const debouncedRefetch = useMemo(() => debounce(() => refetch(), 300), [refetch]);

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

	const renderSuggestion = (suggestion: osmData) => <div className="p-2 hover:bg-gray-100 cursor-pointer">{suggestion.display_name}</div>;

	const inputProps = (car: Car, field: 'startPoint' | 'endPoint') => ({
		placeholder: field === 'startPoint' ? 'Start Point' : 'End Point',
		value: car[field],
		onChange: (_: React.FormEvent<HTMLElement>, { newValue }: Autosuggest.ChangeEvent) => {
			updateCar(car.id, field, newValue);
			setInput(newValue);
			debouncedRefetch();
		},
		onBlur: () => setInput(''),
		className: 'border rounded-md p-2 w-full',
	});
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
							<div className="relative">
								{/* <input
									type="text"
									placeholder="Start Point"
									value={car.startPoint}
									onChange={(e) => updateCar(car.id, 'startPoint', e.target.value)}
									className="border rounded-md p-2 w-full pr-10"
								/> */}
								<Autosuggest
									suggestions={suggestions}
									onSuggestionsFetchRequested={() => {}}
									onSuggestionsClearRequested={() => setInput('')}
									getSuggestionValue={(suggestion) => suggestion.display_name}
									renderSuggestion={renderSuggestion}
									inputProps={inputProps(car, 'startPoint')}
								/>
							</div>
							<div className="relative">
								<Autosuggest
									suggestions={suggestions}
									onSuggestionsFetchRequested={() => refetch()}
									onSuggestionsClearRequested={() => setInput('')}
									getSuggestionValue={(suggestion) => suggestion.display_name}
									renderSuggestion={renderSuggestion}
									inputProps={inputProps(car, 'endPoint')}
								/>
							</div>
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
							<Button
								variant="ghost"
								size="icon"
								onClick={() => removeCar(car.id)}
								className="text-red-500 hover:text-red-700 transition-colors"
							>
								<Trash2 className="w-5 h-5" />
							</Button>
						</div>
					</div>
				))}
				<Button
					variant="ghost"
					onClick={addCar}
					className="flex items-center text-blue-500 hover:text-blue-700 transition-colors font-semibold"
				>
					<Plus className="w-5 h-5 mr-1" /> Add Car
				</Button>
			</div>
		</div>
	);
};

export default SetupCars;
