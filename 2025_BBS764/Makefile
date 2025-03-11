TARGETS_DATA=run/raw.xlsx
DTARGETS_INPUT_SLIDES=workshop.slides.html workshop_student.slides.html
DTARGETS_NOINPUT_SLIDES=lecture.slides.html homework.slides.html homework_answers.slides.html
DTARGETS_SLIDES=$(DTARGETS_INPUT_SLIDES) $(DTARGETS_NOINPUT_SLIDES)
DTARGETS_NOTEBOOKS=workshop_student.ipynb workshop.ipynb
DTARGETS_DATA=run/processed.tsv.gz

TARGETS=$(TARGETS_DATA)
DATA_TARGETS=$(DTARGETS_SLIDES) $(DTARGETS_DATA) $(DTARGETS_NOTEBOOKS)

all: $(TARGETS) $(DATA_TARGETS)

$(DTARGETS_INPUT_SLIDES): %.slides.html: %.ipynb
	jupyter nbconvert $< --to slides --SlidesExporter.reveal_number='c/t'

$(DTARGETS_NOINPUT_SLIDES): %.slides.html: %.ipynb
	jupyter nbconvert $< --to slides --no-input --SlidesExporter.reveal_number='c/t'

run/raw.xlsx:
	wget -q -O $@ 'https://www.biorxiv.org/content/biorxiv/early/2023/10/24/2023.09.17.557749/DC1/embed/media-1.xlsx?download=true'

run/processed.tsv.gz: src/preproc.py run/raw.xlsx
	python3 $^ $@

workshop_student.ipynb workshop.ipynb: src/workshop.py workshop_raw.ipynb
	python3 $^ workshop_student.ipynb workshop.ipynb

clean:
	rm -f $(TARGETS)

distclean: clean
	rm -rf $(DTARGETS)
