if (shaka.Player.isBrowserSupported()) {
  this._emit("browser_supported");
  const self = this;
  const otp = this.config.otp;
  const host = new URL(self.manifest_uri).hostname;
  const glEngine = this.helper.getGLEngine();
  let platformVersion = await this.helper.getUAChPlatformVersionString();
  const requestFilter = function (type, request) {
    if (type === shaka.net.NetworkingEngine.RequestType.SEGMENT) {
      request.uris = request.uris.map(uri => {
        const url = new URL(uri);
        url.hostname = host;
        return url.href;
      });
    }
    if (type == shaka.net.NetworkingEngine.RequestType.LICENSE) {
      request.headers['x-otp'] = otp;
      request.headers["x-version"] = self.player_version;
      request.headers["ink-ref"] = self._referal_url;
      request.headers['Content-Type'] = "application/json";

      let bodyBase64 = shaka.util.Uint8ArrayUtils.toStandardBase64(new Uint8Array(request.body));
      let vendor = navigator.vendor ? navigator.vendor : null;
      let brands = navigator.userAgentData && navigator.userAgentData.brands ? JSON.stringify(navigator.userAgentData.brands) : null;
      let isChrome = !!window.chrome;
      let timestamp = Math.floor(new Date().getTime() / 1000);
      let ohVal = self.config.oh_val;
      let emeId = self.config.eme_id_val;
      let licenseHash = self.helper.sha256(bodyBase64);

      let licenseObj = {
        'vn': btoa(vendor),
        'ud': btoa(brands),
        'ic': btoa(isChrome),
        'pf': btoa(platformVersion),
        'oh': btoa(ohVal),
        'em': btoa(emeId),
        'dt': btoa(timestamp),
        'ls': btoa(licenseHash)
      };

      let licenseStr = JSON.stringify(licenseObj);
      let licenseEncoded = btoa(btoa(btoa(btoa(licenseStr))));
      let licenseSig = self.helper.sha256(licenseEncoded);

      const hwAccel = self.helper.isHardwareAccelerationEnabled();
      const visitorEnc = btoa(btoa(btoa(btoa(self.visitor_id))));

      let tokenObj = {
        'v': self.config.video_id,
        'c': bodyBase64,
        's': licenseEncoded,
        'h': btoa(btoa(hwAccel)),
        'g': btoa(btoa(glEngine)),
        'i': visitorEnc
      };

      const tokenStr = JSON.stringify(tokenObj);
      const tokenBase64 = btoa(tokenStr);
      const bodyJson = JSON.stringify({ 'token': tokenBase64 });

      request.body = shaka.util.StringUtils.toUTF8(bodyJson);
      request.headers["in-s"] = licenseSig;
    }
  };
}
