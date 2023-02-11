/*
 * Copyright 2018-2022 ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
 *
 * Restricted Rights Legend
 *
 * Use, duplication, or disclosure of this
 * software and its documentation by the
 * Government is subject to restrictions as
 * set forth in subdivision [(b)(3)(ii)] of
 * the Rights in Technical Data and Computer
 * Software clause at 52.227-7013.
 */ 
 
let thisScriptDir = document.currentScript.src;
thisScriptDir = thisScriptDir.substring(0, thisScriptDir.lastIndexOf('/')) + '/';

// Ensure the required modules are loaded: jquery, inflate, unzip, ANSYSViewer
const AnsysNexusViewerDepends = [ ["jQuery", "utils/jquery.min.js"],
                                  ["JSUnzip", "utils/js-unzip.js"], 
                                  ["JSInflate", "utils/js-inflate.js"], 
                                  ["jQueryContextMenuCSS", "novnc/vendor/jQuery-contextMenu/jquery.contextMenu.min.css"],
                                  ["jQueryContextMenu",    "novnc/vendor/jQuery-contextMenu/jquery.contextMenu.min.js"],
                                  ["jQueryContextMenuUI",  "novnc/vendor/jQuery-contextMenu/jquery.ui.position.min.js"],
                                  ["GLTFViewer", "ANSYSViewer-max.js"] ];
for(const depLoad of AnsysNexusViewerDepends) {
  // Only load if not already loaded
  if (!window.hasOwnProperty(depLoad[0])) {
    if (depLoad[1].endsWith(".js")) { 
      let script = document.createElement('script');
      script.type = 'text/javascript';
      script.src = thisScriptDir + depLoad[1];
      script.async = false;  // async=false ensures scripts are loaded in order, because jquery context menus depend on jquery 
      document.getElementsByTagName('head')[0].appendChild(script);
    } else if (depLoad[1].endsWith(".css")) {
      let link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = thisScriptDir + depLoad[1];
      link.async = false;    
      document.getElementsByTagName('head')[0].appendChild(link);
    }
  }
}

// Define HTML template(s)
const AnsysNexusViewerTemplate = document.createElement('template');
AnsysNexusViewerTemplate.innerHTML = `
<style>
.ansys-nexus-viewer {
  position: relative;
  width: 100%;
  height: 100%;
  margin: 0px;
  padding: 0px;
}
.ansys-nexus-proxy {
  margin:auto;
  width:9.375rem;
  height:6.5625rem;
}
.ansys-nexus-play {
  position: absolute;
  width: 2.5rem;
  height: 3.125rem;
  top:50%; left: 50%; transform: translate(-50%, -50%);
  pointer-events:none;
  display: none;
}
.ansys-nexus-proxy:hover + .ansys-nexus-play {
  display: block;
}
</style>
<div class="ansys-nexus-viewer">
<img class="ansys-nexus-proxy" id="proxy-img" src="/ansys/nexus/images/proxy_viewer.png" style="display:none">
<img class="ansys-nexus-play" id="proxy-play" src="/ansys/nexus/images/play.png">
<div class="ansys-nexus-viewer" id="render-div" style="display: none"><h1>Viewer Active</h1></div>
</div>
`;

// Interface to the GLTFViewer renderer
class GLTFViewerGlue {
  constructor(parent) {
    this._parent = parent;
    this._renderer = null;
    this._webgl_support = null;
  }
  internalRenderer() {
    return this._renderer;
  }
  renderImage() {
    if (this._renderer) {
      return this._renderer.GetRenderedImage();
    }
    return null;
  }
  mouseIn(e) {
    // When the mouse enters an active viewer, mark it as more "recent"
    this._parent.refreshInstance();
  }
  divID() {
    return 'avz-viewer-' + this._parent.guid;
  }
  resizeRenderer(width, height) {
    if (this._renderer === null) return;
    this._renderer.UpdateLayout();
  }
  setPerspective(on) {
    if (this._renderer === null) return;
    this._renderer.scene.navigator.persp = on;
  }

