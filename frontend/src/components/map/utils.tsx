import { useMapEvent } from 'react-leaflet';

export const OnMapClick = () => {
	const map = useMapEvent('click', () => {});
	return null;
};
