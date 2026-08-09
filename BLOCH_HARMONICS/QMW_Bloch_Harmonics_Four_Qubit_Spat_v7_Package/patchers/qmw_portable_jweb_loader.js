autowatch = 1;
inlets = 1;
outlets = 1;

function bang() {
    var patchPath = this.patcher.filepath;
    var slash = Math.max(patchPath.lastIndexOf("/"), patchPath.lastIndexOf("\\"));
    if (!patchPath || slash < 0) {
        post("QMW v7: save the main patch before loading the bundled jweb viewer.\n");
        return;
    }

    var viewerPath = patchPath.substring(0, slash + 1) + "bloch-harmonics-four-qubit-max.html";
    var viewer = new File(viewerPath, "read");
    if (!viewer.isopen) {
        post("QMW v7: bundled jweb viewer not found at " + viewerPath + "\n");
        return;
    }
    viewer.close();
    outlet(0, "readfile", viewerPath);
}
