import { Modal } from 'antd';
import { LatLngExpression } from 'leaflet';
import { useCallback, useState } from 'react';
import { Marker, Popup, TileLayer } from 'react-leaflet';
import { MapContainer } from 'react-leaflet/MapContainer';
import { useMapEvents } from 'react-leaflet/hooks';
import useGlobalStore from '../../store/useGlobalStore';

interface MapClickHandlerProps {
	onPositionSelected: (position: LatLngExpression) => void;
}

function MapClickHandler({ onPositionSelected }: MapClickHandlerProps) {
	useMapEvents({
		click: (e) => {
			onPositionSelected([e.latlng.lat, e.latlng.lng]);
		},
	});
	return null;
}
interface MapPopUpProps {
	onConfirm: (position: LatLngExpression) => void;
}
const MapPopUp: React.FC<MapPopUpProps> = ({ onConfirm }) => {
	const { isMapVisible, setIsMapVisible } = useGlobalStore();
	const [selectedPosition, setSelectedPosition] = useState<LatLngExpression | null>(null);
	const startingPosition: LatLngExpression = [32.27, 34.88];
	const handlePositionSelected = useCallback((position: LatLngExpression) => {
		setSelectedPosition(position);
	}, []);
	const handleConfirm = () => {
		if (selectedPosition) {
			onConfirm(selectedPosition);
			setIsMapVisible(false);
		}
	};
	return (
		<Modal
			title="Pop up"
			open={isMapVisible}
			height="600px"
			width="600px"
			onCancel={() => setIsMapVisible(false)}
			// footer={null}
			footer={[
				<button
					className="px-4 py-2 text-gray-600 bg-gray-200 rounded hover:bg-gray-300 transition-colors"
					key="Cancel"
					onClick={() => setIsMapVisible(false)}
				>
					Cancel
				</button>,
				<button
					className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ml-2"
					key="Confirm"
					onClick={handleConfirm}
					disabled={!selectedPosition}
				>
					Confirm
				</button>,
			]}
		>
			<div className="h-96">
				<MapContainer
					center={startingPosition}
					zoom={13}
					scrollWheelZoom={true}
					className="h-full w-full"
				>
					<MapClickHandler onPositionSelected={handlePositionSelected} />
					<TileLayer
						attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
						url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
					/>
					{selectedPosition && (
						<Marker position={startingPosition}>
							<Popup>
								A pretty CSS3 popup. <br /> Easily customizable.
							</Popup>
						</Marker>
					)}
				</MapContainer>
			</div>
		</Modal>
	);
};
export default MapPopUp;
