
local items = json.decode(io.open(app.params["spec"]):read("a"))
for _, it in ipairs(items) do
  local spr = Sprite(16, 16, ColorMode.RGB)
  local img = Image(16, 16, ColorMode.RGB)
  for _, p in ipairs(it.px) do
    img:drawPixel(p[1], p[2], app.pixelColor.rgba(p[3], p[4], p[5], 255))
  end
  spr:newCel(spr.layers[1], 1, img, Point(0, 0))
  spr.layers[1].name = "icon"
  spr:saveAs(it.ase)
  spr:saveCopyAs(it.png)
  spr:close()
end
