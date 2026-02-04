# Course Materials Pipeline

This repository contains a pipeline for developing and building course materials using Jupyter notebooks. The pipeline automatically generates multiple versions of notebooks and slides from source files, enabling efficient creation of both student and instructor materials.

## Overview

The `2025_BBS764` folder demonstrates a complete course materials pipeline for a Gene Regulatory Network (GRN) course module. The pipeline uses:

- **Jupyter notebooks** as source files for lectures, workshops, and homework
- **Python scripts** for data preprocessing and notebook processing
- **Make** for automated building of all course materials
- **Reveal.js slides** generated from notebooks for presentations

## Key Features

### Automatic Student/Instructor Versions

The pipeline automatically generates multiple versions from a single source:
- **Student notebooks**: Code removed, replaced with placeholders
- **Instructor notebooks**: Complete solutions
- **Progressive slides**: Fragments show solutions incrementally

### Reproducible Data Processing

All data processing is automated and documented:
- Raw data is downloaded automatically
- Processing steps are scripted and version-controlled
- Generated data is excluded from git (see `.gitignore`)

### Modular Design

Components are separated for easy reuse:
- `lib.py` - Shared functions across notebooks
- `src/*.py` - Preprocessing and generation scripts
- `Makefile` - Declarative build system

### Flexible Slide Generation

Notebooks can be converted to slides with different options:
- With or without code input
- Custom slide numbering formats
- Support for fragments and sub-slides

## Directory Structure

```
2025_BBS764/
├── Makefile                    # Build automation
├── lib.py                      # Shared library functions for notebooks
├── src/
│   ├── preproc.py             # Data preprocessing script
│   └── workshop.py            # Workshop notebook generator
├── img/                        # Images and figures for notebooks
├── run/                        # Generated data files
│   ├── raw.xlsx               # Downloaded raw data
│   └── processed.tsv.gz       # Preprocessed data
├── lecture.ipynb              # Lecture notebook (source)
├── homework.ipynb             # Homework notebook (source)
├── homework_answers.ipynb     # Homework with answers (source)
├── workshop_raw.ipynb         # Workshop notebook (source)
├── workshop_student.ipynb     # Workshop for students (generated)
├── workshop.ipynb             # Workshop with solutions (generated)
├── *.slides.html              # Generated HTML slides
├── LICENSE                    # License overview
├── LICENSE_CODE               # BSD 3-Clause for code
├── LICENSE_RESOURCE           # CC BY-NC-SA 4.0 for resources
└── COPYRIGHT                  # Copyright notice
```

## How the Pipeline Works

### 1. Data Processing

The pipeline downloads and preprocesses raw data:

```bash
make run/raw.xlsx              # Downloads raw data from BioRxiv
make run/processed.tsv.gz      # Preprocesses data using src/preproc.py
```

The preprocessing script (`src/preproc.py`):
- Reads raw Excel data from a published study
- Filters and cleans differential expression data
- Outputs a compressed TSV file for use in notebooks

### 2. Notebook Generation

Workshop notebooks are automatically generated in two versions:

```bash
make workshop_student.ipynb workshop.ipynb
```

The `src/workshop.py` script:
- Takes `workshop_raw.ipynb` as input
- Creates `workshop_student.ipynb` with code removed (placeholders for students)
- Creates `workshop.ipynb` with complete solutions
- Handles special markers:
	- `# Your code:` - Line is commented out in student version
	- `#### Your code starts here ####` / `##### Your code ends here #####` - Block is replaced with `???` in student version

### 3. Slide Generation

HTML slides are generated from notebooks using Jupyter's nbconvert:

```bash
make lecture.slides.html              # Lecture slides (no code input)
make homework.slides.html             # Homework slides (no code input)
make workshop_student.slides.html     # Workshop slides (with code placeholders)
make workshop.slides.html             # Workshop slides (with solutions)
```

- Notebooks with code input use `--to slides` (shows code)
- Lecture/homework use `--no-input` (hides code cells)
- All slides use Reveal.js with slide numbering (`c/t` format)

### 4. Build Everything

To build all materials at once:

```bash
make all          # Builds data, notebooks, and slides
make clean        # Removes downloaded data
make distclean    # Removes all generated files
```

## Using the Pipeline

### Prerequisites

```bash
# Required Python packages
pip install jupyter numpy pandas openpyxl matplotlib networkx

# Required tools
apt-get install make wget
```

### Building Course Materials

1. Navigate to the course folder:
	```bash
	cd 2025_BBS764
	```

2. Build all materials:
	```bash
	make all
	```

3. View generated slides in a browser:
	```bash
	# Open any .slides.html file in your browser
	firefox lecture.slides.html
	```

## Adapting the Pipeline for New Courses

### Step 1: Create a New Course Folder

```bash
# Copy the template structure
cp -r 2025_BBS764 2026_NEWCOURSE
cd 2026_NEWCOURSE
rm -f *.slides.html workshop_student.ipynb workshop.ipynb run/*
```

