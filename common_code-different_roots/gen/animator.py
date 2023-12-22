#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 python3Packages.pycairo python3Packages.pyyaml python3Packages.colour

from gpn22_ccdr_gen import design
import sys, math, random
from colour import Color

# made in agony (no, actaully it was fun)

FPS = 30
SEC = 10
frames = SEC*FPS

#
# build keyframes
#

# [frame, action, values]
keyframes = []

# fade in
off_on_frames = 20
on = Color(rgb=(0.0, 0.996, 0.71))
off = Color(rgb=(0.16, 0.3, 0.29))
off_to_on = list(off.range_to(on, off_on_frames))

for i in range(off_on_frames):
	keyframes.append([i+0, "set_segment_color", tuple(map(lambda x: round(x, 3), off_to_on[i].rgb))])

# heartbeat
hb_start = off_on_frames
hb_frames = 280
hb_high_color = Color(rgb=(0.0, 0.996, 0.71))
hb_low_color = Color(rgb=(0.0501, 0.8614, 0.6559))
hb_blur_center = 40
hb_blur_jitter = 3
hb_color_shift_len = 100
hb_color_grad = list(hb_high_color.range_to(hb_low_color, int(hb_color_shift_len/2))) + 
				list(hb_low_color.range_to(hb_high_color, int(hb_color_shift_len/2)))

for i in range(hb_frames):
	keyframes.append([i+hb_start, "set_segment_color", 
						tuple(map(lambda x: round(x, 3), hb_color_grad[i % hb_color_shift_len].rgb))])
	keyframes.append([i+hb_start, "set_segment_blur", (math.sin(i/100)*hb_blur_jitter)+hb_blur_center])

# roots
root_start = 220
root_advance = 3
root_max = 20
root_cnt = 0
root_sp = [7,3,11,23,12,26,16,14,17,25,19,15,1,4,18,27,22,5,0,24,6,13,8,2,9,20,21,10,22,14,9,5,24,20,1,21,18,13,26,19,8,3,2,25,10,27,12,15,4,6,16,11,7,23,0,17]
roots_pre = []
roots = []

keyframes.append([root_start, "generate_roots", 0])

# fade out
on_off_frames = 11
on_seg = Color(rgb=(0.0, 0.996, 0.71))
on_1 = Color(rgb=(0.16, 0.3, 0.29))
on_2 = Color(rgb=(0.1, 0.2, 0.19))
off = Color(rgb=(0.16, 0.3, 0.29))
on_to_off_seg = list(on_seg.range_to(off, on_off_frames))
on_to_off_1 = list(on_1.range_to(off, on_off_frames))
on_to_off_2 = list(on_2.range_to(off, on_off_frames))

for i in range(on_off_frames):
	keyframes.append([289+i, "set_segment_color", tuple(map(lambda x: round(x, 3), on_to_off_seg[i].rgb))])
	keyframes.append([289+i, "set_1_color", tuple(map(lambda x: round(x, 3), on_to_off_1[i].rgb))])
	keyframes.append([289+i, "set_2_color", tuple(map(lambda x: round(x, 3), on_to_off_2[i].rgb))])

#
# render SVGs based on keyframes
#
# afterwards convert SVGs to pngs via
#
'''
	#!/bin/bash
	for file in *.svg; do
	    filename=$(basename "$file")
	    inkscape "$file" --export-type=png --export-width=1920 --export-height=1080 --export-area=0:136:1885:1196 -o "png/${filename%.svg}.png"
	done
'''
# 
# and convert pngs to gif via
#
# gifski -r 30 -W 1920 -H 1080 -o gpn22_congress_infobeamer_1080p_final.gif congress_info*.png
#

if __name__ == "__main__":
	
	for n in range(frames):
		gpn22 = design(sys.argv[1])
		gpn22.filename = "congress_info" + str(n) + ".svg"
		gpn22.outdir = "out/anim/"
		gpn22.create_surface()

		for kf in keyframes:
			if kf[0] == n:
				if kf[1] == "set_segment_color":
					gpn22.color_segment_on = kf[2]
				if kf[1] == "set_1_color":
					gpn22.color_segment_off = kf[2]
				if kf[1] == "set_2_color":
					gpn22.color_segment_bg = kf[2]
				if kf[1] == "set_segment_blur":
					gpn22.blur = kf[2]
				if kf[1] == "generate_roots":
					_pre = []
					for i in root_sp:
						gpn22.root_start = [i]
						gpn22.root_seed = [random.randbytes(7)]
						gpn22.root_buf = []
						root_start += root_advance
						roots_pre.append([root_start, 0, gpn22.gen_root()])

		if roots_pre:
			for r in roots_pre:
				if n % 2 == 0:
					if n > r[0]:
						for c in r[2]:
							if r[1] == c[1]:
								roots.append(c)
						r[1] += 1


		gpn22.draw_bg()
		gpn22.draw_14_seg_disp_grid()
		gpn22.draw_segments()
		gpn22.draw_14_seg_chars(roots, 1)
		gpn22.save()
		if gpn22.run_blur:
			gpn22.do_the_hacky_whacky_svg_blur()
		if gpn22.print:
			gpn22.render_svg_to_png()
	exit()