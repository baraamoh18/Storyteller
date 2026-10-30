# Project Handoff: AI-Driven Manga/Comic Scrollytelling Website

> **Status (last updated 2026-10-30):** Stage 1 (splitting panels into layers) is mostly done with an automatic Google Colab notebook. Stages 2 to 4 have not started yet. See **Section 6: Progress So Far** for details and next steps.

## 1. Project Objective & User Profile
* **Goal:** Convert static 2D manga, manhwa, or comic panels into an interactive, animated "scrollytelling" web experience.
* **User Context:** The user prefers an **AI-first workflow** with minimal manual graphic design or coding required. The AI in this new session should provide copy-pasteable prompts for asset generation and complete, ready-to-run code blocks for implementation.

---

## 2. Reference Style & Visual Analysis
The target aesthetic and animation mechanics are inspired by an interactive graphic novel web experience ("The Notturno Experience"):

### Visual Aesthetic
* **Theme:** Neo-noir, interactive comic book / graphic novel.
* **Color Palette:** High-contrast black and white foundation punctuated by bold, flat accent colors (bright red, lime green, yellow) to direct focus.
* **Textures & Linework:** Rough, hand-drawn ink outlines and vintage halftone dot patterns.
* **Typography:** Bold, stylized retro fonts placed inside speech-bubble containers or stark rectangular comic panels.