### Step 2: Customize the Makefile

Edit the `Makefile` to match your course structure:

```makefile
# Define your target files
DTARGETS_NOINPUT_SLIDES=lecture.slides.html homework.slides.html
DTARGETS_INPUT_SLIDES=workshop.slides.html
DTARGETS_NOTEBOOKS=workshop_student.ipynb workshop.ipynb

# Add custom data processing rules
run/your_data.csv:
	wget -O $@ 'your_data_url'

# Add dependencies between files
workshop.ipynb: run/your_data.csv lib.py
```

### Step 3: Customize Data Processing

Modify or create new preprocessing scripts in `src/`:

```python
# src/your_preproc.py
import argparse
import pandas as pd

parser = argparse.ArgumentParser(description='Process your data')
parser.add_argument('path_in', type=str, help='Input file path')
parser.add_argument('path_out', type=str, help='Output file path')
args = parser.parse_args()

# Your data processing logic
df = pd.read_csv(args.path_in)
# ... process data ...
df.to_csv(args.path_out, index=False)
```

Add the rule to Makefile:

```makefile
run/processed_data.csv: src/your_preproc.py run/raw_data.csv
	python3 $^ $@
```

### Step 4: Create Workshop Notebooks

For interactive workshops with student/instructor versions:

1. Create `workshop_raw.ipynb` with special markers:

	```python
	# Example cell in workshop_raw.ipynb
	
	# Your code:
	result = calculate_something(data)
	
	# Or for code blocks:
	#### Your code starts here ####
	def my_function(x):
		return x * 2
	##### Your code ends here #####
	```

2. The `src/workshop.py` script will automatically:
	- Generate `workshop_student.ipynb` with markers replaced by placeholders
	- Generate `workshop.ipynb` with complete solutions
	- Create proper slide fragments for progressive reveal

### Step 5: Create Lecture and Homework Notebooks

Create standard Jupyter notebooks with slide metadata:

```python
# In Jupyter: View -> Cell Toolbar -> Slideshow
# Set slide types: Slide, Sub-Slide, Fragment, Skip, Notes
```

For homework notebooks:
- `homework.ipynb` - Questions only
- `homework_answers.ipynb` - Questions with solutions

### Step 6: Customize Shared Library

Edit `lib.py` to include functions used across multiple notebooks:

```python
# lib.py
import numpy as np
import matplotlib.pyplot as plt

def your_shared_function(data):
	"""Reusable function for all notebooks"""
	# Your implementation
	return result
```

Import in notebooks:

```python
# In any notebook cell
from lib import your_shared_function
```

### Step 7: Update License and Copyright

1. Edit `COPYRIGHT` with your information:
	```
	Copyright (c) 2026 Your Name. All rights reserved.
	```

2. Review and update license files as needed:
	- `LICENSE_CODE` - For Python scripts, notebooks (default: BSD 3-Clause)
	- `LICENSE_RESOURCE` - For slides, images (default: CC BY-NC-SA 4.0)

### Step 8: Build and Test

```bash
make all                      # Build everything
make clean                    # Clean generated data files
make distclean                # Clean all generated files
```

## Tips and Best Practices

1. **Use the `# Your code:` marker** for single-line student exercises
2. **Use code block markers** for multi-line exercises that should be hidden
3. **Test both versions** - Build and review both student and instructor materials
4. **Version control source files only** - Add generated files to `.gitignore`
5. **Document data sources** - Include URLs and citations in preprocessing scripts
6. **Keep lib.py focused** - Only include truly shared functions
7. **Use meaningful variable names** in Makefile for clarity
8. **Test incremental builds** - Make sure dependencies are correct

## Common Customizations

### Adding a New Notebook Type

```makefile
# In Makefile, add to targets
DTARGETS_NOINPUT_SLIDES += quiz.slides.html

# Slides will be generated automatically from quiz.ipynb
```

### Changing Slide Appearance

Modify nbconvert options in Makefile:

```makefile
%.slides.html: %.ipynb
	jupyter nbconvert $< --to slides \
		--SlidesExporter.reveal_number='c/t' \
		--SlidesExporter.reveal_theme='serif' \
		--SlidesExporter.reveal_transition='fade'
```

### Adding Multiple Workshop Versions

Modify `src/workshop.py` to generate additional versions with different difficulty levels or content subsets.

## Licensing

This course materials pipeline uses a dual-license approach:

- **Code** (Python scripts, Makefiles, notebooks): BSD 3-Clause License (see `LICENSE_CODE`)
- **Resources** (slides, images, narrative content): CC BY-NC-SA 4.0 (see `LICENSE_RESOURCE`)

See individual `LICENSE*` files in each course folder for complete terms.

## Contributing

When creating new course materials:

1. Follow the existing directory structure
2. Document any new dependencies
3. Update the Makefile with new build rules
4. Include proper copyright and license notices
5. Test the complete build process

## Questions and Support

For questions about using or adapting this pipeline, please open an issue on the repository or contact the course instructor.
