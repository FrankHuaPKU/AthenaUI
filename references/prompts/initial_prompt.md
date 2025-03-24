根据以下软件项目规划实现程序。

**Project Name**  
AthenaUI: A TUI Framework for Athena++  

---

# I. Core Functionality  

**Overview**: A series of (Python and shell) scripts for Athena++ to enable terminal user-interface (TUI) execution and post-processing.  
**Design Philosophy**: After using AthenaUI, users should *almost never need to interact with Athena++ source code or non-intuitive command-line operations*.  

## 1. Functional Goals  

- **Compatibility**: Prioritize compatibility to Slurm supercomputing platforms (e.g., Beijing Supercomputing Center), while also supporting local development/debugging (macOS/Linux).  
- **Minimalist Interaction**: All operations use TUI or single-command workflows to reduce input steps and learning costs (no need to memorize/copy complex commands).  

## 2. TUI Design  
- **curses**: Python’s `curses` library for cross-platform compatibility. Fallback to ASCII art for unsupported terminals.  
- **Key UI Features**:  
  - Display all required parameters in a single view to avoid repeated prompts.  
  - Dynamically adapt to terminal window sizes.  
  - Use ASCII/box-drawing characters for visual elements (examples below):  
    ```  
    +-------------------+  
    |                   |  
    |                   |  
    +-------------------+  

    +===================+  
    |                   |  
    |                   |  
    +===================+  
    ```  

---

# II. Architecture Design  

## 1. Directory Structure  
```text  
AthenaUI/  
├── user/  
│   ├── platforms/          # Platform templates (.platform files)  
│   │   ├── BSCCsc51248.platform  # Slurm template (SLURM_FLAG=ON)  
│   │   └── macOS.platform  # Local template (SLURM_FLAG=OFF)  
│   ├── example.user        # User config example  
│   └── current.user        # Active user config  
├── src/  
│   ├── pgen/               # Problem generators  
│   │   └── shearingBox.sh  # Shearing box simulation setup  
│   ├── post/               # Post-processing core (Python)  
│   │   └── spectra.py      # Turbulence spectrum analysis  
│   └── commands/           # Command entries (executable shell scripts)  
│       ├── run             # Launch simulation  
│       ├── slc             # Generate 2D slice plots  
│       └── mon             # Monitor running cases  
├── test/  
│   ├── dependency_test.sh  # Environment validation script  
│   └── test_output/        # Test output directory (initially empty)  
├── references/             # Development references  
│   ├── example_scripts/    # Pre-verified algorithm scripts  
│   ├── athena_wiki/        # Athena++ docs  
│   └── lib_doc/            # Library documentation (e.g., curses)  
├── config.sh               # Configuration script 
├── init.sh                 # Initialization script  
└── README.md               # Project documentation  
```  

## 2. Key File Specifications  

- **.platform File** (Example: `BSCCsc51248.platform`):  
  ```ini  
  SLURM_FLAG    = ON                  # Enable Slurm  
  USERNAME      = hyy                 # Slurm job name
    
  MPI_LOAD      = "module load mpich/4.1.2-ib"  
  HDF5_LOAD     = "module load hdf5/1.10.4-parallel-icc18"  
  PYTHON_LOAD   = "module load anaconda/3-Python3.7.4-fenggl"  
  ```  

- **.user File** (Example: `BSCCsc51248-hyy.user`):  
  ```ini  
  ATHENA_PATH   = /public1/home/sc51248/hyy/Athena++/athena    # Path to Athena++ root directory
  ATHENAUI_PATH = /public1/home/sc51248/hyy/Athena++/AthenaUI  # Path to AthenaUI root directory
  
  SLURM_FLAG    = ON  
  USERNAME      = hyy  
  
  MPI_LOAD      = "module load mpich/4.1.2-ib"  
  HDF5_LOAD     = "module load hdf5/1.10.4-parallel-icc18"  
  PYTHON_LOAD   = "module load anaconda/3-Python3.7.4-fenggl"  
  ```  

---

# III. Development Guidelines  

## 1. Code Standards  
- **Slurm Compatibility**: Dynamically switch commands based on `SLURM_FLAG` (e.g., `srun -J $USERNAME python` vs `python`).  
- **Comments**: All code must include detailed Chinese comments explaining core logic and platform adaptations.  
- **Path Handling**: Use absolute paths derived from `ATHENA_PATH`/`ATHENAUI_PATH`; no hardcoding.  

## 2. User Interaction  
- **TUI Implementation**:  
  - Use Python’s `curses` library for interface rendering.  
  - Collect critical parameters (e.g., grid resolution, solver settings) in unified forms to minimize keystrokes.  

