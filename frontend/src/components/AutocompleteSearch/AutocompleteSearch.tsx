import React, { useEffect, useState } from 'react';
import useGlobalStore from '../../store/useGlobalStore';
import { getCarById, updateCar } from '../../utils/carFunctions';
type props = {
	carId: number;
	isStart: boolean;
};

type osmData = {
	lat: string;
	long: string;
	name: string;
	display_name: string;
	importance: number;
	type: string;
};
const AutocompleteSearch: React.FC<props> = ({ carId, isStart }) => {
	const [cars, setCars] = useGlobalStore((state) => [state.cars, state.setCars]);
	const car = getCarById(cars, carId);
	const [query, setQuery] = useState(isStart ? car!.startPoint : car!.endPoint);
	const [suggestions, setSuggestions] = useState<string[]>([]);
	const field = isStart ? 'startPoint' : 'endPoint';

	useEffect(() => {
		const fetchSuggestions = async () => {
			if (query.length > 2) {
				// Fetch only when the query is at least 3 characters long
				try {
					const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${query}`);
					const data = await response.json();
					setSuggestions(data.map((item: osmData) => item.display_name));
				} catch (error) {
					console.error('Error fetching suggestions:', error);
				}
			}
		};
		const debounceTimeout = setTimeout(fetchSuggestions, 300);
		return () => clearTimeout(debounceTimeout);
	}, [query]);
	// const updateCar = (id: number, field: keyof Car, value: string | boolean) => {
	// 	setCars(cars.map((car) => (car.id === id ? { ...car, [field]: value } : car)));
	// };
	return (
		<div className="relative">
			<input
				type="text"
				value={query}
				onChange={(e) => setQuery(e.target.value)}
				placeholder="Start typing address..."
				className="border rounded-md p-2 w-full"
			/>
			{suggestions.length > 0 && (
				<ul className="absolute z-10 bg-white border w-full">
					{suggestions.map((suggestion, index) => (
						<li
							key={index}
							onClick={() => {
								setQuery(suggestion);
								setSuggestions([]);
								setCars(updateCar(cars, carId, field, query));
							}}
						>
							{suggestion}
						</li>
					))}
				</ul>
			)}
		</div>
	);
};

export default AutocompleteSearch;
