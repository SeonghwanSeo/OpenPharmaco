# PharmacoGUI: Open-source Protein-based Pharmacophore Modeling Software

 <img src="images/logo.png" alt="OpenPharm Logo" height="160">

Open-source GUI software for ***Fully-automated Protein-based Pharmacophore Modeling*** for the ultra-large-scale virtual screening.

PharmacoGUI is currently powered by ***PharmacoNet: Accelerating Large-Scale Virtual Screening by Deep Pharmacophore Modeling***, developed by Seonghwan Seo, KAIST.

If you are terminal user or developer (ex. Deep learning researcher), please visit PharmacoNet Project [[github](https://github.com/SeonghwanSeo/PharmacoNet)].
It provides more functionality.

If you have any problems or need help, please add an github issue.

You can get more information at [Wiki](https://github.com/SeonghwanSeo/OpenPharm/wiki).

\* Tested on Microsoft Window and Mac OS X (Apple Silicon).



## Quick Start

```bash
# Download Pre-trained Model
git clone https://github.com/SeonghwanSeo/PharmacoGUI.git

# Create Environment
cd PharmacoGUI/
conda env create -f environment.yml
conda activate pmgui
pip install .

# Start
conda activate pmgui
pmgui
```



## Citation

Paper on [arxiv](https://arxiv.org/abs/2310.00681)

```
@article{seo2023pharmaconet,
  title = {PharmacoNet: Accelerating Large-Scale Virtual Screening by Deep Pharmacophore Modeling},
  author = {Seo, Seonghwan and Kim, Woo Youn},
  journal = {arXiv preprint arXiv:2310.00681},
  year = {2023},
  url = {https://arxiv.org/abs/2310.00681},
}
```



## Future Plan

- Version 2.0.0
  - Performance Improvement (Provisional: PharmacoNet v2)
  - Binding Affinity Prediction
  - SMILES Input
- Verison 2.1.0:
  - Binding Site Detection for Apo Protein Structures
  - Pharmacophore Customizing
- Version 3
  - Binding Pose Prediction



## Reference

- [PyTorch](https://pytorch.org)
- [NumPy](https://numpy.org)
- [Biopython](http://biopython.org)
- [Open Babel](http://openbabel.org)
- [Open-Source PyMOL](http://pymol.org) ([github](https://github.com/schrodinger/pymol-open-source))
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