  setSrc(url, extension) {
    if (this._renderer === null) return;
    this._renderer.AddFiles(null, url, extension, GLTFViewer.LT_REPLACE);
  }
  setActive(on) {
    let renderDiv = this._parent.querySelector('#render-div');
    if (on) {
      if (this._webgl_support === null) this._webgl_support = webgl_support();
      if (this._webgl_support) {
        // Default options
        let options = {
          showLogo: false, showFileOpen: false, allowEdit: false, showHighlight: false, showAbout: false,
          showMarkup: false, showOptions: false, showViewport: false, showExplode: false
        };
        // override from parent
        if (this._parent.renderer_options !== null) {
          options = this._parent.renderer_options;
          if (typeof(options) === 'string') options = JSON.parse(options);
        }
        // The avz renderer needs to go into a div with a unique global id
        renderDiv.innerHTML = '<div class="ansys-nexus-viewer" id="' + this.divID() + '"></div>';
        let avzDiv = this._parent.querySelector('#' + this.divID());
        avzDiv.addEventListener('mouseenter', this.mouseIn.bind(this));
        this._renderer = new GLTFViewer(this.divID(), this._parent.src, this._parent.src_ext, null, options);
        this.setPerspective(this._parent.perspective);
      } else {
        // Display WebGL error message
        renderDiv.innerHTML = '<div class="ansys-nexus-viewer" id="' + this.divID() + '"></div>';
        let avzDiv = this._parent.querySelector('#' + this.divID());
        avzDiv.innerHTML = '<em>Warning: WebGL is not supported by this browser.<br>3D interactive geometry will not be displayed.</em>';
      }
    } else {
      // Handle deactivation
      if (this._renderer !== null) this._renderer.Clear();
      this._renderer = null;
      renderDiv.innerHTML = '';
    }
  }
}



// Interface to the GLTFViewer renderer
class EnVNCViewerGlue {
  constructor(parent) {
    this._parent = parent;
    this._renderer = null;
    this._token = '';
  }
  internalRenderer() {
    return this._renderer;
  }
  renderImage() {
    if (this._renderer) {
      let rfb = this._renderer.rfb;
      return rfb.renderImage();
    }
    return null;
  }
  mouseIn(e) {
    // When the mouse enters an active viewer, mark it as more "recent"
    this._parent.refreshInstance();
  }
  divID() {
    return 'vnc-viewer-' + this._parent.guid;
  }
  resizeRenderer(width, height) {
    if (this._renderer === null) return;

    this._renderer.sendResizeCommand();
    //this._renderer.UpdateLayout();
  }
  setPerspective(on) {
    if (this._renderer === null) return;
    //this._renderer.scene.navigator.persp = on;
  }

  setSrc(url, extension) {
    if (this._renderer === null) return;
    //this._renderer.AddFiles(null, url, extension, GLTFViewer.LT_REPLACE);
  }

  setActive(on) {
      let renderDiv = this._parent.querySelector('#render-div');
      // Validate options
      let token = null;
      if (!this._parent.renderer_options) {
          this.displayError("Error starting session: Component needs renderer_options, containing a dict with http and ws entries for connecting to the web socket server.");
          return;
      }
      let options_dict = null;
      try {
          options_dict = JSON.parse(this._parent.renderer_options);
          if (!options_dict) {
              this.displayError("Error starting session: Component's renderer_options are empty or unreadable.");
              return;
          }
      } catch (e) {
          this.displayError("Error starting session: Component's renderer_options could not be parsed as a dictionary.");
          return;
      }
      if (options_dict["http"] === undefined || options_dict["ws"] === undefined) {
          this.displayError("Error starting session: Component's renderer_options dict must contain entries named 'http' and 'ws'");
          return;
      }

      if (on) {
          // Create the http request to reserve a session
          let http_url = new URL(options_dict["http"]);
          if (!this._parent.src || this._parent.src.endsWith(".evsn")) {
              http_url.pathname = "/v1/reserve/local_envision"
          } else {
              http_url.pathname = "/v1/reserve/local_ensight"
          }
          let separator = "?";
          if (this._parent.src !== null) {
              http_url.search = http_url.search + separator + "target_pathname="+this._parent.src;
              separator = "&";
          }
          if (options_dict["security_token"] !== undefined) {
              http_url.search = http_url.search + separator + "security_token="+options_dict["security_token"];
              separator = "&";
          }

          // Send the request to reserve the session
          fetch(http_url)
              .then(function (response) {
                  if (!response.ok) {
                      // If the reservation fails, break out of the fetch/then chain by throwing an error
                      throw new Error(response.statusText);
                  } else {
                      // Pass the json response, as a Promise to the next 'then' clause
                      return response.json();
                  }
              })
              .then(function (response_dict) {
                  token = response_dict["token"];
                  if (!token) {
                      throw new Error("Bad response from session reservation");
                  }
                  this._token = token;
                  this.setupActiveDiv();
                  
                  let vncDiv = this._parent.querySelector('#' + this.divID());
                  vncDiv.addEventListener('mouseenter', this.mouseIn.bind(this));

                  let ws_url = new URL(options_dict["ws"]);
                  if (!ws_url.search) {
                      ws_url.search = "?token="+this._token;
                  } else {
                      ws_url.search += "&token="+this._token;
                  }

                  import('/ansys/nexus/novnc/app/ui_envision.js')
                      .then(EnVNCViewer => {
                          this._renderer = new EnVNCViewer.default(vncDiv, ws_url);
                      })
              }.bind(this))
              .catch((error) => {
                  this.displayError("Error activating session: " + error);
              });

    } else {
        // Handle deactivation
        if (this._renderer !== null) {
            this._renderer.disconnect();
            this._renderer = null;
        }

        // This REST call to release can be redundant.  If ensight or envision was started with
        // the 'exit_on_last_disconnect' vnc option, the _renderer.disconnect() call will implicitly
        // cause the app to exit, and websocketserver will release the session.  
        // If we extend this component to connect to persistent apps, this REST call could be necessary.
        if (this._token) {
            // Create the http request to release the session
            let http_url = new URL(options_dict["http"]);
            http_url.pathname = "/v1/release/"+this._token;

            // Send the request to release the session
            fetch(http_url)
                .then((response) => {
                    if (!response.ok) {
                        // This is not a problem.  The websocketserver may have already released the resource.
                    }
                })
                .catch((error) => {
                    this.displayError("Error deactivating session: " + error);
                });
        }
        this._token = '';

        renderDiv.innerHTML = '';
    }
  }

