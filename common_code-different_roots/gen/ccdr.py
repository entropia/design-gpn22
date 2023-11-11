#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 python3Packages.pycairo

import time, random, sys, math
import cairo

# nya nya mau mau mau! :3 ~jana

def draw_14_seg_disp(ctx, x, y, scale, col, character):
	# normals
	xn, yn = 0.707108562*scale, 1*scale

	# rect
	ctx.rectangle(x, y, xn, yn)
	ctx.set_source_rgb(0.1, 0.2, 0.19)
	ctx.fill()
	ctx.set_source_rgb(0.408, 0.52, 0.51)
	ctx.set_line_width(0.2)
	ctx.stroke()

	# ~ (background, unlit segments)
	ctx.set_source_rgb(0.16, 0.3, 0.29)
	ctx.set_font_size(scale*0.7)
	ctx.select_font_face("DSEG14 Modern",
					 cairo.FONT_SLANT_NORMAL,
					 cairo.FONT_WEIGHT_NORMAL)
	xbearing, ybearing, width, height, dx, dy = ctx.text_extents("~")
	ctx.move_to(x+xn/2-width/2-xbearing, y+yn/2-height/2-ybearing)
	ctx.show_text("~")
	ctx.fill()

	# lit char
	ctx.set_source_rgb(*col)
	ctx.set_font_size(scale*0.7)
	ctx.select_font_face("DSEG14 Modern",
					 cairo.FONT_SLANT_NORMAL,
					 cairo.FONT_WEIGHT_NORMAL)
	xbearing, ybearing, width, height, dx, dy = ctx.text_extents(character)
	if(character != "Y"):
		ctx.move_to(x+xn/2-width/2-xbearing, y+yn/2-height/2-ybearing)
		ctx.show_text(character)
	else:
		ctx.move_to(x+xn/2+width/2+xbearing, y+yn/2+height/2+ybearing)
		ctx.save()
		ctx.rotate(180*(3.141/180))
		ctx.show_text(character)
		ctx.restore()
	ctx.fill()


# nya
print("Generating Display")
WIDTH, HEIGHT = 1000, 1414
surface = cairo.SVGSurface("gpn22_ccdr.svg", WIDTH, HEIGHT)
ctx = cairo.Context(surface)
ctx.scale(HEIGHT, HEIGHT)

# BG
ctx.rectangle(0, 0, 1, 1)
ctx.set_source_rgb(0.165, 0.165, 0.165)
ctx.fill()

# lets generate some roots
root_str = [[0, 0, ""]]
seed = ["alerta", "anti", "fascista~"]
start = [2, 11, 15]
# "char", x rule, [y rules, follow]
rules = {	"|" : [1, [[0, "YYYYYYYYYYYY\\\\//()()| "]]],
			"Y" : [1, [[1, "\\\\\\)))||| '"],
					   [-1, "///(((||| '"]]],
			"\\": [1, [[1, "YYYY//(((||| '"]]],
			"/" : [1, [[-1, "YYYY\\\\)))||| '"]]],
			"'" : [1, []],
			" " : [1, []],
			")" : [1, [[-1, "YYYY///(((||| "]]],
			"(" : [1, [[1, "YYYY\\\\\\)))||| "]]]}

for i in range(len(start)):
	axiom = [start[i], 0, "|"]
	alive = True
	random.seed(seed[i])
	root_str.append(axiom)
	head = [axiom]

	while head and alive:
		t = head[0]
		head.pop(0)
		r = rules[t[2]]
		new_y = t[1]+r[0]

		for b in r[1]:
			new_x = b[0] + t[0]
			opt_len = len(b[1])
			new_char = b[1][random.randint(0, opt_len-1)]
			new_root = [new_x, new_y, new_char]
			head.append(new_root)
			root_str.append(new_root)
		
		if(new_y > 8 or head == []):
			alive = False



