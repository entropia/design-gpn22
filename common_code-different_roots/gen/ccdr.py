#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 python3Packages.pycairo

import time, random, sys, math
import cairo

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
	ctx.move_to(x+xn/2-width/2-xbearing, y+yn/2-height/2-ybearing)
	ctx.show_text(character)
	ctx.fill()

# nya
WIDTH, HEIGHT = 1000, 1414
surface = cairo.SVGSurface("gpn22_ccdr.svg", WIDTH, HEIGHT)
ctx = cairo.Context(surface)
ctx.scale(HEIGHT, HEIGHT)

# PCB
ctx.rectangle(0, 0, 1, 1)
ctx.set_source_rgb(0.0, 0.1765, 0.01569)
ctx.fill()

# write common code() different roots
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
ictx = cairo.Context(interm)
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

surface.finish()
surface.flush()

# hacky whacky stuff, search and replace on svg


#svg = open("gpn22_ccdr.svg")
