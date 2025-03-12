# Description: This script demonstrates how to create a scene, build a simulation, and run the simulation.

import pyhelios
from pyhelios.util import scene_writer
import time

if __name__ == "__main__":
    print("Creating scene writer...")
    sim = pyhelios.Simulation()

    scene_name = "test_scene"

    box_mesh_filepath = "data/sceneparts/tree.obj"
    box_mesh = scene_writer.create_scenepart_obj(box_mesh_filepath)

    ground_mesh_filepath = "data/sceneparts/groundplane.obj"
    ground_mesh = scene_writer.create_scenepart_obj(ground_mesh_filepath)

    sp_list = []
    sp_list.extend([box_mesh, ground_mesh])

    print("Building the scene...")
    scene = scene_writer.build_scene(scene_id=scene_name, name=scene_name, sceneparts=sp_list)
    print("Scene built.")

    scene_file = f"data/scenes/{scene_name}.xml"
    print(f"Writing scene to {scene_name}...")
    with open(scene_file, "w") as f:
        f.write(scene)
    print(f"Scene written to {scene_name}.")

    # Build simulation parameters
    print("Building simulation parameters...")
    survey_file = f"data/surveys/test_survey.xml"
    simBuilder = pyhelios.SimulationBuilder(
        survey_file,
        'assets/',
        'output/',
    )
    simBuilder.setNumThreads(8)  
    simBuilder.setRebuildScene(False)

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
            print(f"\rSimulation {sim} running for {int(mins)} min and {int(secs)} sec.", end="")
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

