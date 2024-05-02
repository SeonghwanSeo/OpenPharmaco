# OpenPharm: Open-source Protein-based Pharmacophore Modeling

Open-source GUI software for **Fully-automated Protein-based Pharmacophore Modeling** for the ultra-large-scale virtual screening.

<img src="openpharm/gui/images/favicon_transparent.png" alt="OpenPharm Logo" height="100">

OpenPharm is currently powered by ***PharmacoNet: Accelerating Large-Scale Virtual Screening by Deep Pharmacophore Modeling***, developed by Seonghwan Seo, KAIST.

If you are terminal user or developer (ex. Deep Learning developer), please visit PharmacoNet Project [[github](https://github.com/SeonghwanSeo/PharmacoNet)]. I plan to provide more flexible functionality.

If you have any problems or need help, please add an github issue.

## Quick Start

```bash
# Download Pre-trained Model
git clone https://github.com/SeonghwanSeo/OpenPharm.git

# Create Environment
cd OpenPharm/
conda env create -f environment.yml
conda activate openpharm
python setup.py install

# Start
openpharm
python openpharm/main.py
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



# Future Plan

- Version 2.0.0
  - Performance Improvement (Provisional: PharmacoNet v2)
  - Binding Affinity Prediction
  - SMILES Input
- Verison 2.1.0:
  - Binding Site Detection for Apo Protein Structures
  - Pharmacophore Customizing
- Version 3
  - Binding Pose Prediction
