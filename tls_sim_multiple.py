import pyhelios
from pyhelios.util import scene_writer
import time
import os
import glob
from pathlib import Path
from utils import export_to_raycloud, export_ascii_with_rays


def run_tls_simulation(tree_file_path, output_base_dir="output"):
    """
    Run TLS simulation for a single tree OBJ file.
    
    Args:
        tree_file_path: Path to the tree OBJ file
        output_base_dir: Base directory for outputs
        
    Returns:
        Tuple of (num_measurements, num_trajectories, output_dir)
    """
    # Extract filename without extension for naming
    tree_filename = Path(tree_file_path).stem
    
    # Create output directory for this tree
    output_dir = Path(output_base_dir) / tree_filename
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n=== Processing {tree_filename} ===")
    print(f"Input file: {tree_file_path}")
    print(f"Output directory: {output_dir}")
    
    # Create simulation instance
    sim = pyhelios.Simulation()
    sim_name = f"tls_sim_{tree_filename}"
    
    # Create scene parts list with just this tree
    sp_list = []
    print(f"Loading tree: {tree_file_path}")
    tree_mesh = scene_writer.create_scenepart_obj(tree_file_path)
    sp_list.append(tree_mesh)
    
    # Build the scene
    print("Building the scene...")
    scene = scene_writer.build_scene(scene_id=sim_name, name=sim_name, sceneparts=sp_list)
    print("Scene built.")
    
    # Write scene file
    scene_file = f"data/scenes/{sim_name}.xml"
    print(f"Writing scene to {scene_file}...")
    with open(scene_file, "w") as f:
        f.write(scene)
    print(f"Scene written to {scene_file}.")
    
    # Build simulation parameters
    print("Building simulation parameters...")
    survey_file = "data/surveys/tls_sim_survey.xml"
    simBuilder = pyhelios.SimulationBuilder(
        survey_file,
        'assets/',
        str(output_dir) + '/',
    )
    
    # Set simulation parameters (same as original)
    simBuilder.setNumThreads(0)
    simBuilder.setRebuildScene(False)
    simBuilder.setFixedGpsTimeStart("")
    simBuilder.setLasOutput(True)
    simBuilder.setLas10(True)
    simBuilder.setZipOutput(False)
    simBuilder.setSplitByChannel(False)
    simBuilder.setKDTFactory(4)
    simBuilder.setKDTJobs(0)
    simBuilder.setKDTSAHLossNodes(32)
    simBuilder.setParallelizationStrategy(1)
    simBuilder.setChunkSize(32)
    simBuilder.setWarehouseFactor(4)
    simBuilder.setCallbackFrequency(0)
    simBuilder.setFinalOutput(True)
    simBuilder.setLegNoiseDisabled(True)
    simBuilder.setRebuildScene(False)
    simBuilder.setWriteWaveform(False)
    simBuilder.setCalcEchowidth(False)
    simBuilder.setFullwaveNoise(False)
    simBuilder.setPlatformNoiseDisabled(True)
    simBuilder.setLegacyEnergyModel(True)
    simBuilder.setExportToFile(True)
    simBuilder.setCallback(None)
    simBuilder.rotateFilters = []
    simBuilder.scaleFilters = []
    simBuilder.translateFilters = []
    
    print("Building the simulation...")
    sim = simBuilder.build()
    print("Simulation built.")
    
    # Start the simulation
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
    
    # Join simulation results
    print("\nJoining simulation results...")
    output = sim.join()
    print("Simulation results joined.")
    
    # Get measurements and trajectories
    measurements = output.measurements
    trajectories = output.trajectories
    
    num_measurements = len(measurements)
    num_trajectories = len(trajectories)
    
    print(f'Number of measurements: {num_measurements}')
    print(f'Number of points in trajectory: {num_trajectories}')
    
    # Export additional formats to the tree-specific output directory
    ascii_output_file = output_dir / f"{tree_filename}_rays.asc"
    export_ascii_with_rays(output, str(ascii_output_file))
    
    return num_measurements, num_trajectories, str(output_dir)


def main():
    """
    Main function to run TLS simulations for all tree OBJ files.
    """
    print("=== Multiple Tree TLS Simulation ===")
    
    # Get all tree OBJ files from the rct_synth_trees directory
    tree_pattern = 'data/sceneparts/rct_synth_trees/*.obj'
    tree_files = glob.glob(tree_pattern)
    
    if not tree_files:
        print(f"No tree files found matching pattern: {tree_pattern}")
        return
    
    # Sort files for consistent processing order
    tree_files.sort()
    
    print(f"Found {len(tree_files)} tree files to process")
    
    # Process each tree file
    results = []
    total_start_time = time.time()
    
    for i, tree_file in enumerate(tree_files, 1):
        print(f"\n{'='*60}")
        print(f"Processing tree {i}/{len(tree_files)}")
        print(f"{'='*60}")
        
        try:
            num_measurements, num_trajectories, output_dir = run_tls_simulation(tree_file)
            results.append({
                'file': tree_file,
                'measurements': num_measurements,
                'trajectories': num_trajectories,
                'output_dir': output_dir,
                'status': 'success'
            })
        except Exception as e:
            print(f"ERROR processing {tree_file}: {e}")
            results.append({
                'file': tree_file,
                'measurements': 0,
                'trajectories': 0,
                'output_dir': '',
                'status': 'failed',
                'error': str(e)
            })
    
    # Print summary
    total_duration = time.time() - total_start_time
    print(f"\n{'='*60}")
    print("PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total processing time: {total_duration/60:.1f} minutes")
    print(f"Total trees processed: {len(tree_files)}")
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']
    
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        total_measurements = sum(r['measurements'] for r in successful)
        total_trajectories = sum(r['trajectories'] for r in successful)
        print(f"Total measurements: {total_measurements}")
        print(f"Total trajectory points: {total_trajectories}")
    
    if failed:
        print(f"\nFailed files:")
        for r in failed:
            print(f"  - {Path(r['file']).name}: {r.get('error', 'Unknown error')}")
    
    print(f"\nResults saved to individual folders in 'output/' directory")


if __name__ == "__main__":
    main()