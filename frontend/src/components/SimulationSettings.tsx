import useGlobalStore from '../store/useGlobalStore';

const SimulationSettings: React.FC = () => {
	const { simulationSpeed, setSimulationSpeed } = useGlobalStore();

	return (
		<div className="p-6">
			<div className="mb-6">
				<label className="block mb-2 font-medium text-gray-700">Simulation Speed</label>
				<input
					type="range"
					min="1"
					max="15"
					step="2"
					value={simulationSpeed}
					onChange={(e) => setSimulationSpeed(parseFloat(e.target.value))}
					className="w-full"
				/>
				<span className="text-gray-600">{simulationSpeed}x</span>
			</div>
			{/* <div>
            <label className="block mb-2 font-medium text-gray-700">Traffic Density</label>
            <input
            type="range"
            min="0"
            max="100"
            value={trafficDensity}
            onChange={(e) => setTrafficDensity(parseInt(e.target.value))}
                className="w-full"
            />
            <span className="text-gray-600">{trafficDensity}%</span>
            </div> */}
		</div>
	);
};
export default SimulationSettings;