  displayError(err_str) {
    let renderDiv = this._parent.querySelector('#render-div');
    renderDiv.innerHTML = "<h1>"+err_str+"</h1>";
  }

  // Set up the html styles, UI elements, main canvas element, etc. for an active component
  setupActiveDiv() {
    let renderDiv = this._parent.querySelector('#render-div');

    // The vnc renderer needs to go into a div with a unique global id
    renderDiv.innerHTML = 
`<style>

#noVNC_fallback_error {
  z-index: 1000;
  visibility: hidden;
}
#noVNC_fallback_error.noVNC_open {
  visibility: visible;
}

#noVNC_fallback_error > div {
  max-width: 90%;
  padding: 15px;

  transition: 0.5s ease-in-out;

  transform: translateY(-50px);
  opacity: 0;

  text-align: center;
  font-weight: bold;
  color: #fff;

  border-radius: 10px;
  box-shadow: 6px 6px 0px rgba(0, 0, 0, 0.5);
  background: rgba(200,55,55,0.8);
}
#noVNC_fallback_error.noVNC_open > div {
  transform: translateY(0);
  opacity: 1;
}

#noVNC_fallback_errormsg {
  font-weight: normal;
}

#noVNC_fallback_errormsg .noVNC_message {
  display: inline-block;
  text-align: left;
  font-family: monospace;
  white-space: pre-wrap;
}

#noVNC_fallback_error .noVNC_location {
  font-style: italic;
  font-size: 0.8em;
  color: rgba(255, 255, 255, 0.8);
}

#noVNC_fallback_error .noVNC_stack {
  max-height: 50vh;
  padding: 10px;
  margin: 10px;
  font-size: 0.8em;
  text-align: left;
  font-family: monospace;
  white-space: pre;
  border: 1px solid rgba(0, 0, 0, 0.5);
  background: rgba(0, 0, 0, 0.2);
  overflow: auto;
}
#noVNC_transition {
  display: none;

  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;

  color: white;
  background: rgba(0, 0, 0, 0.5);
  z-index: 50;

  /*display: flex;*/
  align-items: center;
  justify-content: center;
  flex-direction: column;
}
:root.noVNC_loading #noVNC_transition,
:root.noVNC_connecting #noVNC_transition,
:root.noVNC_disconnecting #noVNC_transition,
:root.noVNC_reconnecting #noVNC_transition {
  display: flex;
}
:root:not(.noVNC_reconnecting) #noVNC_cancel_reconnect_button {
  display: none;
}
#noVNC_transition_text {
  font-size: 1.5em;
}

.en_partlist {
    display: none;
    position: absolute;
    top: 25px;
    left: 4px;
    height: flex;
    max-height: 50%;
    overflow-y: auto;
    color: black;
    background-color: rgba(255, 255, 255, .9);
    font-weight: bold;
    z-index: 10;
    padding: 3px 5px 4px 5px;
    border: thin solid black;
}

.en_partlist > * {
    pointer-events: auto;
}

.en_ui_toggle {
    position: absolute;
    top: 2px;
    left: 2px;
    width: 20px;
    height: 20px;
    background-color: transparent;
}

.en_ui_toggle > * {
    pointer-events: auto;
}

/*BOTTOM BAR STYLING*/

#video_controls {
    background-color: #F0F0F0;
    bottom: 0;
    left: 0;
    /*hidden by default*/
    display: none;
    position: absolute;
    pointer-events: none;
    flex-direction: row;
    align-items: center;
    padding-top: 2px;
    padding-bottom: 2px;
}

#video_controls > * {
    pointer-events: auto;
    /*flex options are used by the slider and frame label content*/
    display: flex;
    flex-direction: row;
    align-items: center;
}

/*todo: set width dynamically based on number of time steps. initial should be higher.(?)*/
.slider {
    -webkit-appearance: none;
    min-width: 150px;
    max-width: 300px;
    height: 2px;
    background: #d3d3d3;
    outline: none;
    opacity: 0.7;
    -webkit-transition: .2s;
    transition: opacity .2s;
}

.slider:hover {
    opacity: 1;
}

.slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 10px;
    height: 18px;
    background: #007A98;
    cursor: pointer;
}

/*for firefox*/
.slider::-moz-range-thumb {
    width: 10px;
    height: 18px;
    border-radius: 0;
    background: #007A98;
    cursor: pointer;
}

.frame_label {
    min-width: 50px;
    max-width: 200px;
    margin-left: 5px;
    margin-right: 5px;
    color: #000;
}

/*TOGGLES*/

#toggle_controls {
    bottom: 0;
    right: 0;
    /*hidden by default*/
    display: none;
    position: absolute;
    pointer-events: none;
    background-color: #F0F0F0;
    flex-direction: row;
    align-items: center;
    padding-top: 2px;
    padding-bottom: 2px;
}

#toggle_controls > * {
    pointer-events: auto;
    display: flex;
    flex-direction: row;
    align-items: center;
}

.toggle_control_icon {
    margin-left: 5px;
}

#ens_timestep_monitor {
    display: none;
}
         </style>` +
        '<div class="ansys-nexus-viewer noVNC_loading" id="' + this.divID() + '">' +
        `
            <!--
            <div id="noVNC_fallback_error" class="noVNC_vcenter">
                <div>
                    <div>noVNC encountered an error:</div>
                    <br>
                    <div id="noVNC_fallback_errormsg"></div>
                </div>
            </div>
            -->

            <!-- EnSight UI toggle -->
            <div id="ens_ui_toggle" class="en_ui_toggle">
                <img id='ens_ui_toggle_img' src='/ansys/nexus/novnc/app/images/icons/menu_20_gray.png' />
            </div>
            <!-- EnSight part list -->
            <div id="ens_partlist" class="en_partlist">
                <fieldset id="partlist" name="partlist">
                    <legend>Part List</legend>
                </fieldset>
            </div>
            <!-- EnSight var list -->
            <div id="ens_varlist" class="en_partlist">
                <fieldset id="varlist" name="varlist">
                    <legend>Variable List</legend>
                </fieldset>
            </div>

            <!-- EnSight play/pause controls -->
            <div id="video_controls">
                <input type="image" id="play-pause"
                       alt="Play/Pause"
                       src='/ansys/nexus/novnc/app/images/icons/playf_off.svg'
                       playing='false' />
                <input type="range" id="seek-bar" class="slider" value="0" min="0" max="1000" />
                <label for="seek-bar" id="current-frame" class="frame_label">[1 / 1]</label>
            </div>

            <!-- EnSight toggle controls -->
            <div id="toggle_controls">
                <!-- Toggle jump to end of timestep slider -->
                <div id="ens_timestep_monitor" class="toggle_control_icon">
                    <input type="image" alt="Jump to end of slider"
                           id="noVNC_timestep_monitor"
                           src="/ansys/nexus/novnc/app/images/icons/play_once_mode.svg"
                           data-toggle="true"
                           title="Jump to end of slider" />
                </div>
                <!-- Toggle Overlay hidden lines -->
                <div id="ens_hid_ln_toggle" class="toggle_control_icon">
                    <input type="image" alt="Overlay hidden lines"
                           id="noVNC_hid_ln_button"
                           src="/ansys/nexus/novnc/app/images/icons/ang10_Part_hiddenline_off.svg"
                           data-toggle="false"
                           title="Overlay hidden lines" />
                </div>
                <!-- Toggle Part Highlighting -->
                <div id="ens_part_hl_toggle" class="toggle_control_icon">
                    <input type="image" alt="Part Highlight"
                           src="/ansys/nexus/novnc/app/images/icons/highlight3.svg"
                           data-toggle="false"
                           id="noVNC_hl_button"
                           title="Part Highlight" />
                </div>
                <!-- Fit geometry to viewport -->
                <div id="ens_fit_viewport_btn" class="toggle_control_icon">
                    <input type="image" alt="Fit the geometry to the current viewport"
                           src="/ansys/nexus/novnc/app/images/icons/fit.svg"
                           id="noVNC_fit_viewport_btn"
                           title="Fit geometry to viewport" />
                </div>
                <!-- Reset view of current viewport -->
                <div id="ens_reset_view_btn" class="toggle_control_icon">
                    <input type="image" alt="Reset view"
                           src="/ansys/nexus/novnc/app/images/icons/reset3.svg"
                           id="noVNC_reset_view_btn"
                           title="Reset view of current viewport" />
                </div>
                <!-- Toggle fullscreen -->
                <div id="ens_fullscreen_toggle" class="toggle_control_icon">
                    <input type="image" alt="Fullscreen"
                           src="/ansys/nexus/novnc/app/images/fullscreen.svg"
                           id="noVNC_fullscreen_button"
                           title="Full screen" />
                </div>
            </div>

            <!-- Status Dialog -->
            <div id="noVNC_status" style="display:none;"></div>

            <!-- Transition Screens -->
            <div id="noVNC_transition">
                <div id="noVNC_transition_text"></div>
                <div>
                    <input type="button" id="noVNC_cancel_reconnect_button" value="Cancel" class="noVNC_submit" />
                </div>
                <div class="noVNC_spinner"></div>
            </div>

            <div id="noVNC_container">
                <!-- HTML5 Canvas -->
                <div id="noVNC_screen">
                    <canvas id="noVNC_canvas" width="0" height="0">
                        Canvas not supported.
                    </canvas>
                </div>
            </div>
        </div>
      `;
  }
}



