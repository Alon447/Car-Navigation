export type NavigationMethod = 'Shortest' | 'AI' | 'Random' | 'Scenic';

export type Car = {
	id: number;
	startPoint: string;
	endPoint: string;
	navigationMethod: string;
	useTollRoad: boolean;
	startTime: string;
};

export type osmData = {
	lat: string;
	long: string;
	name: string;
	display_name: string;
	importance: number;
	type: string;
};
