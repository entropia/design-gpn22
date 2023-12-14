#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 python3Packages.pycairo python3Packages.pyyaml

import random, sys, math
import yaml
import cairo

# nya nya mau mau mau! :3 ~jana

class design():
	def __init__(self, configfile):
		with open(configfile) as config:
			try:
				conf = yaml.load(config.read(), Loader=yaml.FullLoader)

				self.w, self.h = conf["width"], conf["height"]
				self.filename = conf["filename"]
				self.surface = cairo.SVGSurface("out/" + self.filename, conf["width"], conf["height"])
				self.ctx = cairo.Context(self.surface)
				#self.ctx.scale(max(conf["height"], conf["width"]), max(conf["height"], conf["width"]))
				self.ctx.scale(1414, 1414)
				self.grid = conf["grid"]
				self.grid_padding = conf["grid_padding"]
				self.scale = conf["scale"]
				self.xnorm = min(self.w/self.h, self.h/self.w)
				self.ynorm = 1
				
				self.color_background = conf["color"]["background"]
				self.color_segment_on = conf["color"]["segment_on"]
				self.color_segment_off = conf["color"]["segment_off"]
				self.color_segment_bg = conf["color"]["segment_bg"]

				self.root_seed = conf["root"]["seed"]
				self.root_start = conf["root"]["start"]
				self.root_buf = [[0, 0, ""]]
				self.root_depth = conf["root"]["depth"]

				self.texts = conf["text"]

				print(self.xnorm, self.ynorm)

			except yaml.YAMLError as exc:
				print(exc)

	# Write SVG
	def save(self):
		print("Saving", self.filename)
		self.surface.finish()
		self.surface.flush()

	# BG
	def draw_bg(self):
		self.ctx.rectangle(0, 0, self.w, self.h)
		self.ctx.set_source_rgb(*self.color_background)
		self.ctx.fill()

	# generate the 14 seg texts
	def draw_texts(self):
		if self.texts:
			for t in self.texts:
				self.draw_14_seg_chars(t["buf"], t["scaler"], t["x"], t["y"])

	# generate the background grid
	def draw_14_seg_disp_grid(self):	
		for x in range(self.grid[0]):
			for y in range(self.grid[1]):
				if self.h > self.w:
					self.draw_14_seg_disp(self.xnorm/(self.grid[0]+self.grid_padding[0])*x, self.ynorm/(self.grid[1]+self.grid_padding[1])*y, self.scale, " ")
				else:
					self.draw_14_seg_disp(self.ynorm/(self.grid[0]+self.grid_padding[0])*x, self.xnorm/(self.grid[1]+self.grid_padding[1])*y, self.scale, " ")

	# char drawing aligner and helper
	def draw_14_seg_chars(self, chars, scaler, offx = 0, offy = 0):
		for x in range(self.grid[0]):
			for y in range(self.grid[1]):
				for i in range(len(chars)):
					if x == chars[i][0] and y == chars[i][1]:
						if self.h > self.w:
							self.draw_14_seg_disp(self.xnorm/(self.grid[0]+self.grid_padding[0])*(x*scaler)+self.xnorm/self.grid[0]*offx, self.ynorm/(self.grid[1]+self.grid_padding[1])*y+self.xnorm/self.grid[1]*offy, self.scale*scaler, chars[i][2])
						else:
							self.draw_14_seg_disp(self.ynorm/(self.grid[0]+self.grid_padding[0])*(x*scaler)+self.ynorm/self.grid[0]*offx, self.xnorm/(self.grid[1]+self.grid_padding[1])*y+self.ynorm/self.grid[1]*offy, self.scale*scaler, chars[i][2])

	# Render the 14 seg display
	def draw_14_seg_disp(self, x, y, scale, character, rotate = False):
		# normals
		xn, yn = self.xnorm*scale, self.ynorm*scale #min(self.xnorm, 1)*scale, max(self.xnorm, 1)*scale # dinA* 
		
		# segment background rectangle
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

		# lit segments
		self.ctx.set_source_rgb(*self.color_segment_on)
		if not rotate:
			self.ctx.move_to(x+xn/2-width/2-xbearing, y+yn/2-height/2-ybearing)
			self.ctx.show_text(character)
		else:
			self.ctx.move_to(x+xn/2+width/2+xbearing, y+yn/2+height/2+ybearing)
			self.ctx.save()
			self.ctx.rotate(180*(3.141/180))
			self.ctx.show_text(character)
			self.ctx.restore()

		self.ctx.fill()

	# root generator, kind of L-System, but just kind of
	def gen_root(self):
		# lets generate some roots
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

		for i in range(len(self.root_start)):
			axiom = [self.root_start[i], 0, "|"]
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

if __name__ == "__main__":
	args = sys.argv[1:]
	if args:
		for a in args:
			gpn22 = design(a)
			gpn22.draw_bg()
			gpn22.draw_14_seg_disp_grid()
			gpn22.draw_14_seg_chars(gpn22.gen_root(), 1)
			gpn22.draw_texts()
			gpn22.save()
	else:
		print("Usage: python gpn22_ccdr_gen.py <config> <config> <...>")

	exit()


# hacky whacky stuff, search and replace on svg to add filters and such
 # do not do this for now, it just does not work well (yet >:3)
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
