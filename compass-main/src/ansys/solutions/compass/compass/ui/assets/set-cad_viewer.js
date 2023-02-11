
function set3DView(fileUrl, div_id) {
    if (fileUrl != '' && div_id != '') {

		contextPath = "/assets/";
		//debugger;

        try {
            var options = {
                allowEdit: false,
                active : true,
                showLogo : false,
                showFileOpen : true,
                showHighlight : true,
                showAbout : false,
                showMarkup : false,
                showOptions : false,
                showViewport : false,
                showExplode : false
            };
            VIEWER_UNIQUE = new GLTFViewer(div_id, fileUrl, "SCDOC", contextPath, options);
            // GLTFViewer(containerID,url,urlType,contextPath,options,viewportNumber,controllingViewer)
            // where viewportNumber and controllingViewer are optional
            // and viewportNumber is 0 by default
        } catch (error) {
            console.log("failed loading 3D view");
            console.log(error);
        }
    }
}