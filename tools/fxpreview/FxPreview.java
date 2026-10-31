import static org.lwjgl.opengl.GL33.*;

import java.awt.image.BufferedImage;
import java.io.File;
import java.nio.ByteBuffer;
import java.nio.FloatBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import javax.imageio.ImageIO;

import org.lwjgl.BufferUtils;
import org.lwjgl.glfw.GLFW;
import org.lwjgl.opengl.GL;

/**
 * Compiles the real spell_fx.fsh in a hidden window and draws each of its modes at a few points of their life, on a dark
 * and a bright ground, into a sheet. The game needn't run: a bad shader fails here, and what comes out is what the shader
 * draws. tools/fxpreview/run.sh runs it.
 */
public class FxPreview {
	static final int CELL = 200, COLS = 6;
	static final float[] LIFE = {0.03f, 0.12f, 0.28f, 0.5f, 0.72f, 0.9f};
	static final float[][] TINT = {{1f, 0.48f, 0.17f}, {0.55f, 1f, 0.7f}, {0.47f, 0.72f, 1f}, {0.6f, 0.3f, 0.9f}, {1f, 0.78f, 0.31f}, {0.88f, 0.12f, 0.17f}};
	static final List<float[]> VERTS = new ArrayList<>();

	/** position, colour, uv, mode and param */
	static void vert(float x, float y, float[] c, float a, float u, float v, int mode, int param) {
		VERTS.add(new float[] {x, y, 0, c[0], c[1], c[2], a, u, v, mode, param});
	}

	/** A frame of the atlas's FLAME flipbook, as SpellParticles' frame() picks it. */
	static void atlas(float x, float y, float w, float h, float[] c, int sheet, int f, int mode, int param) {
		float cell = 1 / 8f, u = 0.5f + (f % 4) * cell, v = (Math.min(f, 15) / 4) * cell;
		vert(x, y, c, 1, u, v + cell, mode, param);
		vert(x + w, y, c, 1, u + cell, v + cell, mode, param);
		vert(x + w, y + h, c, 1, u + cell, v, mode, param);
		vert(x, y, c, 1, u, v + cell, mode, param);
		vert(x + w, y + h, c, 1, u + cell, v, mode, param);
		vert(x, y + h, c, 1, u, v, mode, param);
	}

	static void quad(float x, float y, float w, float h, float[] c, float a, int mode, int param) {
		vert(x, y, c, a, -1, 1, mode, param);
		vert(x + w, y, c, a, 1, 1, mode, param);
		vert(x + w, y + h, c, a, 1, -1, mode, param);
		vert(x, y, c, a, -1, 1, mode, param);
		vert(x + w, y + h, c, a, 1, -1, mode, param);
		vert(x, y + h, c, a, -1, -1, mode, param);
	}

	/** A crescent as client/FxKit's Slash draws it. */
	static void slash(float cx, float cy, float rad, float wide, float from, float to, float k, float[] c, int param) {
		final int STEPS = 40;
		float head = 1 - (1 - Math.min(1, k * 3)) * (1 - Math.min(1, k * 3)), tail = 0;
		for (int i = 0; i < STEPS; i++) {
			float t0 = i / (float) STEPS, t1 = (i + 1) / (float) STEPS;
			float a0 = from + (to - from) * t0 * head, a1 = from + (to - from) * t1 * head;
			float w0 = wide * (float) Math.sin(t0 * Math.PI * 0.92 + 0.1), w1 = wide * (float) Math.sin(t1 * Math.PI * 0.92 + 0.1);
			float[] p = {cx + (float) Math.cos(a0) * (rad - w0), cy + (float) Math.sin(a0) * (rad - w0)}, q = {cx + (float) Math.cos(a0) * (rad + w0 * 0.3f), cy + (float) Math.sin(a0) * (rad + w0 * 0.3f)};
			float[] r = {cx + (float) Math.cos(a1) * (rad + w1 * 0.3f), cy + (float) Math.sin(a1) * (rad + w1 * 0.3f)}, s = {cx + (float) Math.cos(a1) * (rad - w1), cy + (float) Math.sin(a1) * (rad - w1)};
			float y0 = t0, y1 = t1;
			vert(p[0], p[1], c, 1, -1, y0, 9, param);
			vert(q[0], q[1], c, 1, 1, y0, 9, param);
			vert(r[0], r[1], c, 1, 1, y1, 9, param);
			vert(p[0], p[1], c, 1, -1, y0, 9, param);
			vert(r[0], r[1], c, 1, 1, y1, 9, param);
			vert(s[0], s[1], c, 1, -1, y1, 9, param);
		}
	}

