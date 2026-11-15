-- Course filter for the Quarto build of a course's docs/ folder.
--
-- 1. Collapsed answers. The labs write them as HTML, which GitHub also
--    renders:
--
--        <details>
--        <summary>Answer</summary>
--
--        Markdown text.
--
--        </details>
--
--    In HTML output each one becomes a collapsed Quarto callout. A PDF can't
--    collapse anything, so by default the answers move to an "Answers" section
--    at the end of the page, and a pointer ("Answer A3 is at the end of this
--    page.") stays where the answer was. Set `answers-in-pdf: inline` in the
--    page or project metadata to keep them in place as callouts instead.
--
-- 2. Embedded video. A PDF can't play it, so for non-HTML output the <video>
--    block becomes its poster frame with a link to the clip.

local is_html = quarto.doc.is_format("html")
local answers_inline = false
local answers = {}   -- answers[chapter] = list of answers in that chapter
local chapter = 0    -- book builds merge chapters; each starts at a level-1 header

local function is_raw(b, pat)
  return b.t == "RawBlock" and b.format:match("html") and b.text:match(pat) ~= nil
end

local function make_callout(title, content, collapse)
  return (quarto.Callout({
    type = "tip",
    title = title,
    collapse = collapse,
    content = content,
  }))
end

local section = nil

local function answers_id(k)
  return k == 0 and "answers" or ("answers-" .. k)
end

local function answer_block(title, content)
  if is_html or answers_inline then
    return (make_callout(title, content, is_html))
  end
  answers[chapter] = answers[chapter] or {}
  local list = answers[chapter]
  local label = "A" .. (#list + 1)
  table.insert(list, { label = label, title = title, section = section, content = content })
  return pandoc.Para({
    pandoc.Emph({ pandoc.Str(title .. ":"), pandoc.Space(), pandoc.Str(label .. ","),
      pandoc.Space(), pandoc.Str("in"), pandoc.Space(),
      pandoc.Link("Answers", "#" .. answers_id(chapter)), pandoc.Space(), pandoc.Str("at"),
      pandoc.Space(), pandoc.Str("the"), pandoc.Space(), pandoc.Str("end.") }),
  })
end

-- "A3. Part 4: Subthreshold conduction", plus the summary text when it
-- says more than "Answer".
local function answer_heading(a)
  local text = a.label .. "."
  if a.section then text = text .. " " .. a.section end
  if a.title ~= "Answer" or not a.section then text = text .. " (" .. a.title .. ")" end
  return pandoc.Para({ pandoc.Strong({ pandoc.Str(text) }) })
end

local function exists(path)
  local f = io.open(path, "r")
  if f then f:close() return true end
  return false
end

-- A raw HTML path is relative to the page it was written in. In the book
-- build every chapter is merged into one document at the docs root, so a
-- "../assets/..." path from a guide page no longer resolves; fall back to the
-- path from the docs root.
local function resolve(path)
  local here = pandoc.path.directory(quarto.doc.input_file)
  if exists(pandoc.path.join({ here, path })) then return path end
  local stripped = path:gsub("^%.%./", "")
  while stripped:match("^%.%./") do stripped = stripped:gsub("^%.%./", "") end
  return stripped
end

local function flush(out, n)
  local list = answers[n]
  if not list then return end
  out:insert(pandoc.Header(2, "Answers", pandoc.Attr(answers_id(n), { "unnumbered" })))
  for _, a in ipairs(list) do
    out:insert(answer_heading(a))
    out:extend(a.content)
  end
  answers[n] = nil
end

local function convert(blocks)
  local out = pandoc.Blocks({})
  local i = 1
  while i <= #blocks do
    local b = blocks[i]
    if is_raw(b, "^%s*<details[%s>]") then
      local title = b.text:match("<summary>(.-)</summary>")
      local j = i + 1
      if not title and blocks[j] and is_raw(blocks[j], "^%s*<summary>%s*$") then
        local parts = {}
        j = j + 1
        while blocks[j] and not is_raw(blocks[j], "^%s*</summary>%s*$") do
          table.insert(parts, pandoc.utils.stringify(blocks[j]))
          j = j + 1
        end
        title = table.concat(parts, " ")
        j = j + 1
      elseif not title and blocks[j] and is_raw(blocks[j], "^%s*<summary>.-</summary>%s*$") then
        title = blocks[j].text:match("<summary>(.-)</summary>")
        j = j + 1
      end
      local depth, content = 1, pandoc.Blocks({})
      while blocks[j] do
        local c = blocks[j]
        if is_raw(c, "^%s*<details[%s>]") then
          depth = depth + 1
        elseif is_raw(c, "^%s*</details>%s*$") then
          depth = depth - 1
          if depth == 0 then break end
        end
        content:insert(c)
        j = j + 1
      end
      if depth ~= 0 then
        io.stderr:write("course.lua: unbalanced <details>, left as is\n")
        out:insert(b)
        i = i + 1
      else
        out:insert(answer_block(title or "Answer", convert(content)))
        i = j + 1
      end
    elseif not is_html and is_raw(b, "<video") then
      local poster = b.text:match('poster="([^"]+)"')
      local clip = b.text:match('<source[^>]-src="([^"]+)"')
      local blocks_out = pandoc.Blocks({})
      if poster then
        blocks_out:insert(pandoc.Para({ pandoc.Image({}, resolve(poster)) }))
      end
      if clip then
        blocks_out:insert(pandoc.Para({ pandoc.Emph({
          pandoc.Str("This is a video in the web version of the page:"), pandoc.Space(),
          pandoc.Link(clip:match("[^/]+$"), clip), pandoc.Str(".") }) }))
      end
      out:extend(blocks_out)
      i = i + 1
    else
      if b.t == "Header" and b.level == 1 then
        flush(out, chapter)
        chapter = chapter + 1
        section = nil
      elseif b.t == "Header" and b.level == 2 then
        section = pandoc.utils.stringify(b)
      end
      -- PDFs number chapters only. Lab headers already say "Part 1: ...", and
      -- the book template ignores number-depth.
      if not is_html and b.t == "Header" and b.level >= 2 and not b.classes:includes("unnumbered") then
        b.classes:insert("unnumbered")
      end
      if b.t == "BulletList" or b.t == "OrderedList" then
        for k, item in ipairs(b.content) do b.content[k] = convert(item) end
      elseif b.t == "BlockQuote" or b.t == "Div" then
        b.content = convert(b.content)
      end
      out:insert(b)
      i = i + 1
    end
  end
  return out
end

return {
  {
    -- The pages start with an H1 and have no title in their front matter, so
    -- without this the browser tab shows the file name. Use the H1 instead.
    -- Quarto fills in pagetitle with the file name itself, so a pagetitle
    -- equal to the file name counts as unset.
    Pandoc = function(doc)
      if not is_html or doc.meta.title then
        return nil
      end
      local stem = quarto.doc.input_file:match("([^/\\]+)%.%w+$")
      if doc.meta.pagetitle
          and pandoc.utils.stringify(doc.meta.pagetitle) ~= stem then
        return nil
      end
      for _, b in ipairs(doc.blocks) do
        if b.t == "Header" and b.level == 1 then
          doc.meta.pagetitle = pandoc.utils.stringify(b.content)
          return doc
        end
      end
    end,
  },
  {
    Meta = function(meta)
      local v = meta["answers-in-pdf"]
      answers_inline = v ~= nil and pandoc.utils.stringify(v) == "inline"
    end,
  },
  {
    -- Each page, or each chapter of the book, gets its own Answers section
    -- at its end: convert() flushes one before each chapter heading, and the
    -- last one goes at the end of the document.
    Pandoc = function(doc)
      local blocks = convert(doc.blocks)
      flush(blocks, chapter)
      doc.blocks = blocks
      return doc
    end,
  },
}
