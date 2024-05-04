from setuptools import setup, find_packages
from modules.openpharm import __version__

with open('./README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='openpharm',
    version=__version__,
    description='OpenPharm: Open-source Protein-based Pharmacophore Modeling Tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Seonghwan Seo',
    author_email='shwan0106@kaist.ac.kr',
    url='https://github.com/SeonghwanSeo/OpenPharm',
    packages=find_packages(where='modules'),
    package_dir={'': 'modules'},
    package_data={
        'openpharm': ['images/favicon.ico', 'images/loading_image.png', 'images/down_arrow.png', 'images/right_arrow.png']
    },
    install_requires=[
        'torch==1.13.1',
        'torchvision==0.14.1',
        'timm==0.9.12',
        'numpy>=1.26',
        'numba>=0.59',
        'omegaconf>=2.3.0',
        'molvoxel==0.1.3',
        'rdkit>=2023.9.4',
        'gdown>=5.1.0',
        'biopython>=1.83',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',

        'Development Status :: 4 - Beta',

        'Operating System :: OS Independent',

        'License :: OSI Approved :: MIT License',

        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Programming Language :: Python :: 3.10',
    ],
    entry_points={
        "console_scripts": [
            "_openpharm = openpharm.main:main",
            "openpharm = openpharm.main:run",
        ]
    },
)
