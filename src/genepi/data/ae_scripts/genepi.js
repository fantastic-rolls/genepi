// JSON LIBRARY
if (typeof JSON !== "object") { JSON = {} } (function () { "use strict"; var rx_one = /^[\],:{}\s]*$/; var rx_two = /\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g; var rx_three = /"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g; var rx_four = /(?:^|:|,)(?:\s*\[)+/g; var rx_escapable = /[\\"\u0000-\u001f\u007f-\u009f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g; var rx_dangerous = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g; function f(n) { return (n < 10) ? "0" + n : n } function this_value() { return this.valueOf() } if (typeof Date.prototype.toJSON !== "function") { Date.prototype.toJSON = function () { return isFinite(this.valueOf()) ? (this.getUTCFullYear() + "-" + f(this.getUTCMonth() + 1) + "-" + f(this.getUTCDate()) + "T" + f(this.getUTCHours()) + ":" + f(this.getUTCMinutes()) + ":" + f(this.getUTCSeconds()) + "Z") : null }; Boolean.prototype.toJSON = this_value; Number.prototype.toJSON = this_value; String.prototype.toJSON = this_value } var gap; var indent; var meta; var rep; function quote(string) { rx_escapable.lastIndex = 0; return rx_escapable.test(string) ? "\"" + string.replace(rx_escapable, function (a) { var c = meta[a]; return typeof c === "string" ? c : "\\u" + ("0000" + a.charCodeAt(0).toString(16)).slice(-4) }) + "\"" : "\"" + string + "\"" } function str(key, holder) { var i; var k; var v; var length; var mind = gap; var partial; var value = holder[key]; if (value && typeof value === "object" && typeof value.toJSON === "function") { value = value.toJSON(key) } if (typeof rep === "function") { value = rep.call(holder, key, value) } switch (typeof value) { case "string": return quote(value); case "number": return (isFinite(value)) ? String(value) : "null"; case "boolean": case "null": return String(value); case "object": if (!value) { return "null" } gap += indent; partial = []; if (Object.prototype.toString.apply(value) === "[object Array]") { length = value.length; for (i = 0; i < length; i += 1) { partial[i] = str(i, value) || "null" } v = partial.length === 0 ? "[]" : gap ? ("[\n" + gap + partial.join(",\n" + gap) + "\n" + mind + "]") : "[" + partial.join(",") + "]"; gap = mind; return v } if (rep && typeof rep === "object") { length = rep.length; for (i = 0; i < length; i += 1) { if (typeof rep[i] === "string") { k = rep[i]; v = str(k, value); if (v) { partial.push(quote(k) + ((gap) ? ": " : ":") + v) } } } } else { for (k in value) { if (Object.prototype.hasOwnProperty.call(value, k)) { v = str(k, value); if (v) { partial.push(quote(k) + ((gap) ? ": " : ":") + v) } } } } v = partial.length === 0 ? "{}" : gap ? "{\n" + gap + partial.join(",\n" + gap) + "\n" + mind + "}" : "{" + partial.join(",") + "}"; gap = mind; return v } } if (typeof JSON.stringify !== "function") { meta = { "\b": "\\b", "\t": "\\t", "\n": "\\n", "\f": "\\f", "\r": "\\r", "\"": "\\\"", "\\": "\\\\" }; JSON.stringify = function (value, replacer, space) { var i; gap = ""; indent = ""; if (typeof space === "number") { for (i = 0; i < space; i += 1) { indent += " " } } else if (typeof space === "string") { indent = space } rep = replacer; if (replacer && typeof replacer !== "function" && (typeof replacer !== "object" || typeof replacer.length !== "number")) { throw new Error("JSON.stringify") } return str("", { "": value }) } } if (typeof JSON.parse !== "function") { JSON.parse = function (text, reviver) { var j; function walk(holder, key) { var k; var v; var value = holder[key]; if (value && typeof value === "object") { for (k in value) { if (Object.prototype.hasOwnProperty.call(value, k)) { v = walk(value, k); if (v !== undefined) { value[k] = v } else { delete value[k] } } } } return reviver.call(holder, key, value) } text = String(text); rx_dangerous.lastIndex = 0; if (rx_dangerous.test(text)) { text = text.replace(rx_dangerous, function (a) { return ("\\u" + ("0000" + a.charCodeAt(0).toString(16)).slice(-4)) }) } if (rx_one.test(text.replace(rx_two, "@").replace(rx_three, "]").replace(rx_four, ""))) { j = eval("(" + text + ")"); return (typeof reviver === "function") ? walk({ "": j }, "") : j } throw new SyntaxError("JSON.parse") } } }());
//


var AUDIO_TO_KEYFRAMES_CMD_ID = 4218

app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);

var cache = {}

var episode = {}

var dataFile = File("___TMPLT_CONFIG_FILE___")
if (dataFile.open("r")) {
    dataFile.encoding = "utf-8"
    var data = dataFile.read()
    episode = JSON.parse(data)
    dataFile.close()
}

