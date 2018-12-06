
all: build update

clean:
	rm thumbs/*.png

trim:
	mogrify -verbose -resize '1024x>' *png

build:
	for f in *png; do convert "$$f" -thumbnail 320x -crop 320x240+0+0 "thumbs/$$f"; done

update:
	scp -r . oliver@drax:public_html/redmap-manual/


