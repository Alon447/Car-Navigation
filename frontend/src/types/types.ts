export type NavigationMethod = 'Shortest' | 'AI' | 'Random' | 'Scenic';

export type Car = {
	id: number;
	startPoint: string;
	endPoint: string;
	navigationMethod: string;
	useTollRoad: boolean;
	startTime: string;
};