## 3. Reference Materials  
- **references/example_scripts**: Verified algorithm scripts for AI-assisted optimization (e.g., MPI parallelization).  
- **references/athena_wiki**: Athena++ official documentation.  
- **references/lib_doc**: Library documentation (e.g., `curses` API references).  

---

# IV. Key Feature Implementation  

## 1. System Configuration (`config.sh`)  
- **First-Time Setup Workflow**:  
  1. If `current.user` is missing, create it with `nano` and populate a template:  
     ```text
     ATHENA_PATH   =                     # Path to your Athena++ directory  
     ATHENAUI_PATH =                     # Path to your AthenaUI directory  
     
     SLURM_FLAG    =                     # ON/OFF  
     USERNAME      =                     # Slurm job name  
     MPI_LOAD      = " "                 # Module load commands  
     HDF5_LOAD     = " "
     PYTHON_LOAD   = " "
    
     # ------------------------------------------------------------
     # example user file: BSCCsc51248-hyy.user
    
     # ATHENA_PATH   = /public1/home/sc51248/hyy/Athena++/athena     # Path to your Athena++ directory
     # ATHENAUI_PATH = /public1/home/sc51248/hyy/Athena++/AthenaUI   # Path to your AthenaUI directory
    
     # SLURM_FLAG    = ON                                            # Slurm flag
     # USERNAME      = hyy                                           # Job name for Slurm systems
    
     # MPI_LOAD      = "module load mpich/4.1.2-ib"
     # HDF5_LOAD     = "module load hdf5/1.10.4-parallel-icc18"
     # PYTHON_LOAD   = "module load anaconda/3-Python3.7.4-fenggl"
     ```  
  2. Run `test/dependency_test.sh` to validate the configuration.  
     - On success: Print *"Dependency test passed! Configuration complete."*  
     - On failure: Re-open `current.user` for editing until validation passes.  

## 2. Initialization Script (`init.sh`)  
- **Functionality**:  
  - Load `current.user` configurations.  
  - Set executable permissions for `src/commands/` scripts.  
  - Add `src/commands/` to `PATH` for direct command access (e.g., `run`, `slc`).  
  - Display an ASCII art welcome screen and supported commands:  
    ```  
    (AthenaUI ASCII art here)  

    Available commands:  
      run: Configure a new simulation case.  
      slc: Generate 2D slice plots from .athdf files.  
      spc: Plot turbulence spectra from .athdf files.  

    Initialization complete! Type a command to start.  
    ```  

---

# V. User Experience  

## Workflow  
1. **First-Time Configuration**:  
   - Run `config.sh` and follow instructions to set up configurations.  

2. **Regular Usage**:  
   - Navigate to `AthenaUI/` and run `init.sh` to launch AthenaUI.  
   - A welcome screen and command list will appear on each launch.  

3. **Short cut**:  
   - Add a custom alias (e.g., `hyy`) to `~/.bashrc` for launching AthenaUI from any directory:  
     ```bash  
     alias hyy='cd /path/to/AthenaUI && source init.sh'  
     ```  
     where the path to AthenaUI is derived from $ATHENAUI_PATH variable.

---

# VI. Development Environment & Workflow  

- **Remote Development**: Use VSCode/Cursor with SSH to connect to Beijing Supercomputing Center.  
- **Code Standards**:  
  - All code must include detailed Chinese comments.
  - Every single file should have a detailed discription at the beginning, explaining its functionalities.
  - Versioning follows **Semantic Versioning** (e.g., `v1.0.0` for stable releases, `v0.y.z` for development).  
- **Repository**: Hosted on GitHub.  

---

# VII. Version Roadmap  

## v0.0 - Framework Setup  
- Initialize directory structure and reference docs.  

## v0.1 - Environment Validation  
- Deliverables:  
  - `user/` directory with config system.  
  - `test/dependency_test.sh` and `test_output/`.  
  - `config.sh`  

## v0.2 - Core Execution  
- Deliverables:  
  - `src/pgen/shearingBox.sh` (simulation setup).  
  - `src/commands/run` (Slurm/local execution).  
  - Functional `init.sh`.  

## v0.3 - Visualization Tools  
- Deliverables:  
  - `src/commands/slc` for Athena++-integrated slice plotting.  
  - Enhanced `init.sh` command listings.  

*Later versions TBD.*

请理解以上需求，并用中文向我提问以确认你正确理解了所有需求，以及进一步确认一些可能的细节。