function get_resource(path) {
    if (path in cache) {
        return app.project.itemByID(cache[path])
    } else {
        var item = app.project.importFile(new ImportOptions(new File(path)))
        cache[path] = item.id
        return item
    }
}

function createFromTemplate(template, dstFile) {
    project = app.open(new File(template))
    project.save(new File(dstFile))
    return project
}

function generateAudioKeyframes(config, comp) {
    var audios = config.audios || {}
    var mapping = {}
    for (var name in audios) {
        if (name == "master") continue;
        var item = get_resource(audios[name])
        var layer = comp.layers.add(item)
        app.executeCommand(AUDIO_TO_KEYFRAMES_CMD_ID)
        layer.remove()
        // New layer should be created at index 1
        layer = comp.layer(1)
        // Create audio wrapper
        var wrapperComp = getComp("Audio_Wrapper")
        wrapperComp = wrapperComp.duplicate()
        wrapperComp.name = "Audio_Wrapper_" + name
        var wrapperLayer = comp.layers.add(wrapperComp)
        layer.copyToComp(wrapperComp)
        wrapperLayer.name = "audio_" + name
        layer.remove()
        mapping[name.toLowerCase()] = wrapperLayer
    }
    return mapping
}

function generateLobby(config, comp) {
    var payload = config.payload || {}
    // Instanciate lobby precomp
    var start = config.start || 0
    var end = config.end || 1
    var duration = end - start
    var lobbyComp = getComp("Lobby")
    lobbyComp = lobbyComp.duplicate()
    lobbyComp.name = "Lobby_" + config.name.toUpperCase()
    lobbyComp.duration = duration
    var layer = comp.layers.add(lobbyComp)
    layer.startTime = start
    layer.audioEnabled = false
    if (config.name) layer.name = config.name;
    // get audio
    var item = get_resource(payload.audio)
    item = lobbyComp.layers.add(item, duration)
    // item.inPoint = start
    item.startTime = -start
    item.inPoint = 0
    item.outPoint = duration
    var spectrum = lobbyComp.layers.byName("audio_spectrum")
    spectrum.duration = duration * 2
    var effect = spectrum.effect("spectrum").property(1)
    effect.setValue(1)
}

function generateGamePlay(config, title, subtitle, comp, mapping) {
    var payload = config.payload || {}
    var start = config.start || 0
    var end = config.end || 1
    var duration = end - start
    var nbPlayers = payload.players || 3
    var subtype = payload.subtype[0].toUpperCase() + payload.subtype.slice(1)
    var compNameParts = [subtype, "UI", nbPlayers, "Players"]
    var guests = (payload.guests || []).sort()
    if ("title" in payload) {
        title = payload.title
    }
    if ("subtitle" in payload) {
        subtitle = payload.subtitle
    }
    if (payload.guests) {
        compNameParts.push(payload.guests)
    }
    var roleplayComp = getComp(compNameParts.join("_"))
    roleplayComp = roleplayComp.duplicate()
    roleplayComp.duration = duration
    var layer = comp.layers.add(roleplayComp, duration)
    layer.startTime = start
    // set titles
    var properties = layer.property("ADBE Layer Overrides")
    for (var i = 1; i < properties.numProperties; ++i) {
        var prop = properties.property(i)
        if (prop.name === "Title") {
            prop.setValue(title)
        } else if (prop.name === "Subtitle") {
            prop.setValue(subtitle)
        } else if (prop.name.slice(0, 12) === "Audio_Level_") {
            var name = prop.name.slice(12).toLowerCase()
            if (name in mapping) {
                prop.expression = "thisComp.layer(\"" + mapping[name].name + "\").essentialProperty(\"Voice_Activation\")"
            }
        }
    }
}

function getComp(name) {
    for (var i = 1; i <= app.project.numItems; i++) {
        if (app.project.item(i) instanceof CompItem && app.project.item(i).name === name) {
            return app.project.item(i)
        }
    }
    return null
}

dstFileName = episode["prerender_project"]
project = createFromTemplate(episode["template"], dstFileName)

var comp = getComp("Scene")
comp = comp.duplicate()
comp.duration = episode.duration
comp.workAreaStart = 0
comp.workAreaDuration = comp.duration

// close all opened comps
do {
    app.executeCommand(4)
} while (app.project.activeItem != null && app.project.activeItem instanceof CompItem);

comp.openInViewer()

app.executeCommand(app.findMenuCommandId("Montage : Scene"))
var audioMapping = generateAudioKeyframes(episode, comp)
for (var i in episode.sections) {
    var section = episode.sections[i]
    if (section.type === "lobby") {
        generateLobby(section, comp)
    } else if (section.type in ["roleplay", "question", "fight", "talk"]) {
        generateGamePlay(section, episode.title, episode.subtitle, comp, audioMapping)
    }
}
