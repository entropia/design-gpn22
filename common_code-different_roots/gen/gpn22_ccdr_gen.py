#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 python3Packages.pycairo python3Packages.pyyaml

import random, sys, math, subprocess
import yaml, cairo

# nya nya mau mau mau! :3 ~jana

class design():
	def __init__(self, configfile):
		with open(configfile) as config:
			try:
				conf = yaml.load(config.read(), Loader=yaml.FullLoader)

				self.w, self.h = conf["width"], conf["height"]
				self.filename = conf["filename"]
				self.outdir = "out/"

				#self.ctx.scale(max(conf["height"], conf["width"]), max(conf["height"], conf["width"]))
				self.grid = conf["grid"]
				self.scale = conf["scale"]
				self.xnorm = min(self.w/self.h, self.h/self.w)
				self.ynorm = 1
				
				self.color_background = conf["colors"]["background"]
				self.color_segment_on = conf["colors"]["segment_on"]
				self.color_segment_off = conf["colors"]["segment_off"]
				self.color_segment_bg = conf["colors"]["segment_bg"]

				self.run_blur = conf["blur"]["blur"]
				self.blur = conf["blur"]["strength"]

				self.blurs = []

				if conf.get("roots"):
					self.root_seed = conf["roots"]["seed"]
					self.root_start = conf["roots"]["start"]
					self.root_buf = []
					self.root_depth = conf["roots"]["depth"]
					self.root_blur = conf["roots"]["blur"]

				if conf.get("segments"):
					self.segments = conf["segments"]

				if conf.get("panel"):
					self.panel = conf["panel"]
					self.panel_x = conf["panel"]["x"]
					self.panel_y = conf["panel"]["y"]
					self.panel_w = conf["panel"]["w"]
					self.panel_h = conf["panel"]["h"]

				if conf.get("texts"):
					self.texts = conf["texts"]

				if conf.get("png"):
					self.print = conf["png"]["print"]
					self.print_width = conf["png"]["width"]
					self.print_height = conf["png"]["height"]

			except yaml.YAMLError as exc:
				print(exc)

	def create_surface(self):
		self.surface = cairo.SVGSurface(self.outdir + self.filename, self.w, self.h)
		self.ctx = cairo.Context(self.surface)
		self.ctx.scale(1414, 1414)

	# Write SVG
	def save(self):
		#print("Saving", self.filename)
		self.surface.finish()
		self.surface.flush()

	# BG
	def draw_bg(self):
		self.ctx.rectangle(0, 0, self.w, self.h)
		self.ctx.set_source_rgb(*self.color_background)
		self.ctx.fill()

	# draw the non 14 segment texts
	def draw_texts(self):
		if hasattr(self, 'texts'):
			for t in self.texts:
				self.ctx.set_font_size(t["size"])
				self.ctx.select_font_face(t["font"], cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
				xbearing, ybearing, width, height, dx, dy = self.ctx.text_extents(t["string"])
				if self.h > self.w:
					self.ctx.move_to((self.xnorm*t["x"])-width/2-xbearing, (self.ynorm*t["y"])-height/2-ybearing)
				else:
					self.ctx.move_to((self.ynorm*t["x"])-width/2-xbearing, (self.xnorm*t["y"])-height/2-ybearing)
				self.ctx.set_source_rgb(*t["color"])
				self.ctx.show_text(t["string"])
				self.ctx.fill()

	# generate the 14 seg segments
	def draw_segments(self):
		if hasattr(self, 'segments'):
			for t in self.segments:
				self.draw_14_seg_chars(t["buf"], t["scaler"], t["x"], t["y"])

	# generate the background grid
	def draw_14_seg_disp_grid(self):
		if hasattr(self, 'panel'):
			for x in range(self.panel_x, self.panel_w):
				for y in range(self.panel_y, self.panel_h):
					if self.h > self.w:
						self.draw_14_seg_disp(self.xnorm/(self.grid[0])*x, self.ynorm/(self.grid[1])*y, self.scale, " ")
					else:
						self.draw_14_seg_disp(self.ynorm/(self.grid[0])*x, self.xnorm/(self.grid[1])*y, self.scale, " ")

	# char drawing aligner and helper
	def draw_14_seg_chars(self, chars, scaler, offx = 0, offy = 0):
		for x in range(self.grid[0]):
			for y in range(self.grid[1]):
				for i in range(len(chars)):
					if x == chars[i][0] and y == chars[i][1]:
						if self.h > self.w:
							self.draw_14_seg_disp(self.xnorm/(self.grid[0])*(x*scaler)+self.xnorm/self.grid[0]*offx, self.ynorm/(self.grid[1])*y+self.xnorm/self.grid[1]*offy, self.scale*scaler, chars[i][2])
						else:
							self.draw_14_seg_disp(self.ynorm/(self.grid[0])*(x*scaler)+self.ynorm/self.grid[0]*offx, self.xnorm/(self.grid[1])*y+self.ynorm/self.grid[1]*offy, self.scale*scaler, chars[i][2])

	# Render the 14 seg display
	def draw_14_seg_disp(self, x, y, scale, character, rotate = False):
		# normals
		xn, yn = self.xnorm*scale, self.ynorm*scale

		# segment background rectangle
		#self.ctx.rectangle(x, y, xn+0.001, yn+0.001)
		self.ctx.rectangle(x, y, xn, yn)
		self.ctx.set_source_rgb(*self.color_segment_bg)
		self.ctx.fill()

		# font
		self.ctx.set_font_size(scale*0.7)
		self.ctx.select_font_face("DSEG14 Modern", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		xbearing, ybearing, width, height, dx, dy = self.ctx.text_extents("~")
				
		# ~ (unlit segments)
		self.ctx.set_source_rgb(*self.color_segment_off)
		self.ctx.move_to(x+xn/2-width/2-xbearing, y+yn/2-height/2-ybearing)
		self.ctx.show_text("~")
		self.ctx.fill()
		self.ctx.set_source_rgb(*self.color_segment_off)
		self.ctx.move_to(x+xn/2-width/2-xbearing, y+yn/2-height/2-ybearing)
		self.ctx.show_text(".")
		self.ctx.fill()

		# lit segments
		self.ctx.set_source_rgb(*self.color_segment_on)
		if character != "Y": #not rotate:
			self.ctx.move_to(x+xn/2-width/2-xbearing, y+yn/2-height/2-ybearing)
			self.ctx.show_text(character)
		else:
			self.ctx.move_to(x+xn/2+width/2+xbearing, y+yn/2+height/2+ybearing)
			self.ctx.save()
			self.ctx.rotate(180*(3.141/180))
			self.ctx.show_text(character)
			self.ctx.restore()

		self.ctx.fill()


	# root generator, kind of L-System, but just kind of..
	def gen_root(self):
		# lets generate some roots
		# "char", x rule, [y rules, next char (hacky weighted random)]
		rules = {	"|" : [1, [[0, "YYYYYYYYYYYY\\\\//()()| "]]],
					"Y" : [1, [[1, "\\\\\\)))||| '"],
							   [-1, "///(((||| '"]]],
					"\\": [1, [[1, "YYYY//(((||| '"]]],
					"/" : [1, [[-1, "YYYY\\\\)))||| '"]]],
					")" : [1, [[-1, "YYYY///(((||| "]]],
					"(" : [1, [[1, "YYYY\\\\\\)))||| "]]],
					"'" : [1, []],
					" " : [1, []],
					"start": [0, [[0, "()()|||||//\\\\Y|"]]]}

		for i in range(len(self.root_start)):
			axiom = [self.root_start[i], 0, random.choice(rules["|"][1][0][1])]
			alive = True
			random.seed(self.root_seed[i] if self.root_seed[i] != "" else random.randbytes(7))
			self.root_buf.append(axiom)
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
					self.root_buf.append(new_root)
				
				if new_y > self.root_depth or head == []:
					alive = False

		return self.root_buf

	# Okay, okay, I know, this is reaaaaaaly hacky
	# we are inserting a blur filter with the url #f1 into <defs> here
	# then we are looking for all the lines containing the segment on color
	# we duplicate them all into one <g> and append it
	# the <g> will be linked to #f1
	# finally we will remove the main group from cairo
	def do_the_hacky_whacky_svg_blur(self):
		#print("Modifying SVG", self.outdir + self.filename," >:3")
		
		svg = open(self.outdir + self.filename, 'r')
		text = [x for x in svg.read().splitlines() if x]

		filt = "<filter id=\"f1\" x=\"0\" y=\"0\">\n<feGaussianBlur in=\"SourceGraphic\" stdDeviation=\"{0:g} {1:g}\" />\n</filter>".format(self.blur, self.blur)
		new_group = ["<g style=\"fill:rgb({0:.1f}%,{1:.1f}%,{2:.1f}%);fill-opacity:1;filter:url(#f1)\">".format(self.color_segment_on[0]*100,self.color_segment_on[1]*100,self.color_segment_on[2]*100)]

		found_blur = False

		for k, l in enumerate(text):
			if "<defs>" in l:
				text.insert(k+1, filt)

			if "<g id=\"surface" in l:
				text.pop(k)

			if "<g style=\"fill:rgb({0:.1f}%,{1:.1f}%,{2:.1f}%);fill-opacity:1;\">".format(self.color_segment_on[0]*100,self.color_segment_on[1]*100,self.color_segment_on[2]*100).replace(".0", "") in l:
				new_group.append(text[k  ])
				new_group.append(text[k+1])
				new_group.append(text[k+2])
				found_blur = True

			if "</svg>" in l:				
				new_group.append("</g>")

		text.pop(len(text)-2)

		if found_blur == False:
			print("couldn't find blur in " + self.filename)
			print("rgb({0:.1f}%,{1:.1f}%,{2:.1f}%)".format(self.color_segment_on[0]*100,self.color_segment_on[1]*100,self.color_segment_on[2]*100).replace(".0", ""))

		out = open(self.outdir + self.filename, 'w')
		
		out.write("\n".join(text[:-1] + new_group + text[-1:]))

		out.close()
		svg.close()

	def render_svg_to_png(self):
		#print("Rendering " + self.filename + " to png")

		subprocess.run(["inkscape", '--export-type=png', \
						f'--export-filename={"out/png/" + self.filename[:-4]}', \
						f'--export-width={self.print_width}', f'--export-height={self.print_height}', \
						self.outdir + self.filename])

if __name__ == "__main__":
	args = sys.argv[1:]
	if args:
		for a in args:
			gpn22 = design(a)
			gpn22.draw_bg()
			gpn22.draw_14_seg_disp_grid()
			gpn22.draw_14_seg_chars(gpn22.gen_root(), 1)
			gpn22.draw_segments()
			gpn22.draw_texts()
			gpn22.save()
			if gpn22.run_blur:
				gpn22.do_the_hacky_whacky_svg_blur()
			if gpn22.print:
				gpn22.render_svg_to_png()
	else:
		print("Usage: python gpn22_ccdr_gen.py <config> <config> <...>")

	exit()