	/** A pillar seen side on: the tube's front half, faded towards its edges as FxKit's Tube does. */
	static void tube(float x, float y, float w, float h, float[] c, float k, int param) {
		final int ROUND = 24, UP = 16;
		for (int i = 0; i < ROUND; i++)
			for (int j = 0; j < UP; j++) {
				float a0 = (float) (Math.PI * i / ROUND), a1 = (float) (Math.PI * (i + 1) / ROUND), v0 = j / (float) UP, v1 = (j + 1) / (float) UP;
				float[] xs = {x + w / 2 - (float) Math.cos(a0) * w / 2 * rad(v0), x + w / 2 - (float) Math.cos(a1) * w / 2 * rad(v0), x + w / 2 - (float) Math.cos(a1) * w / 2 * rad(v1), x + w / 2 - (float) Math.cos(a0) * w / 2 * rad(v1)};
				float f0 = (float) Math.sin(a0), f1 = (float) Math.sin(a1), u0 = a0 / (float) Math.PI, u1 = a1 / (float) Math.PI;
				float e0 = fade(v0), e1 = fade(v1);
				vert(xs[0], y + h * v0, c, f0 * e0, u0, v0 * 6, 17, param);
				vert(xs[1], y + h * v0, c, f1 * e0, u1, v0 * 6, 17, param);
				vert(xs[2], y + h * v1, c, f1 * e1, u1, v1 * 6, 17, param);
				vert(xs[0], y + h * v0, c, f0 * e0, u0, v0 * 6, 17, param);
				vert(xs[2], y + h * v1, c, f1 * e1, u1, v1 * 6, 17, param);
				vert(xs[3], y + h * v1, c, f0 * e1, u0, v1 * 6, 17, param);
			}
	}

	static float rad(float v) {
		return 0.75f + 0.25f * (float) Math.sin(v * Math.PI);
	}

	static float fade(float v) {
		return Math.min(1, v * 8) * Math.min(1, (1 - v) * 3);
	}

	static int param(float k, int seed) {
		return Math.round(k * 255) + seed * 256;
	}

