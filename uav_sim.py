# Description: This script demonstrates how to create a scene, build a simulation, and run the simulation.

import pyhelios
from pyhelios.util import scene_writer
import time

if __name__ == "__main__":
    print("Creating scene writer...")
    sim = pyhelios.Simulation()

    sim_name = "uav_sim"

    box_mesh_filepath = "data/sceneparts/tree.obj"
    box_mesh = scene_writer.create_scenepart_obj(box_mesh_filepath)

    ground_mesh_filepath = "data/sceneparts/groundplane.obj"
    ground_mesh = scene_writer.create_scenepart_obj(ground_mesh_filepath)

    sp_list = []
    sp_list.extend([box_mesh, ground_mesh])

    print("Building the scene...")
    scene = scene_writer.build_scene(scene_id=sim_name, name=sim_name, sceneparts=sp_list)
    print("Scene built.")

    scene_file = f"data/scenes/{sim_name}.xml"
    print(f"Writing scene to {sim_name}...")
    with open(scene_file, "w") as f:
        f.write(scene)
    print(f"Scene written to {sim_name}.")

    # Build simulation parameters
    print("Building simulation parameters...")
    survey_file = f"data/surveys/{sim_name}_survey.xml"
    simBuilder = pyhelios.SimulationBuilder(
        survey_file,
        'assets/',
        'output/',
    )

    # Set simulation parameters, these are the default values.
    simBuilder.setNumThreads(0)                # Sets the number of threads for simulation processing (0 means use all available)
    simBuilder.setRebuildScene(False)          # Controls whether to rebuild the scene or use cached version if available
    simBuilder.setFixedGpsTimeStart("")        # Sets the GPS start time (empty uses system time)
    simBuilder.setLasOutput(False)             # Controls whether to output point cloud in LAS format
    simBuilder.setLas10(False)                 # Controls whether to use LAS format version 1.0
    simBuilder.setZipOutput(False)             # Controls whether to compress output files
    simBuilder.setSplitByChannel(False)        # Controls whether to create separate output files for each channel
    simBuilder.setKDTFactory(4)                # Sets the KDTree implementation type (4 = Fast SAH approximation)
    simBuilder.setKDTJobs(0)                   # Sets number of threads for KDTree building (0 = all available)
    simBuilder.setKDTSAHLossNodes(32)          # Sets number of bins/nodes for Surface Area Heuristic
    simBuilder.setParallelizationStrategy(1)   # Sets parallelization approach (1 = warehouse-based strategy)
    simBuilder.setChunkSize(32)                # Sets processing chunk size for task distribution
    simBuilder.setWarehouseFactor(4)           # Sets multiplier for number of tasks in the warehouse relative to workers
    simBuilder.setCallbackFrequency(0)         # Sets how often simulation progress callback is called (0 = every frame)
    simBuilder.setFinalOutput(True)            # Controls whether final result files are generated
    simBuilder.setLegNoiseDisabled(True)       # Controls whether to disable leg noise regardless of XML settings
    simBuilder.setRebuildScene(False)          # Controls whether to rebuild the scene (duplicate parameter)
    simBuilder.setWriteWaveform(False)         # Controls whether to write full waveform data
    # simBuilder.setWritePulse(False)            # Controls whether to write all pulse data, including misses # TODO THIS IS NOT EXPOSED TO PYHELIOS YET
    simBuilder.setCalcEchowidth(False)         # Controls whether to calculate echo width from waveform
    simBuilder.setFullwaveNoise(False)         # Controls whether to add random noise to full waveform
    simBuilder.setPlatformNoiseDisabled(True)  # Controls whether to disable platform noise regardless of XML settings
    simBuilder.setLegacyEnergyModel(True)      # Controls whether to use the legacy energy calculation model
    simBuilder.setExportToFile(True)           # Controls whether to export simulation results to files
    simBuilder.setCallback(None)               # Sets a callback function for monitoring simulation progress
    simBuilder.rotateFilters = []              # Defines rotation filters to apply to the scene
    simBuilder.scaleFilters = []               # Defines scaling filters to apply to the scene
    simBuilder.translateFilters = []           # Defines translation filters to apply to the scene
    
    print("Building the simulation...")
    sim = simBuilder.build()
    print("Simulation built.")
    print("done building")

    # Get the first leg pulse frequency
    leg = sim.sim.getLeg(0)
    freq = leg.getScannerSettings().pulseFreq
    scanner = sim.sim.getScanner()
    scanner_id = scanner.deviceId

    # Start the simulation.
    print("Starting the simulation...")
    start_time = time.time()
    sim.start()
    
    if sim.isStarted():
        print('Simulation has started!\nSurvey Name: {survey_name}\n{scanner_info}'.format(
            survey_name=sim.sim.getSurvey().name,
            scanner_info=sim.sim.getScanner().toString()))

        while sim.isRunning():
            duration = time.time() - start_time
            mins = duration // 60
            secs = duration % 60
            print(f"\rSimulation {sim_name} running for {int(mins)} min and {int(secs)} sec.", end="")
            time.sleep(1)

    # Create instance of PyHeliosOutputWrapper class using sim.join().
    print("Joining simulation results...")
    output = sim.join()
    print("Simulation results joined.")

    # Create instances of vector classes by accessing 'measurements' and 'trajectories' attributes of output wrapper.
    measurements = output.measurements
    trajectories = output.trajectories

    # Get amount of points in trajectory and amount of measurements by accessing length of measurement and trajectory vectors.
    print(f'\nNumber of measurements for sim {sim}: {len(measurements)}')
    print(f'Number of points in trajectory for sim {sim}: {len(trajectories)}')