// A list of the created instances
var AnsysNexusViewerInstanceList = [];
// A list of the currently active instances
var AnsysNexusViewerActiveInstanceList = [];
// The real limit varies based on browser implementations. Some browsers limit per-domain (cross-pages)
// and some limit per-tab or per-page.  The maximum is usually 8 or 16.  4 reflects the idea that other
// WebGL-based components might be in use and the fact that we cannot track over tabs/pages.
const AnsysNexusViewerMaxActiveInstances = 4;
// Internal "uid" generation.  Not a true UID, but a sequence of unique strings
var AnsysNexusViewerBaseUID = 0xC6476AE;

// Define the new element <ansys-nexus-viewer>
class AnsysNexusViewer extends HTMLElement {

  // Called at object creation
  constructor() {
    super();
    this._guid = this.generateUID();
    this._renderer = "webgl";  // 'webgl' or 'envnc'
    this._renderer_options = null;  // pass-thru to the renderer
    this._src = null;  // 3D data source URL
    this._src_ext = null; // 3D data source extension (type) used with data URI src values
    this._proxy_img = null;  // proxy image URL
    this._proxy_size = [0, 0]; // The size of the proxy image
    this._observer = null; // resizing observer
    this._perspective = false;  // perspective mode
    this._aspect_ratio = null;  // aspect_ratio override
    this._render_instance = null; // The specific instance for the target renderer
  }

