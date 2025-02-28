TARGETS=lecture.slides.html homework.slides.html

all: $(TARGETS)

$(TARGETS): %.slides.html: %.ipynb
	jupyter nbconvert $< --to slides --no-input --SlidesExporter.reveal_number='c/t'
#jupyter nbconvert 1.ipynb --to slides --post serve --SlidesExporter.reveal_number='c/t'
