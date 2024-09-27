import { Car } from 'src/types/types';

export const getCarById = (cars: Car[], id: number): Car | undefined => {
	return cars.find((car) => car.id === id);
};

export const updateCar = (cars: Car[], id: number, field: keyof Car, value: string | boolean): Car[] => {
	return cars.map((car) => (car.id === id ? { ...car, [field]: value } : car));
};