  //  Called when added to the DOM
  connectedCallback() {
    // root of the local instance DOM
    this.appendChild(AnsysNexusViewerTemplate.content.cloneNode(true));
    // register the new instance
    AnsysNexusViewerInstanceList.push(this);
    // parse the element attributes
    const guid = this.getAttribute('guid');
    if (guid !== null) {
      this._guid = guid;
    }
    const renderer = this.getAttribute('renderer');
    if (renderer !== null) {
      this._renderer = renderer;
    }
    const perspective = this.getAttribute('perspective');
    if (perspective !== null) {
      this.perspective = (perspective === 'true');
    }
    // some items can be null
    this._renderer_options = this.getAttribute('renderer_options');
    this.aspect_ratio = this.getAttribute('aspect_ratio');
    this.src_ext = this.getAttribute('src_ext');
    this.src = this.getAttribute('src');
    this.proxy_img = this.getAttribute('proxy_img');
    if (this._renderer === 'webgl') {
      this._render_instance = new GLTFViewerGlue(this);
    } else if (this._renderer === 'envnc') {
      this._render_instance = new EnVNCViewerGlue(this);
    }
    // Don't activate until all fields are set
    let activate = this.getAttribute('active');
    if (activate === null) {
      // If we have a source but no proxy, then activate
      activate = (this.src !== null) && (this._proxy_img === null);
    } else {
      activate = (activate === 'true')
    }
    if (activate) {
      this._indirectActivate(activate);
    } else {
      this._setVisibility(false);
    }
    let proxyElem = this.querySelector('#proxy-img');
    proxyElem.onclick = this._proxyClicked.bind(this);
    proxyElem.onload = this._proxyLoaded.bind(this);
    this._observer = new ResizeObserver(this._directObserverCallback.bind(this));
    this._observer.observe(this.querySelector('#render-div'));
  }

