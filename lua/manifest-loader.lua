-- manifest-loader.lua - YAML manifest loader for Fiddlie documents
local M = {}

local data = nil

-- Simple YAML parser (fallback if lyaml not available)
local function simple_yaml_parse(content)
  local result = {}
  local stack = {{obj = result, indent = -1, is_list_item = false}}

  for line in content:gmatch("[^\r\n]+") do
    -- Skip comments and empty lines
    if not line:match("^%s*#") and not line:match("^%s*$") then
      local indent = #(line:match("^(%s*)") or "")
      local trimmed = line:match("^%s*(.-)%s*$")

      -- Pop stack to find parent, but be careful with list item continuations
      while #stack > 1 do
        local top = stack[#stack]
        -- Pop if we're at same or lower indent, unless this is a continuation of a list item
        if top.indent >= indent and not (top.is_list_item and indent > stack[#stack - 1].indent) then
          table.remove(stack)
        else
          break
        end
      end

      local parent = stack[#stack].obj

      -- Check for list item
      local list_match = trimmed:match("^%-%s*(.*)$")
      if list_match then
        if type(parent) ~= "table" then
          parent = {}
          stack[#stack].obj = parent
        end

        -- Check if list item has key: value on same line
        local key, value = list_match:match("^([%w_]+):%s*(.*)$")
        if key then
          local item = {}
          -- Remove quotes from value
          value = value:gsub('^"(.*)"$', '%1'):gsub("^'(.*)'$", '%1')
          item[key] = value
          table.insert(parent, item)
          -- Push item onto stack with special indent for continuation lines
          table.insert(stack, {obj = item, indent = indent, is_list_item = true})
        else
          -- Simple list item (just a value)
          list_match = list_match:gsub('^"(.*)"$', '%1'):gsub("^'(.*)'$", '%1')
          if list_match ~= "" then
            table.insert(parent, list_match)
          else
            -- Empty list item starts a new object
            local item = {}
            table.insert(parent, item)
            table.insert(stack, {obj = item, indent = indent, is_list_item = true})
          end
        end
      else
        -- Key: value pair
        local key, value = trimmed:match("^([%w_]+):%s*(.*)$")
        if key then
          if value == "" then
            -- Nested object
            parent[key] = {}
            table.insert(stack, {obj = parent[key], indent = indent, is_list_item = false})
          else
            -- Remove quotes from value
            value = value:gsub('^"(.*)"$', '%1'):gsub("^'(.*)'$", '%1')
            parent[key] = value
          end
        end
      end
    end
  end

  return result
end

-- Try to load lyaml, fall back to simple parser
local function parse_yaml(content)
  local ok, lyaml = pcall(require, "lyaml")
  if ok then
    return lyaml.load(content)
  else
    return simple_yaml_parse(content)
  end
end

-- Load a manifest file
function M.load(filepath)
  local file = io.open(filepath, "r")
  if not file then
    io.stderr:write("manifest-loader: Could not open file: " .. filepath .. "\n")
    return false
  end

  local content = file:read("*all")
  file:close()

  local ok, result = pcall(parse_yaml, content)
  if not ok then
    io.stderr:write("manifest-loader: Failed to parse YAML: " .. tostring(result) .. "\n")
    return false
  end

  data = result
  return true
end

-- Check if manifest is loaded
function M.is_loaded()
  return data ~= nil
end

-- Get a value using dot notation (e.g., "document.title" or "history.1.date")
function M.get(path, default)
  if not data then
    return default or ""
  end

  local current = data
  for part in path:gmatch("[^.]+") do
    if type(current) ~= "table" then
      return default or ""
    end

    -- Check if part is a number (array index)
    local index = tonumber(part)
    if index then
      current = current[index]
    else
      current = current[part]
    end

    if current == nil then
      return default or ""
    end
  end

  if type(current) == "boolean" then
    return current and "true" or "false"
  end

  return tostring(current)
end

-- Count items in an array
function M.count(path)
  if not data then
    return 0
  end

  local current = data
  for part in path:gmatch("[^.]+") do
    if type(current) ~= "table" then
      return 0
    end
    local index = tonumber(part)
    if index then
      current = current[index]
    else
      current = current[part]
    end
    if current == nil then
      return 0
    end
  end

  if type(current) == "table" then
    return #current
  end

  return 0
end

-- Iterate over array items
function M.foreach(path, callback)
  local count = M.count(path)
  for i = 1, count do
    callback(i, path .. "." .. i)
  end
end

return M
