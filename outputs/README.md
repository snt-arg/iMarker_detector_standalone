# 📁 Output Directory

This folder stores the generated outputs from the **iMarker Detector Standalone** program. It serves as a centralized location for logging visualizations, debug results, intermediate artifacts, and final detections.

## 🏷️ File Naming Convention

All saved outputs follow a structured naming scheme to help trace back to the specific run configuration:

```
YYYYMMDD_HHMMSS_<variant>.<ext>
```

`<ext>` refers to the file extension, including `png` and `jpg`. Also, `<variant>` shows the sensor-algorithm pair variant used during execution, including:

| Variant       | Description                                |
| ------------- | ------------------------------------------ |
| `sv_offImg`   | Single-vision offline static frame (RGB)   |
| `sv_offImgUV` | Single-vision offline static frame (UV/IR) |
| `sv_offVid`   | Single-vision offline video (RGB)          |
| `sv_usbUv`    | Single-vision USB UV camera setup          |
| `sv_usbIr`    | Single-vision USB IR camera setup          |
| `sv_rs`       | Single-vision RealSense camera setup       |
| `dv_usb`      | Dual-vision USB camera setup               |
| `dv_ids`      | Dual-vision iDS camera setup               |
