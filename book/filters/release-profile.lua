-- Release profile: strip authoring / production meta from published HTML/PDF.
-- Source markdown keeps these sections for the writing pipeline; only the
-- release build applies this filter.

local function header_text(header)
  return pandoc.utils.stringify(header.content):gsub("%s+", " "):gsub("^%s+", ""):gsub("%s+$", "")
end

local function should_drop_header(header)
  local text = header_text(header)

  -- Chapter writing scaffold
  if text == "Metadata" then
    return true
  end
  -- Exact Gate checklist only; keep content like "2.3 Gates：阶段门禁..."
  if text == "Gate" then
    return true
  end
  if text:find("Review Notes", 1, true) then
    return true
  end
  -- e.g. "06 · Review：可读稿自检与后续审校入口"
  if text:find("Review：", 1, true) or text:find("Review:", 1, true) then
    return true
  end

  -- Manifesto / TOC production checklists and process audits
  if text:match("^D%d%d%-T%d%d") then
    return true
  end
  if text == "来源记录" then
    return true
  end
  if text == "核心问题去重审计" then
    return true
  end
  if text == "v0.1 边界" then
    return true
  end

  -- Chapter-end internal path bibliographies read as production notes, not
  -- published references. Keep in-source; omit from release HTML/PDF.
  if text == "References" or text == "参考文献" then
    return true
  end

  return false
end

function Pandoc(doc)
  local kept = {}
  local skip_until_level = nil

  for _, block in ipairs(doc.blocks) do
    if block.t == "Header" then
      if skip_until_level and block.level <= skip_until_level then
        skip_until_level = nil
      end

      if not skip_until_level and should_drop_header(block) then
        skip_until_level = block.level
      elseif not skip_until_level then
        table.insert(kept, block)
      end
    elseif not skip_until_level then
      table.insert(kept, block)
    end
  end

  doc.blocks = kept
  return doc
end
