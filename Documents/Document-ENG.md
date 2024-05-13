# OpenPharm Manual (English)

<img src="images/logo.png" alt="OpenPharm Logo" height="200">

OpenPharm powers PharmacoNet's graphical user interface for fully automated protein-based pharmacophore modeling and ultra-fast virtual screening with deep learning.

Development and maintenance: Seonghwan Seo (Laboratory of Prof. Woo Yeon Kim, Department of Chemistry, KAIST)

If you use OpenPharm in your work, please cite: 
> Seo, S., & Kim, W. Y. (2023, December). PharmacoNet: Accelerating Large-Scale Virtual Screening by Deep Pharmacophore Modeling. In NeurIPS 2023 Workshop on New Frontiers of AI for Drug Discovery and Development.

Paper: https://arxiv.org/abs/2310.00681

Source Code: https://github.com/SeonghwanSeo/OpenPharm



## 1. Start

### 1-1. Install

Download the source code from Github and install the required libraries through the Anaconda virtual environment.

```bash
# Install Project
git clone https://github.com/SeonghwanSeo/OpenPharm
cd OpenPharm

# Install conda environment
conda env create -f environment.yml
conda activate openpharm
pip install .
```

### 1-2. Launch

User can now run OpenPharm with the openpharm command as shown below.

```bash
conda activate openpharm  # (re-activate to load alias)
openpharm
```

The first time user run OpenPharm, it goes through an initial setup process and downloads the necessary files. (139 MB)

<img src="images/googledrive_download.png" alt="image-20240503184859239" style="zoom:33%;" />

Once all downloads have finished, subsequent runs will take about seconds of loading time.



## 2. Protein-based Pharmacophore Modeling

### 2-1. Specifying proteins and binding sites

OpenPharm downloads protein files from RCSB, automatically parses them, and recognizes binding sites.

Enter the PDB code in `Enter RCSB PDB Code`.

If user wants to use a custom protein file, manually enter the protein file (`.pdb`) via `Open Protein File` and the binding ligand (`.mol2, .sdf`) via `Open Ligand File` to recognize the binding site.

Tap the button (▸) left to `Protein` in the explorer to visualize the structure, including chains, sticks, and lines.

<img src="images/rcsb_load.png" style="zoom:33%;" />

### 2-2. Pharmacophore modeling

Select the desired binding site ligand from explorer, and click the `Modeling` to perform protein-based pharmacophore modeling.

The calculated pharmacopore model can be saved by clicking `Save Model File` (`.pm` extension)

<img src="images/modeling.png" style="zoom:33%;" />

<img src="images/model.png" style="zoom:33%;" />

### 2-3. Importing a pharmacopore model

User can load the saved pharmacopore models by clicking `Open Model File` or by drag and drop the file into the program window.

Before clicking `Open Model File`, user needs to initialize the session by `Clear`.



### 2-4. Initializing a session

To reset the protein or pharmacophore model, click `Clear`.

<img src="images/model_clear.png" style="zoom:33%;" />



## 3. Ultra-fast virtual screening

With the pharmacopore model open, user can perform virtual screening by clicking the `Screening`.

<img src="images/screening_window.png" style="zoom:33%;" />



### 3-1. Open the compound library

Click the `Library` to select a folder, or drag and drop it into the screening window.
Then all `sdf` and `mol2` files within the folder and its subfolders will be loaded.
(Each file can contain one or more conformers).

For example, if user select the `library/` folder below, the files `a.mol2`, `b.mol2`, `c.mol2`, `d.sdf`, `d.mol2`, and `e.sdf` will all be loaded.

```bash
├── library/
    ├── a.mol2
    ├── library1/
    │   ├── b.mol2
    │   └── library1_1/
    │       ├── c.mol2
    │       └── d.sdf
    └── library2/
        ├── d.mol2
        └── e.sdf
```

Below is a screenshot when opening an example library of 1,000 compounds containing 8 conformers.
(Example library: https://drive.google.com/file/d/1XCMv97WpfgEccR4xXTGep_PCMMJq3f7t/view?usp=share_link)

<img src="images/screening_library_load.png" style="zoom:33%;" />

User can change the file parsing rule by clicking `Advanced` and choose between `File Name` or `File Path.` (Default: `File Name.`)

For example, `d.sdf` and `d.mol2` above are indistinguishable because they have the same filename, but they are distinguishable with their file paths.

Below is the screenshot when `File Path` is selected.

<img src="images/screening_library_load_filepath.png" style="zoom:33%;" />



### 3-2. Parameter Setting

PharmacoNet, a built-in program in OpenPharm, performs screening through parameters assigned to 7 pharmacophoric feature type.
OpenPharm allows user to change the weighting for each type.

User can change the value under `Parameter Setting` via mouse or keyboard, and it will be colored blue if it is set higher than the default, or red if it is set lower.

Clicking `Reset All` resets the parameters to the default setting.

<img src="images/screening_parameter.png" style="zoom:33%;" />



### 3-3. Virtual screening

Once everything is set up, set the number of CPU cores for multi-processing by changing the slide bar or number next to `CPUs`.
OpenPharm automatically recognizes the maximum number of CPUs in system.

Finally, click `Run` to start virtual screening.
After screening, the molecules with the highest scores are listed first.

<img src="images/screening_run.png" style="zoom:33%;" />

<img src="images/screening_result.png" style="zoom:33%;" />



### 3-4. Export the result

Click `Save` to export the screening result.

The key is determined by the user setting: `File Name` or `File Path`.



### 3-5. Initializing

To run screening with different libraries or parameter settings, click `Clear` to initialize the session.



## 4. Reference

OpenPharm was developed utilizing PyTorch, NumPy, Numba, BioPython, OpenBabel, Open-Source PyMol, and PyQt5.



## 5.Citation

Paper: https://arxiv.org/abs/2310.00681

If you use OpenPharm in your work, please cite: 

> Seo, S., & Kim, W. Y. (2023, December). PharmacoNet: Accelerating Large-Scale Virtual Screening by Deep Pharmacophore Modeling. In NeurIPS 2023 Workshop on New Frontiers of AI for Drug Discovery and Development.




## 6. Copyright

```
MIT License

Copyright (c) 2023 Seonghwan Seo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

