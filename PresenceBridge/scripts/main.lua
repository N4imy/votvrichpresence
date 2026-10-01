print("[PresenceBridge] Mod loaded!")

local STATE_FILE =
    "C:/Program Files (x86)/VotV/WindowsNoEditor/Presence/presence_state.txt"

local gameplayStatics = StaticFindObject(
    "/Script/Engine.Default__GameplayStatics"
)

local lastState = ""


local function writeState(text)

    if text == lastState then
        return
    end

    local file = io.open(STATE_FILE, "w")

    if not file then
        print("[PresenceBridge] ERROR: Could not open state file")
        return
    end

    file:write(text)
    file:close()

    lastState = text

    print("[PresenceBridge] State: " .. text)
end


LoopAsync(2000, function()

    local cycle = FindFirstOf("daynightCycle_C")


    --------------------------------------------------
    -- MAIN MENU / NO WORLD
    --------------------------------------------------

    if not cycle or not cycle:IsValid() then
        writeState("menu")
        return
    end


    --------------------------------------------------
    -- WORLD NOT ACTIVE
    --------------------------------------------------

    if cycle.IsActive == false then
        writeState("menu")
        return
    end


    --------------------------------------------------
    -- TIME DATA
    --------------------------------------------------

    local maxTime = cycle.MaxTime
    local totalTime = cycle.totalTime

    if not maxTime or maxTime <= 0 then
        writeState("menu")
        return
    end

    if not totalTime or totalTime < 0 then
        writeState("menu")
        return
    end


    --------------------------------------------------
    -- DAY
    --------------------------------------------------

    local gameDay =
        math.floor(totalTime / maxTime) + 1


    --------------------------------------------------
    -- TIME
    --------------------------------------------------

    local timeInDay =
        totalTime % maxTime

    local hoursFloat =
        (timeInDay / maxTime) * 24

    local hour =
        math.floor(hoursFloat)

    local minute =
        math.floor(
            (hoursFloat - hour) * 60
        )

    local gameTime =
        string.format("%02d:%02d", hour, minute)


    --------------------------------------------------
    -- PAUSE
    --------------------------------------------------

    local paused = false

    if gameplayStatics
        and gameplayStatics:IsValid()
    then

        paused =
            gameplayStatics:IsGamePaused(cycle)
    end


    --------------------------------------------------
    -- STATE
    --------------------------------------------------

    if paused then

        writeState(
            "paused|"
            .. tostring(gameDay)
            .. "|"
            .. gameTime
        )

    else

        writeState(
            "playing|"
            .. tostring(gameDay)
            .. "|"
            .. gameTime
        )

    end

end)