	public static void main(String[] a) throws Exception {
		Path fsh = Path.of(a[0]), vsh = Path.of(a[1]);
		String out = a[2];
		GLFW.glfwInit();
		GLFW.glfwWindowHint(GLFW.GLFW_VISIBLE, GLFW.GLFW_FALSE);
		GLFW.glfwWindowHint(GLFW.GLFW_CONTEXT_VERSION_MAJOR, 3);
		GLFW.glfwWindowHint(GLFW.GLFW_CONTEXT_VERSION_MINOR, 2);
		GLFW.glfwWindowHint(GLFW.GLFW_OPENGL_PROFILE, GLFW.GLFW_OPENGL_CORE_PROFILE);
		GLFW.glfwWindowHint(GLFW.GLFW_OPENGL_FORWARD_COMPAT, GLFW.GLFW_TRUE);
		long win = GLFW.glfwCreateWindow(64, 64, "fx", 0, 0);
		GLFW.glfwMakeContextCurrent(win);
		GL.createCapabilities();

		int vs = compile(GL_VERTEX_SHADER, Files.readString(vsh)), fs = compile(GL_FRAGMENT_SHADER, Files.readString(fsh));
		int prog = glCreateProgram();
		glAttachShader(prog, vs);
		glAttachShader(prog, fs);
		glBindAttribLocation(prog, 0, "Position");
		glBindAttribLocation(prog, 1, "Color");
		glBindAttribLocation(prog, 2, "UV0");
		glBindAttribLocation(prog, 3, "UV2");
		glLinkProgram(prog);
		if (glGetProgrami(prog, GL_LINK_STATUS) == 0) throw new RuntimeException(glGetProgramInfoLog(prog));
		System.out.println("shader compiled and linked");

		// each row a mode, each column a moment; left half dark ground, right half bright
		String[] names = {"ink", "star", "crescent", "sheet", "slash", "flow", "ring", "crack", "flare", "swirl", "arc", "rune", "tube", "heal beam"};
		int rows = names.length, w = CELL * LIFE.length * 2, h = CELL * rows;
		for (int side = 0; side < 2; side++) {
			float ox = side * CELL * LIFE.length;
			for (int col = 0; col < LIFE.length; col++) {
				float k = LIFE[col], x = ox + col * CELL, pad = 12, s = CELL - pad * 2;
				for (int row = 0; row < rows; row++) {
					float y = row * CELL + pad, cx = x + CELL / 2f, cy = row * CELL + CELL / 2f;
					float[] c = TINT[row % TINT.length];
					int seed = 3 + row * 7 + col;
					switch (names[row]) {
						case "ink" -> atlas(x + pad, y, s, s, TINT[5], 1 + (int) (k * 16) % 16 * 0, (int) (k * 16), 18, param(k, seed));
						case "star" -> {
							quad(x + pad, y, s, s, new float[3], 1, 19, param(k, seed));
							quad(x + pad + 20, y + 20, s - 40, s - 40, c, 1, 19, param(k, seed));
						}
						case "crescent" -> {
							quad(x + pad, y, s, s, new float[3], 1, 20, param(k, seed));
							quad(x + pad + 8, y + 8, s - 16, s - 16, TINT[5], 1, 20, param(k, seed));
						}
						case "sheet" -> {
							float[] t = TINT[1];
							vert(x + pad, y, t, 1, -1, 0, 21, param(k, seed));
							vert(x + pad + s, y, t, 1, 1, 0, 21, param(k, seed));
							vert(x + pad + s, y + s, t, 1, 1, 1, 21, param(k, seed));
							vert(x + pad, y, t, 1, -1, 0, 21, param(k, seed));
							vert(x + pad + s, y + s, t, 1, 1, 1, 21, param(k, seed));
							vert(x + pad, y + s, t, 1, -1, 1, 21, param(k, seed));
						}
						case "slash" -> {
							slash(cx - 30, cy + 10, 90, 34, 2.6f, -0.3f, k, TINT[0], param(k, seed));
							slash(cx - 26, cy + 8, 84, 8, 2.6f, -0.3f, k * 1.2f, new float[] {1, 1, 1}, param(Math.min(1, k * 1.2f), seed + 1));
						}
						case "flow" -> strip(x + pad, cy, s, 42, c, 1, 10, param(k, seed), 10);
						case "ring" -> quad(x + pad, y, s, s, c, 1, 11, param(k, seed));
						case "crack" -> quad(x + pad, y, s, s, c, 1, 12, param(k, seed));
						case "flare" -> quad(x + pad, y, s, s, c, 1, 13, param(k, seed));
						case "swirl" -> quad(x + pad, y, s, s, TINT[3], 1, 14, param(0.45f, seed));
						case "arc" -> strip(x + pad, cy, s, 36, c, 1, 15, param(k, seed), 6);
						case "rune" -> quad(x + pad, y, s, s, c, 1, 16, param(k, 2 + col));
						case "tube" -> tube(cx - 38, y, 76, s, c, k, param(k, seed));
						default -> {
							strip(x + pad, cy, s, 34, TINT[1], 0.4f, 10, param(k, seed), 8);
							strip(x + pad, cy, s, 11, TINT[1], 1, 10, param(k, seed + 1), 8);
							quad(cx - 40 + s / 2f - 40, cy - 60, 120, 120, TINT[1], 0.8f, 13, param(k, seed));
						}
					}
				}
			}
		}

		FloatBuffer fb = BufferUtils.createFloatBuffer(VERTS.size() * 9);
		ByteBuffer modes = BufferUtils.createByteBuffer(VERTS.size() * 4);
		for (float[] v : VERTS) {
			fb.put(v, 0, 9);
			modes.putShort((short) v[9]).putShort((short) v[10]);
		}
		fb.flip();
		modes.flip();
		modes.order(java.nio.ByteOrder.nativeOrder());
		ByteBuffer modes2 = BufferUtils.createByteBuffer(VERTS.size() * 4);
		for (float[] v : VERTS) modes2.putShort((short) v[9]).putShort((short) v[10]);
		modes2.flip();
		int vao = glGenVertexArrays();
		glBindVertexArray(vao);
		int vbo = glGenBuffers();
		glBindBuffer(GL_ARRAY_BUFFER, vbo);
		glBufferData(GL_ARRAY_BUFFER, fb, GL_STATIC_DRAW);
		glVertexAttribPointer(0, 3, GL_FLOAT, false, 36, 0);
		glVertexAttribPointer(1, 4, GL_FLOAT, false, 36, 12);
		glVertexAttribPointer(2, 2, GL_FLOAT, false, 36, 28);
		glEnableVertexAttribArray(0);
		glEnableVertexAttribArray(1);
		glEnableVertexAttribArray(2);
		int vbo2 = glGenBuffers();
		glBindBuffer(GL_ARRAY_BUFFER, vbo2);
		glBufferData(GL_ARRAY_BUFFER, modes2, GL_STATIC_DRAW);
		glVertexAttribIPointer(3, 2, GL_SHORT, 4, 0);
		glEnableVertexAttribArray(3);

		int tex = glGenTextures();
		glBindTexture(GL_TEXTURE_2D, tex);
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, (ByteBuffer) null);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
		int fbo = glGenFramebuffers();
		glBindFramebuffer(GL_FRAMEBUFFER, fbo);
		glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0);
		glViewport(0, 0, w, h);
		glEnable(GL_SCISSOR_TEST);
		glScissor(0, 0, w / 2, h);
		glClearColor(0.09f, 0.1f, 0.12f, 1);
		glClear(GL_COLOR_BUFFER_BIT);
		glScissor(w / 2, 0, w / 2, h);
		glClearColor(0.5f, 0.66f, 0.84f, 1);
		glClear(GL_COLOR_BUFFER_BIT);
		glDisable(GL_SCISSOR_TEST);
		glEnable(GL_BLEND);
		glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA);

		BufferedImage sheet = ImageIO.read(new File("src/main/resources/assets/ashbound/textures/vfx/spell.png"));
		ByteBuffer pixels = BufferUtils.createByteBuffer(sheet.getWidth() * sheet.getHeight() * 4);
		for (int y = 0; y < sheet.getHeight(); y++)
			for (int x = 0; x < sheet.getWidth(); x++) {
				int c = sheet.getRGB(x, y);
				pixels.put((byte) (c >> 16)).put((byte) (c >> 8)).put((byte) c).put((byte) (c >> 24));
			}
		pixels.flip();
		int atlas = glGenTextures();
		glBindTexture(GL_TEXTURE_2D, atlas);
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, sheet.getWidth(), sheet.getHeight(), 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

		glUseProgram(prog);
		float[] mv = {1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1};
		float[] pr = {2f / w, 0, 0, 0, 0, 2f / h, 0, 0, 0, 0, 1, 0, -1, -1, 0, 1};
		glUniformMatrix4fv(glGetUniformLocation(prog, "ModelViewMat"), false, mv);
		glUniformMatrix4fv(glGetUniformLocation(prog, "ProjMat"), false, pr);
		glUniform4f(glGetUniformLocation(prog, "ColorModulator"), 1, 1, 1, 1);
		glUniform1f(glGetUniformLocation(prog, "GameTime"), 0.0312f);
		glDrawArrays(GL_TRIANGLES, 0, VERTS.size());
		if (glGetError() != 0) System.out.println("gl error");

		ByteBuffer px = BufferUtils.createByteBuffer(w * h * 4);
		glReadPixels(0, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE, px);
		BufferedImage img = new BufferedImage(w, h, BufferedImage.TYPE_INT_RGB);
		for (int y = 0; y < h; y++)
			for (int x = 0; x < w; x++) {
				int i = (x + y * w) * 4;
				img.setRGB(x, y, (px.get(i) & 255) << 16 | (px.get(i + 1) & 255) << 8 | px.get(i + 2) & 255);
			}
		ImageIO.write(img, "png", new File(out));
		System.out.println("wrote " + out);
		bloom(w, h, out.replace(".png", "_bloom.png"));
		GLFW.glfwTerminate();
	}

	static int target(int w, int h) {
		int t = glGenTextures();
		glBindTexture(GL_TEXTURE_2D, t);
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, (ByteBuffer) null);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
		return t;
	}

	static int POST, QUAD;

	static void pass(int from, int fbo, int to, int w, int h, float dx, float dy, float gain) {
		glBindFramebuffer(GL_FRAMEBUFFER, fbo);
		if (to != 0) glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, to, 0);
		glViewport(0, 0, w, h);
		glBindTexture(GL_TEXTURE_2D, from);
		glUniform2f(glGetUniformLocation(POST, "Step"), dx, dy);
		glUniform1f(glGetUniformLocation(POST, "Gain"), gain);
		glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
	}

	/** The real blur (spell_post) over the sheet, as client/Bloom does it: half, quarter, eighth, added back on. */
	static void bloom(int w, int h, String out) throws Exception {
		String dir = "src/main/resources/assets/ashbound/shaders/core/";
		POST = glCreateProgram();
		glAttachShader(POST, compile(GL_VERTEX_SHADER, Files.readString(Path.of(dir + "spell_post.vsh"))));
		glAttachShader(POST, compile(GL_FRAGMENT_SHADER, Files.readString(Path.of(dir + "spell_post.fsh"))));
		glBindAttribLocation(POST, 0, "Position");
		glBindAttribLocation(POST, 1, "UV0");
		glLinkProgram(POST);
		if (glGetProgrami(POST, GL_LINK_STATUS) == 0) throw new RuntimeException(glGetProgramInfoLog(POST));
		System.out.println("post shader compiled and linked");
		int frame = target(w, h);
		glBindTexture(GL_TEXTURE_2D, frame);
		glCopyTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, 0, 0, w, h, 0);
		QUAD = glGenVertexArrays();
		glBindVertexArray(QUAD);
		int vb = glGenBuffers();
		glBindBuffer(GL_ARRAY_BUFFER, vb);
		glBufferData(GL_ARRAY_BUFFER, new float[] {-1, -1, 0, 0, 0, 1, -1, 0, 1, 0, -1, 1, 0, 0, 1, 1, 1, 0, 1, 1}, GL_STATIC_DRAW);
		glVertexAttribPointer(0, 3, GL_FLOAT, false, 20, 0);
		glVertexAttribPointer(1, 2, GL_FLOAT, false, 20, 12);
		glEnableVertexAttribArray(0);
		glEnableVertexAttribArray(1);
		glUseProgram(POST);
		glDisable(GL_BLEND);
		glDisable(GL_DEPTH_TEST);
		int fbo = glGenFramebuffers(), a = target(w / 4, h / 4), b = target(w / 4, h / 4), c = target(w / 8, h / 8), d = target(w / 8, h / 8), end = target(w, h);
		pass(frame, fbo, a, w / 4, h / 4, 1f / w, 0, 1);
		pass(a, fbo, b, w / 4, h / 4, 0, 4f / h, 1);
		pass(b, fbo, c, w / 8, h / 8, 4f / w, 0, 1);
		pass(c, fbo, d, w / 8, h / 8, 0, 8f / h, 1);
		pass(frame, fbo, end, w, h, 0, 0, 1);
		glEnable(GL_BLEND);
		glBlendFunc(GL_ONE, GL_ONE);
		pass(frame, fbo, 0, w, h, 0, 0, 0.4f);
		pass(b, fbo, 0, w, h, 0, 0, 0.55f);
		pass(d, fbo, 0, w, h, 0, 0, 0.6f);
		ByteBuffer px = BufferUtils.createByteBuffer(w * h * 4);
		glReadPixels(0, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE, px);
		BufferedImage img = new BufferedImage(w, h, BufferedImage.TYPE_INT_RGB);
		for (int y = 0; y < h; y++)
			for (int x = 0; x < w; x++) {
				int i = (x + y * w) * 4;
				img.setRGB(x, y, (px.get(i) & 255) << 16 | (px.get(i + 1) & 255) << 8 | px.get(i + 2) & 255);
			}
		ImageIO.write(img, "png", new File(out));
		System.out.println("wrote " + out + (glGetError() != 0 ? " (gl error)" : ""));
	}

	/** A ribbon across the cell: x across it, y along in blocks. */
	static void strip(float x, float cy, float len, float wide, float[] c, float a, int mode, int param, float blocks) {
		vert(x, cy - wide / 2, c, a, -1, 0, mode, param);
		vert(x + len, cy - wide / 2, c, a, -1, blocks, mode, param);
		vert(x + len, cy + wide / 2, c, a, 1, blocks, mode, param);
		vert(x, cy - wide / 2, c, a, -1, 0, mode, param);
		vert(x + len, cy + wide / 2, c, a, 1, blocks, mode, param);
		vert(x, cy + wide / 2, c, a, 1, 0, mode, param);
	}

	static int compile(int type, String src) {
		int s = glCreateShader(type);
		glShaderSource(s, src);
		glCompileShader(s);
		if (glGetShaderi(s, GL_COMPILE_STATUS) == 0) throw new RuntimeException(glGetShaderInfoLog(s));
		return s;
	}
}