  // Called when removed from the DOM
  disconnectedCallback() {
    this.active = false;
    let idx = AnsysNexusViewerInstanceList.indexOf(item);
    if (idx >= 0) {
      AnsysNexusViewerInstanceList.splice(idx, 1);
    }
  }

  // Instance management
  generateUID() {
    AnsysNexusViewerBaseUID += 1;
    return AnsysNexusViewerBaseUID.toString();
  }

  _freeActiveInstance() {
    // Make sure that there is room for at least one additional active instance
    if (AnsysNexusViewerActiveInstanceList.length >= AnsysNexusViewerMaxActiveInstances) {
      // items at the head are the oldest...
      AnsysNexusViewerActiveInstanceList[0].active = false;
    }
  }

  refreshInstance() {
    // If the user begins to interact with an instance, that instance can
    // be made to look more recent so that it is not reaped in the original
    // activation order
    const idx = AnsysNexusViewerActiveInstanceList.indexOf(this);
    if (idx >= 0) {
      AnsysNexusViewerActiveInstanceList.push(AnsysNexusViewerActiveInstanceList.splice(idx, 1)[0]);
    }
  }

  // Activation GUI handling
  _proxyClicked() {
    this.active = true;
  }

  // Grab the proxy image size (for aspect ratio control)
  _proxyLoaded() {
    let proxyElem = this.querySelector('#proxy-img');
    this._proxy_size = [proxyElem.width, proxyElem.height];
  }

  // Resize handling: enforce aspect ratios, etc
  _indirectObserverCallback() {
    // Three resizing cases:
    // 1) aspect_ratio is null - assume external styles are controlling things
    if (this.aspect_ratio === null) return;
    // 2) aspect_ratio is a number - use it
    let aspectRatio = this.aspect_ratio;
    // 3) aspect_ratio is proxy - use the proxy image aspect ratio: this._proxy_size
    if ((this.aspect_ratio === "proxy") && (this._proxy_size[1] > 0)) {
      aspectRatio = this._proxy_size[0] / this._proxy_size[1];
    }
    // Apply the aspect ratio to the div
    let renderDiv = this.querySelector('#render-div');
    let newHeight = Math.round(renderDiv.clientWidth / aspectRatio);
    let oldHeight = renderDiv.clientHeight;
    if (oldHeight != newHeight) {
      renderDiv.style.height = newHeight + 'px';
      this._render_instance.resizeRenderer(renderDiv.clientWidth, newHeight);
    }
  }

  _directObserverCallback() {
    setTimeout(this._indirectObserverCallback.bind(this), 0);
  }

  // display either the proxy image or the renderer div
  _setVisibility(on) {
    let proxyElem = this.querySelector('#proxy-img');
    let renderDiv = this.querySelector('#render-div');
    if (on) {
      proxyElem.style.display = 'none';
      renderDiv.style.display = 'block';
    } else {
      proxyElem.style.display = 'block';
      renderDiv.style.display = 'none';
    }
  }

