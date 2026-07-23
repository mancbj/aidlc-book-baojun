-- PDF-only compatibility: use the supplied cover as page one, render the
-- protected script E safely, and allow long hashes to wrap.

local protected_e = "𝓔"

local function has_class(element, wanted)
  for _, class_name in ipairs(element.classes) do
    if class_name == wanted then return true end
  end
  return false
end

function Meta(meta)
  if not FORMAT:match("latex") then return nil end
  -- Keep searchable PDF metadata without asking the Pandoc template to emit
  -- its own title page before the authored cover.
  meta["title-meta"] = meta.title
  meta["author-meta"] = meta.author
  meta.title = nil
  meta.subtitle = nil
  meta.author = nil
  return meta
end

local function resolve_resource(path)
  if pandoc.path.is_absolute(path) then return path end
  for _, directory in ipairs(PANDOC_STATE.resource_path) do
    local candidate = pandoc.path.join({directory, path})
    local handle = io.open(candidate, "rb")
    if handle then
      handle:close()
      return candidate
    end
  end
  return path
end

function Figure(element)
  if not FORMAT:match("latex") then return nil end
  local block = element.content[1]
  local image = block and block.content and block.content[1]
  if not image or image.t ~= "Image" or not has_class(image.attr, "book-cover") then
    return nil
  end
  local cover = resolve_resource(image.src)
  return pandoc.RawBlock("latex", table.concat({
    "\\thispagestyle{empty}",
    "\\newgeometry{margin=0pt}",
    "\\noindent\\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{\\detokenize{" .. cover .. "}}",
    "\\restoregeometry",
    "\\clearpage",
  }, "\n"))
end

function Str(element)
  if not FORMAT:match("latex") or not element.text:find(protected_e, 1, true) then
    return nil
  end

  local result = {}
  local cursor = 1
  while true do
    local first, last = element.text:find(protected_e, cursor, true)
    if not first then
      local tail = element.text:sub(cursor)
      if tail ~= "" then table.insert(result, pandoc.Str(tail)) end
      break
    end
    local prefix = element.text:sub(cursor, first - 1)
    if prefix ~= "" then table.insert(result, pandoc.Str(prefix)) end
    table.insert(result, pandoc.Math("InlineMath", "\\mathcal{E}"))
    cursor = last + 1
  end
  return result
end

function Code(element)
  if not FORMAT:match("latex") then return nil end
  if element.text:find(protected_e, 1, true) then
    local result = {}
    local cursor = 1
    while true do
      local first, last = element.text:find(protected_e, cursor, true)
      if not first then
        local tail = element.text:sub(cursor)
        if tail ~= "" then table.insert(result, pandoc.Code(tail, element.attr)) end
        break
      end
      local prefix = element.text:sub(cursor, first - 1)
      if prefix ~= "" then table.insert(result, pandoc.Code(prefix, element.attr)) end
      table.insert(result, pandoc.Math("InlineMath", "\\mathcal{E}"))
      cursor = last + 1
    end
    return result
  end
  if #element.text < 40 or not element.text:match("^[0-9a-fA-F]+$") then
    return nil
  end
  local chunks = {}
  for index = 1, #element.text, 16 do
    table.insert(chunks, element.text:sub(index, index + 15))
  end
  return pandoc.RawInline("latex", "\\texttt{" .. table.concat(chunks, "\\allowbreak{}") .. "}")
end

function CodeBlock(element)
  if not FORMAT:match("latex") or not element.text:find(protected_e, 1, true) then
    return nil
  end
  -- Verbatim environments cannot contain math nodes. The immediately
  -- following formula retains the script glyph; the Mermaid source uses E.
  element.text = element.text:gsub(protected_e, "E")
  return element
end
