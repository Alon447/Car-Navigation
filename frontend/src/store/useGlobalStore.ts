import { create } from 'zustand';
import { Car, NavigationMethod } from '../types/types';

type SimulationState = {
	// inputs
	startingPoint: string;
	setStartingPoint: (point: string) => void;

	destinationPoint: string;
	setDestinationPoint: (point: string) => void;

	navigationMethod: NavigationMethod;
	setNavigationMethod: (method: NavigationMethod) => void;

	cars: Car[];
	setCars: (cars: Car[]) => void;

	simulationSpeed: number;
	setSimulationSpeed: (simulationSpeed: number) => void;
	// is map pop up visible
	isMapVisible: boolean;
	setIsMapVisible: (isVisible: boolean) => void;
};

const useGlobalStore = create<SimulationState>((set) => ({
	startingPoint: '',
	setStartingPoint: (point) => set({ startingPoint: point }),
	destinationPoint: '',
	setDestinationPoint: (point) => set({ destinationPoint: point }),
	navigationMethod: 'Shortest',
	setNavigationMethod: (navigationMethod: NavigationMethod) => {
		set({ navigationMethod: navigationMethod });
	},
	cars: [],
	setCars: (cars: Car[]) => set({ cars: cars }),
	isMapVisible: false,
	setIsMapVisible: (isVisible: boolean) => set({ isMapVisible: isVisible }),
	simulationSpeed: 1,
	setSimulationSpeed: (simulationSpeed: number) => set({ simulationSpeed: simulationSpeed }),
}));

export default useGlobalStore;