  // The various modules may be loaded async
  // If the GLTFViewer module has been loaded, this function returns true
  _dependentModulesLoaded() {
    return (typeof webgl_support === "function");
  }

  // We have been asked to activate via html attribute, we might need to try later...
  _indirectActivate(on) {
    if (this._dependentModulesLoaded()) {
      this.active = on;
    } else {
      setTimeout(this._indirectActivate.bind(this, on), 10);
    }
  }

  // Find the file(type) extension name for the target URI
  urlType(url) {
    if (url === null) return null;
    if (url.toLowerCase().endsWith('avz')) return 'AVZ';
    if (url.toLowerCase().endsWith('scdoc')) return 'SCDOC';
    if (url.toLowerCase().endsWith('evsn')) return 'EVSN';
    return null;
  }

  // Return a data URI for a PNG representation of the current rendered image
  renderImage() {
    if (this.active) {
      return this._render_instance.renderImage();
    }
    return null;
  }

  // properties
  // guid (read only)
  get guid() {
    return this._guid;
  }

  // renderer (read only)
  get renderer() {
    return this._renderer;
  }

  // renderer_options (read only)
  get renderer_options() {
    return this._renderer_options;
  }

  // internal_render_instance()
  get internal_render_instance() {
    if (this.active) {
      return this._render_instance.internalRenderer();
    }
    return null;
  }

  // active
  set active(value) {
    const idx = AnsysNexusViewerActiveInstanceList.indexOf(this);
    if (value) {
      if (idx < 0) {
        // Make sure there is space for this instance to become active
        this._freeActiveInstance();
        // activate
        AnsysNexusViewerActiveInstanceList.push(this);
        this._setVisibility(true)
        // Actually activate the instance
        this._render_instance.setActive(true);
        const event = new CustomEvent('active-changed', {detail: {active: true}});
        this.dispatchEvent(event);
      }
    } else {
      if (idx >= 0) {
        // deactivate
        AnsysNexusViewerActiveInstanceList.splice(idx, 1);
        this._setVisibility(false);
        // Actually deactivate the instance
        this._render_instance.setActive(false);
        const event = new CustomEvent('active-changed', {detail: {active: false}});
        this.dispatchEvent(event);
      }
    }
  }
  get active() {
    return AnsysNexusViewerActiveInstanceList.indexOf(this) >= 0;
  }
  // perspective
  set perspective(value) {
    if (value != this._perspective) {
      this._perspective = value;
      if (this._render_instance !== null) this._render_instance.setPerspective(value);
      const event = new CustomEvent('perspective-changed', {detail: {perspective: this._perspective}});
      this.dispatchEvent(event);
    }
  }
  get perspective() {
    return this._perspective;
  }
  // aspect_ratio ('proxy' or a float)
  set aspect_ratio(value) {
    if (value != this._aspect_ratio) {
      this._aspect_ratio = value;
      const event = new CustomEvent('aspect-ratio-changed', {detail: {aspect_ratio: this._aspect_ratio}});
      this.dispatchEvent(event);
    }
  }
  get aspect_ratio() {
    return this._aspect_ratio;
  }
  // src
  set src(value) {
    if (value != this._src) {
      this._src = value;
      // Update the source extension if the extension has not been set
      if ((value !== null) && (this.src_ext === null)) {
        this.src_ext = this.urlType(value);
      }
      if (this._render_instance !== null) this._render_instance.setSrc(value, this._src_ext);
      const event = new CustomEvent('src-changed', {detail: {src: this._src}});
      this.dispatchEvent(event);
    }
  }
  get src() {
    return this._src;
  }
  // src_ext
  set src_ext(value) {
    if (value != this._src_ext) {
      this._src_ext = value;
    }
  }
  get src_ext() {
    return this._src_ext;
  }
  // proxy_img
  set proxy_img(value) {
    if (value != this._proxy_img) {
      this._proxy_img = value;
      let proxy_elem = this.querySelector('#proxy-img');
      proxy_elem.src = this._proxy_img;
      proxy_elem.style.height = '100%';
      proxy_elem.style.width = '100%';
      const event = new CustomEvent('proxy-img-changed', {detail: {proxy_img: this._proxy_img}});
      this.dispatchEvent(event);
    }
  }
  get proxy_img() {
    return this._proxy_img;
  }
}

// register the web component
if (!window.customElements.get('ansys-nexus-viewer')) {
  window.customElements.define('ansys-nexus-viewer', AnsysNexusViewer);
}