### Scroll Animation Mechanics ("Scrollytelling")
* **User-Driven Pacing:** Animations do not play automatically; the timeline is scrubbed forward and backward in exact synchronization with the user's trackpad/mouse scroll.
* **Seamless "Zoom-Through" Transitions:** Instead of traditional page cuts, the camera zooms deeply into a specific focal point (e.g., a character's eye or a red circle), which masks and expands to reveal the background of the next scene.
* **2.5D Parallax & Depth:** Foreground (characters, speech bubbles), midground, and background layers move at different speeds along the Y/Z axes to create a sense of depth from flat 2D art.
* **Sequential Frame Motion:** Scrolling triggers frame-by-frame or continuous sequence animations (e.g., a character walking, a hand crushing an object, liquid pouring).

---

## 3. Technical Stack Recommendations
* **Framework:** React (via Vite or Next.js) or standard HTML5/CSS/JS.
* **Animation Libraries:** 
  * **GSAP (GreenSock) + ScrollTrigger:** Ideal for pinning the viewport (`pin: true`), scrubbing timelines (`scrub: true`), and orchestrating complex sequential zooms.
  * **Framer Motion (React):** Using `useScroll` to track scroll progress and `useTransform` to map scroll percentages to scale, opacity, and X/Y translations.
* **Rendering:** Standard DOM layers for simple scenes, or HTML5 Canvas / WebGL (PixiJS / Three.js) if heavy frame-by-frame sequences or depth maps are introduced.

---

## 4. The 4-Stage AI Workflow

### Stage 1: Asset Preparation (AI Graphic Pipeline)
Static comic panels must be deconstructed into separate, overlapping layers before coding.

> **Status: built and tested.** Steps 1 and 2 below are now automated by the `Split_Manga_Layers.ipynb` Colab notebook (see Section 6). The tools listed here are still useful as manual fallbacks. Steps 3 and 4 (outpainting and depth maps) have not been done yet.

1. **Layer Separation (Segmentation):** Use **Clipdrop**, **PhotoRoom**, **Meta’s Segment Anything Model (SAM)**, or **Photoshop Object Selection** to cut out foreground characters and speech bubbles as transparent PNGs.
2. **Background Inpainting (Filling the Holes):** Take the background layer (now missing the character) and use **Photoshop Generative Fill** or **Stable Diffusion Inpainting** to redraw the missing art behind the character.
   * *Suggested Prompt:* `"fill background matching manga ink style, high contrast, seamless linework"`
3. **Outpainting (Expanding Canvas Real Estate):** Use **Midjourney (Pan/Zoom)** or **DALL-E Outpainting** to extend the edges of the background panel so the virtual camera has room to pan and zoom without showing empty borders.
4. **Depth Maps (Optional 2.5D Effect):** Use **LeiaPix** or **Depth-Anything** to generate depth maps from flat layers for subtle 3D perspective shifts.

### Stage 2: Motion Choreography (Multimodal Vision AI)
Upload the separated PNG layers (background, midground, foreground character, speech bubbles) to a vision-capable LLM (like Claude or GPT-4o) to plan the timeline.

* **Choreography Prompt Template:**
  > "I have extracted [X] layers from a comic panel: [list layers, e.g., background, character, speech bubble]. Act as an interactive web art director. Write a step-by-step scroll timeline from 0% to 100% scroll progress detailing exact parallax speed ratios, camera pins, and which specific element should scale up to serve as the zoom-through transition into the next scene."

### Stage 3: Automated Code Generation (AI Coding Assistant)
Feed the choreography plan into an AI coding tool (**Claude Code**, **Cursor**, **v0.dev**, or **ChatGPT/Claude**) to generate the functional site.

* **Implementation Prompt Template:**
  > "Create a full-screen, responsive scrollytelling component using GSAP ScrollTrigger (or React + Framer Motion). Pin the container for 300vh of total scroll. Between 0% and 50% scroll, scale the background by 1.3x while translating the character layer down at 0.5x speed. Between 50% and 100%, zoom directly into the character's eye (coordinates X, Y) until it fills the viewport and crossfades into the next section. Provide the complete, working single-file code."

### Stage 4: Assembly & AI Debug Loop
1. **Preview:** Load the generated code and transparent PNG assets into an online sandbox (**CodeSandbox**, **StackBlitz**) or a local **Vite** environment.
2. **Refinement:** Iterate on timing and easing curves by pasting the code back into the AI.
   * *Debug Prompt Template:* `"Smooth out the easing curve between 40% and 60% scroll so the zoom feels continuous rather than stepped, and adjust the transform-origin so the zoom centers accurately on [target element]."`

---

## 5. Instructions for the New AI Session
When starting from this handoff document:
1. Read **Section 6: Progress So Far** first. Then confirm with the user whether they have run the layer splitter on their own panels yet, and which stage they want to work on next.
2. Guide them one step at a time—do not overwhelm them with jargon.
3. Whenever writing code, provide complete, self-contained files with clear placeholder image URLs so the user can test the scroll physics immediately before swapping in their custom manga layers.

---

## 6. Progress So Far

### Where the work happens
* The project runs in **Claude projects (cloud threads on claude.ai)**, not in GitHub's own cloud tools. Each piece of work gets its own thread.
* The GitHub repo **github.com/baraamoh18/Storyteller** is attached to the project. Code is saved there on branches, and shared files (notebook, sample results) are kept in the project's shared files folder under `layer-splitter/`.

### Stage 1: Layer splitting (largely done)
An automatic layer splitter was built and tested on Baraa's 3 sample strips.

**What it is:** a Google Colab notebook, `Split_Manga_Layers.ipynb`, that runs in the browser with nothing to install. The same tool is in the repo at `tools/layer-splitter/` (`split_layers.py`, `README.md`, `requirements.txt`) on branch `claude/project-thread-6clyex`.

**What it does, for each uploaded strip:**
1. **Splits the strip into panels** automatically by finding the gaps between them.
2. **Cuts out the characters** as `characters.png` with a see-through background. It runs two AI cutout models (BiRefNet full and BiRefNet lite) and keeps anything either one sees as a character, because each model misses different details (hair, hands, swords, arms).
3. **Finds the speech bubbles** and saves each one as a see-through PNG in a `bubbles/` folder.
4. **Fills in the background** where the characters and bubbles were, using LaMa inpainting, and saves it as `background.png`.
5. Also saves `original.png` per panel, a `layers.json` with where each layer sits on the strip, and a `preview.png` with the panels, characters and bubbles marked.

**Test results on the 3 sample strips:** it found all 6 panels and all 3 speech bubbles by itself. Character cutouts are clean. The output files are `sample-results-overview.png`, `before-after-accuracy.png` and `sample-layers.zip` in the project's `layer-splitter/` folder.

**Known limits:**
* The filled-in backgrounds look a little smudgy where the characters used to be. The characters cover those spots, so it should be fine for parallax, but large camera moves may show it.
* Sound effects drawn over the art (like "SLASH") stay in the characters layer.
* In the last sample panel, a small bit of white glow is still stuck to the character's cheek.

**Fallback options if a cutout misses something:**
* **Fix by hand in a minute:** open the `characters.png` in Photopea (free, in the browser) or Photoshop, use **Select Subject**, then **Refine Hair**.
* **Click-to-select AI (Segment Anything):** the most accurate option, but it needs one click per panel. It can be added to the notebook if the automatic results keep missing details.

**How to run the notebook:**
1. Download `Split_Manga_Layers.ipynb` to your computer.
2. Go to **colab.research.google.com** and sign in with a Google account.
3. Click **Upload** (or **File → Upload notebook**) and pick the file.
4. Click **Runtime → Change runtime type**, choose **T4 GPU**, and click Save.
5. Click **Runtime → Run all**. If it warns that the notebook isn't from Google, click **Run anyway**.
6. When the **Choose Files** button appears under Step 2, select your strip images.
7. Wait about 1 to 2 minutes per panel. Previews appear at the bottom and **layers.zip** downloads by itself.

Inside the zip, each image gets its own folder with `panel_01`, `panel_02`, and so on. Each panel folder has `characters.png` and `background.png`, and the speech bubbles are in a `bubbles` folder. Tip: try 2 or 3 strips before doing a whole chapter.

### Next steps
1. **Run the splitter on more panels** and check the cutouts. Fix any misses by hand, or add Segment Anything to the notebook if misses are common.
2. **Stage 2: Plan the scroll choreography** for the first scenes using the layers (parallax speeds, pins, zoom-through targets).
3. **Stage 3: Build the GSAP + ScrollTrigger scroll site** with the real layers, starting with placeholder images if needed.
4. Later: outpaint backgrounds and try depth maps (Stage 1, steps 3 and 4) if the camera needs more room or depth.