# write common code() different roots, append roots
ccdr_str = [[ 2,14,"C"],
			[ 3,14,"O"],
			[ 4,14,"M"],
			[ 5,14,"M"],
			[ 6,14,"O"],
			[ 7,14,"N"],

			[ 9,14,"C"],
			[10,14,"O"],
			[11,14,"D"],
			[12,14,"E"],
			[13,14,"("],
			[14,14,")"],

			[ 3,15,"D"],
			[ 4,15,"I"],
			[ 5,15,"F"],
			[ 6,15,"F"],
			[ 7,15,"E"],
			[ 8,15,"R"],
			[ 9,15,"E"],
			[10,15,"N"],
			[11,15,"T"],

			[13,15,"R"],
			[14,15,"O"],
			[15,15,"O"],
			[16,15,"T"],
			[17,15,"S"]]

ccdr_str = root_str + ccdr_str
_x,_y,_scale = 20, 18, 0.05

for x in range(_x):
	for y in range(_y):
		draw_14_seg_disp(ctx, 0.707108562/_x*x, 1/(_y+2)*y, _scale, (0.0, 0.996, 0.71), " ")
		for i in range(len(ccdr_str)):
			if(x == ccdr_str[i][0] and y == ccdr_str[i][1]):
				draw_14_seg_disp(ctx, 0.707108562/_x*x, 1/(_y+2)*y, _scale, (0.0, 0.996, 0.71), ccdr_str[i][2])

# write GPN-22
gpn22_str = ["G", "P", "N", "-", "2", "2"]

for x in range(len(gpn22_str)):
	draw_14_seg_disp(ctx, 0.707108562/_x*(x*3)+0.707108562/_x, 1/(_y+2)*10, _scale*3, (0.0, 0.996, 0.71), gpn22_str[x]) #0.707108562/10*x+0.707108562/10*2.5

# footer - this does just not work, wtf
'''
footer = cairo.ImageSurface.create_from_png("gpn22_footer.png")
w, h = footer.get_width(), footer.get_height()
print(w,h,WIDTH, HEIGHT)
interm = cairo.ImageSurface(cairo.FORMAT_ARGB32, w,h)
ictx = cairo.Context(inte
rm)
ictx.set_source_surface(footer, -300, -10)
print(interm.get_width(),interm.get_height())
ictx.paint()
#w, h = footer.get_width(), footer.get_height()
#stride = cairo.ImageSurface.format_stride_for_width (cairo.FORMAT_ARGB32, w)
#footer = cairo.ImageSurface.create_for_data(fdata, cairo.FORMAT_ARGB32, w, h,stride)
#ctx.rectangle(0, 1/20*18, 1, 1/20*2)
ctx.set_source_surface(interm, 0, 0)
ctx.paint()
'''

# Write SVG
print("Writing SVG")
surface.finish()
surface.flush()

# hacky whacky stuff, search and replace on svg to add filters and such
exit() # do not do this for now, it just does not work well (yet >:3)
# please open the output file in inkscape
# 1. mark everything and ungroup it
# 2. click on 1 bright green char, marking it
# 3. right click → slect same → same fill color, all bright chars should be selected now
# 4. duplicate and place exactly on old chars, keep selection active(!)
# 5. go to filters → Blurs → Blur and select 20 20, apply
# 6. all chars should glow now
# 7. place footer, it uses the font NewStroke, which I couldn't get as ttf, just as .c/.h files

print("Modifying SVG")
svg = open("gpn22_ccdr.svg.raw", 'r')

# Blur
text = [x for x in svg.read().splitlines() if x]

filt = "<filter id=\"f1\" x=\"0\" y=\"0\">\n<feGaussianBlur in=\"SourceGraphic\" stdDeviation=\"20 20\" />\n</filter>"
filt_handle = "<g style=\"fill:rgb(0%,99.6%,71%);fill-opacity:1;filter:url(#f1)\">"

for k, l in enumerate(text):
	if("<defs>" in l):
		text.insert(k+1, filt)

	if("<g style=\"fill:rgb(0%,99.6%,71%);fill-opacity:1;\">" in l):
		text.insert(k+3, filt_handle)
		text.insert(k+4, text[k+1])
		text.insert(k+5, text[k+2])


out = open("gpn22_ccdr.svg", 'w')
out.write("\n".join(text))
out.close()
svg.close()
