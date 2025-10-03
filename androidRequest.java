@Override
@SuppressLint(value={"HardwareIds"})
public byte[] executeKeyRequest(UUID object, ExoMediaDrm.KeyRequest object2) {
    String string;
    Object object3;
    block10: {
        block9: {
            i.e("uuid", object);
            i.e("request", object2);
            object3 = ((ExoMediaDrm.KeyRequest)object2).getLicenseServerUrl();
            if (this.forceDefaultLicenseUrl) break block9;
            string = object3;
            if (!TextUtils.isEmpty((CharSequence)object3)) break block10;
        }
        string = this.defaultLicenseUrl;
    }
    if (TextUtils.isEmpty((CharSequence)string)) {
        object = new DataSpec.Builder();
        object2 = Uri.EMPTY;
        throw new MediaDrmCallbackException(((DataSpec.Builder)object).setUri((Uri)object2).build(), (Uri)object2, y0.C, 0L, new IllegalStateException("No license URL"));
    }
    HashMap<String, String> headers = new HashMap<String, String>();
    Object object4 = C.PLAYREADY_UUID;
    object3 = i.a(object4, object) ? "text/xml" : "application/json";
    headers.put("Content-Type", (String)object3);
    if (i.a(object4, object)) {
        headers.put("SOAPAction", "http://schemas.microsoft.com/DRM/2007/03/protocols/AcquireLicense");
    }
    object = this.keyRequestProperties;
    synchronized (object) {
        headers.putAll(this.keyRequestProperties);
    }
    object3 = new m();
    object2 = ((ExoMediaDrm.KeyRequest)object2).getData();
    i.d("request.data", object2);
    object4 = Settings.Secure.getString((ContentResolver)this.context.getContentResolver(), (String)"android_id");
    object = new AppPrefs(this.context);
    object = ((m)object3).g(A.b0(new g("a", object4), new g("b", ((AppPrefs)object).getUniqueIdentifier()), new g("c", ((AppPrefs)object).getInstallationTimestamp())));
    i.d("gson.toJson(\n           \u2026ceIdentifierArr\n        )", object);
    object4 = UtilsKt.toBase64((String)object);
    Object object5 = this.context.getPackageName();
    try {
        object = this.context.getPackageManager().getPackageInfo((String)object5, (int)0).versionName;
    }
    catch (PackageManager.NameNotFoundException nameNotFoundException) {
        object = "unknown.package";
    }
    object2 = new g("c", UtilsKt.base64Encoder((byte[])object2));
    i.d("packageName", object5);
    object5 = new g("a", UtilsKt.toBase64((String)object5));
    i.d("appVersion", object);
    object = ((m)object3).g(A.b0(new g[]{object2, object5, new g("v", UtilsKt.toBase64((String)object)), new g("sv", UtilsKt.toBase64(UtilsKt.toBase64("3.0.63"))), new g("d", UtilsKt.toBase64((String)object4))}));
    i.d("gson.toJson(deviceInformationBaseMap)", object);
    object2 = UtilsKt.toBase64(UtilsKt.toBase64((String)object));
    object = this.otp.substring(0, 32);
    i.d("this as java.lang.String\u2026ing(startIndex, endIndex)", object);
    object4 = this.videoId.substring(0, 16);
    i.d("this as java.lang.String\u2026ing(startIndex, endIndex)", object4);
    object = UtilsKt.toBase64(this.encryptAes256((String)object2, (String)object, (String)object4));
    object = ((m)object3).g(A.b0(new g("v", this.videoId), new g("c", UtilsKt.toBase64((String)object))));
    i.d("gson.toJson(tokenContent)", object);
    object = ((m)object3).g(A.a0(new g("token", UtilsKt.toBase64((String)object))));
    i.d("tokenPayload", object);
    object = ((String)object).getBytes(a.a);
    i.d("this as java.lang.String).getBytes(charset)", object);
    return CustomMediaDrmCallback.Companion.executePost(this.dataSourceFactory, string, (byte[])object, headers);
}