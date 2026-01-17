-- req-tracker.lua - Requirement ID tracking and duplicate detection
local M = {}

-- Table to store all used requirement IDs (numeric part -> full ID string)
local usedIds = {}

-- Extract numeric part from ID like "CR-001" -> 1
local function extractNumber(id)
  local num = id:match("%-(%d+)$")
  if num then
    return tonumber(num)
  end
  return nil
end

-- Format number as 3-digit zero-padded string
local function formatNumber(n)
  if n < 10 then
    return "00" .. n
  elseif n < 100 then
    return "0" .. n
  else
    return tostring(n)
  end
end

-- Register a requirement ID
-- Returns: ok (boolean), existing_id (string or nil if duplicate)
function M.register(id)
  local num = extractNumber(id)
  if num == nil then
    -- No numeric part found, skip tracking
    return true, nil
  end

  if usedIds[num] then
    -- Duplicate detected
    return false, usedIds[num]
  end

  -- Register this ID
  usedIds[num] = id
  return true, nil
end

-- Get the highest used ID number (0 if none registered)
function M.getMaxId()
  local max = 0
  for num, _ in pairs(usedIds) do
    if num > max then
      max = num
    end
  end
  return max
end

-- Get count of registered requirements
function M.getCount()
  local count = 0
  for _ in pairs(usedIds) do
    count = count + 1
  end
  return count
end

-- Get next available ID (max + 1), formatted as string
function M.getNextId()
  return formatNumber(M.getMaxId() + 1)
end

-- Print summary to log
function M.printSummary()
  local maxId = M.getMaxId()
  local count = M.getCount()
  if maxId > 0 then
    texio.write_nl("term and log", "")
    texio.write_nl("term and log", "========================================")
    texio.write_nl("term and log", "REQUIREMENTS SUMMARY")
    texio.write_nl("term and log", "  Total requirements: " .. count)
    texio.write_nl("term and log", "  Highest used ID:    " .. formatNumber(maxId))
    texio.write_nl("term and log", "  Next available:     " .. formatNumber(maxId + 1))
    texio.write_nl("term and log", "========================================")
    texio.write_nl("term and log", "")
  end
end

-- Reset state (useful for testing)
function M.reset()
  usedIds = {}
end

return M
